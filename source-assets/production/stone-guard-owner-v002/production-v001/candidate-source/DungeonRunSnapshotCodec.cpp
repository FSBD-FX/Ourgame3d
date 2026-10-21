#include "DungeonRunSnapshotCodec.h"
#include "Dom/JsonObject.h"
#include <array>
#include <cmath>
#include <limits>
#include <string>
#include <type_traits>
#include <vector>

namespace DungeonRunSnapshotCodec
{
namespace
{
// Transport/allocation ceilings for this explicitly versioned development
// scope. They are implementation bounds, not a claim about full-game budgets.
constexpr int64 MaxBytes=64ll*1024*1024;
constexpr int32 MaxDepth=128;
constexpr int32 MaxElements=1048576;
constexpr int32 MaxNodes=1048576;
constexpr int32 MaxObjectFields=256;
constexpr uint64 MaxTypedStorage=64ull*1024*1024;
using FNode=TSharedPtr<FJsonValue>;
using FObjectPtr=TSharedPtr<FJsonObject>;

bool Fail(FString& Why,const TCHAR* Message)
{if(Why.IsEmpty())Why=Message;return false;}

bool AppendCodePoint(FString& Text,uint32 C)
{
    if(C>0x10ffff||(C>=0xd800&&C<=0xdfff))return false;
    if constexpr(sizeof(TCHAR)==2)
    {
        if(C>0xffff){C-=0x10000;Text.AppendChar(TCHAR(0xd800+(C>>10)));Text.AppendChar(TCHAR(0xdc00+(C&1023)));}
        else{const TCHAR Unit=TCHAR(C);Text.AppendChars(&Unit,1);}
    }
    else{const TCHAR Unit=TCHAR(C);Text.AppendChars(&Unit,1);}
    return true;
}
bool ReadUtf8(const uint8* B,int32 Count,int32& At,uint32& C)
{
    if(At>=Count)return false;const uint8 Lead=B[At++];
    if(Lead<0x80){C=Lead;return true;}
    int32 Tail=0;uint32 Min=0;
    if(Lead>=0xc2&&Lead<=0xdf){Tail=1;C=Lead&31;Min=0x80;}
    else if(Lead>=0xe0&&Lead<=0xef){Tail=2;C=Lead&15;Min=0x800;}
    else if(Lead>=0xf0&&Lead<=0xf4){Tail=3;C=Lead&7;Min=0x10000;}
    else return false;
    if(Count-At<Tail)return false;
    for(int32 I=0;I<Tail;++I){const uint8 Next=B[At++];if((Next&0xc0)!=0x80)return false;C=(C<<6)|(Next&63);}
    return C>=Min&&C<=0x10ffff&&!(C>=0xd800&&C<=0xdfff);
}
bool NativeUtf8(const std::string& Bytes,FString& Text)
{
    if(Bytes.size()>uint64(MaxBytes))return false;Text.Reset();int32 At=0;
    while(At<int32(Bytes.size())){uint32 C;if(!ReadUtf8(reinterpret_cast<const uint8*>(Bytes.data()),int32(Bytes.size()),At,C)||!AppendCodePoint(Text,C))return false;}
    return true;
}
int32 HexDigit(uint8 C)
{return C>='0'&&C<='9'?C-'0':C>='a'&&C<='f'?C-'a'+10:C>='A'&&C<='F'?C-'A'+10:-1;}

// This parser is separate from the Store and UE's permissive DOM reader. It
// checks original bytes before insertion can erase a duplicate key. Unicode
// escapes, UTF-8 shortest forms and surrogate pairs are decoded explicitly.
class FStrictParser
{
    const TArray<uint8>& Bytes;FString& Why;int32 At=0,Nodes=0;
    bool Take(uint8 C){if(At>=Bytes.Num()||Bytes[At]!=C)return false;++At;return true;}
    bool Hex4(uint32& Code)
    {
        Code=0;if(Bytes.Num()-At<4)return false;
        for(int32 I=0;I<4;++I){const int32 D=HexDigit(Bytes[At++]);if(D<0)return false;Code=(Code<<4)|uint32(D);}return true;
    }
    bool String(FString& Text)
    {
        if(!Take('"'))return Fail(Why,TEXT("Expected a JSON string"));Text.Reset();
        while(At<Bytes.Num())
        {
            if(Text.Len()>MaxElements)return Fail(Why,TEXT("JSON string length limit exceeded"));
            const uint8 C=Bytes[At++];if(C=='"')return true;
            if(C<32)return Fail(Why,TEXT("Unescaped JSON control character"));
            if(C=='\\')
            {
                if(At>=Bytes.Num())return Fail(Why,TEXT("Truncated JSON escape"));const uint8 E=Bytes[At++];
                if(E=='"'||E=='\\'||E=='/')Text.AppendChar(TCHAR(E));
                else if(E=='b')Text.AppendChar(TCHAR(8));else if(E=='f')Text.AppendChar(TCHAR(12));
                else if(E=='n')Text.AppendChar(TCHAR(10));else if(E=='r')Text.AppendChar(TCHAR(13));else if(E=='t')Text.AppendChar(TCHAR(9));
                else if(E=='u')
                {
                    uint32 U;if(!Hex4(U))return Fail(Why,TEXT("Invalid Unicode escape"));
                    if(U>=0xd800&&U<=0xdbff)
                    {
                        uint32 Low;if(!Take('\\')||!Take('u')||!Hex4(Low)||Low<0xdc00||Low>0xdfff)return Fail(Why,TEXT("Unpaired Unicode high surrogate"));
                        U=0x10000+((U-0xd800)<<10)+(Low-0xdc00);
                    }
                    if(!AppendCodePoint(Text,U))return Fail(Why,TEXT("Invalid Unicode scalar"));
                }
                else return Fail(Why,TEXT("Unknown JSON escape"));
            }
            else if(C<0x80)Text.AppendChar(TCHAR(C));
            else
            {
                --At;uint32 U;if(!ReadUtf8(Bytes.GetData(),Bytes.Num(),At,U)||!AppendCodePoint(Text,U))return Fail(Why,TEXT("Invalid UTF-8 scalar"));
            }
        }
        return Fail(Why,TEXT("Unterminated JSON string"));
    }
    bool Value(FNode& Out,int32 Depth)
    {
        if(Depth>MaxDepth||++Nodes>MaxNodes)return Fail(Why,TEXT("JSON depth/node limit exceeded"));
        if(At>=Bytes.Num())return Fail(Why,TEXT("Truncated JSON value"));const uint8 C=Bytes[At];
        if(C=='{')
        {
            ++At;auto Object=MakeShared<FJsonObject>();
            if(Take('}')){Out=MakeShared<FJsonValueObject>(Object);return true;}
            TSet<FString> Keys;
            for(int32 Count=0;;++Count)
            {
                if(Count>=MaxObjectFields)return Fail(Why,TEXT("JSON object field limit exceeded"));
                FString Key;if(!String(Key))return false;
                // All field names in this wire schema are ASCII identifiers.
                // Disallow NUL/control/non-ASCII keys before native lookup.
                if(Key.IsEmpty()||Key.Len()>MaxObjectFields)return Fail(Why,TEXT("Invalid JSON field-name width"));
                for(int32 I=0;I<Key.Len();++I)if(!((Key[I]>='A'&&Key[I]<='Z')||(Key[I]>='a'&&Key[I]<='z')||(Key[I]>='0'&&Key[I]<='9')||Key[I]=='_'))return Fail(Why,TEXT("Unsupported JSON field name"));
                // UE's DOM/hash lookup is case insensitive. Neither a duplicate
                // nor a case-colliding unknown key may erase an original value.
                // Required schema lookup below additionally matches exact case.
                if(Keys.Contains(Key))return Fail(Why,TEXT("Duplicate or case-colliding decoded JSON field"));Keys.Add(Key);
                if(!Take(':'))return Fail(Why,TEXT("Missing JSON field separator"));FNode Child;if(!Value(Child,Depth+1))return false;Object->SetField(Key,Child);
                if(Take('}'))break;if(!Take(','))return Fail(Why,TEXT("Missing JSON object separator"));
            }
            Out=MakeShared<FJsonValueObject>(Object);return true;
        }
        if(C=='[')
        {
            ++At;TArray<FNode> Values;
            if(Take(']')){Out=MakeShared<FJsonValueArray>(Values);return true;}
            for(;;)
            {
                if(Values.Num()>=MaxElements)return Fail(Why,TEXT("JSON array element limit exceeded"));
                FNode Child;if(!Value(Child,Depth+1))return false;Values.Add(MoveTemp(Child));
                if(Take(']'))break;if(!Take(','))return Fail(Why,TEXT("Missing JSON array separator"));
            }
            Out=MakeShared<FJsonValueArray>(MoveTemp(Values));return true;
        }
        if(C=='"'){FString S;if(!String(S))return false;Out=MakeShared<FJsonValueString>(MoveTemp(S));return true;}
        const auto Literal=[&](const ANSICHAR* Text,int32 Count)
        {if(Bytes.Num()-At<Count||FMemory::Memcmp(Bytes.GetData()+At,Text,Count)!=0)return false;At+=Count;return true;};
        if(Literal("true",4)){Out=MakeShared<FJsonValueBoolean>(true);return true;}
        if(Literal("false",5)){Out=MakeShared<FJsonValueBoolean>(false);return true;}
        if(Literal("null",4)){Out=MakeShared<FJsonValueNull>();return true;}
        return Fail(Why,TEXT("Unsupported token: this schema has no JSON numeric values or whitespace"));
    }
public:
    FStrictParser(const TArray<uint8>& In,FString& Diagnostic):Bytes(In),Why(Diagnostic){}
    bool Parse(FNode& Out)
    {
        if(Bytes.IsEmpty()||Bytes.Num()>MaxBytes||Bytes[0]!='{'||Bytes.Last()!='}')return Fail(Why,TEXT("Expected a bounded canonical UTF-8 JSON object without BOM/trailing data"));
        if(!Value(Out,0))return false;
        return At==Bytes.Num()||Fail(Why,TEXT("Trailing or malformed JSON data"));
    }
};

// A bounded byte writer avoids replacement-character conversion and retains
// embedded NUL by iterating native string lengths explicitly.
class FCanonicalWriter
{
    TArray<uint8> Bytes;FString& Why;bool Good=true;int32 Nodes=0;
    bool Byte(uint8 C)
    {if(!Good)return false;if(Bytes.Num()>=MaxBytes){Good=false;return Fail(Why,TEXT("Canonical payload byte limit exceeded"));}Bytes.Add(C);return true;}
    bool Ascii(const ANSICHAR* S){for(int32 I=0;S[I];++I)if(!Byte(uint8(S[I])))return false;return true;}
    bool Utf8(uint32 C)
    {
        if(C<0x80)return Byte(uint8(C));if(C<0x800)return Byte(uint8(0xc0|(C>>6)))&&Byte(uint8(0x80|(C&63)));
        if(C<0x10000)return Byte(uint8(0xe0|(C>>12)))&&Byte(uint8(0x80|((C>>6)&63)))&&Byte(uint8(0x80|(C&63)));
        return Byte(uint8(0xf0|(C>>18)))&&Byte(uint8(0x80|((C>>12)&63)))&&Byte(uint8(0x80|((C>>6)&63)))&&Byte(uint8(0x80|(C&63)));
    }
    bool String(const FString& Text)
    {
        if(!Byte('"'))return false;constexpr ANSICHAR Hex[]="0123456789abcdef";
        for(int32 I=0;I<Text.Len();++I)
        {
            uint32 C=uint32(Text[I]);
            if(C=='"'||C=='\\'){if(!Byte('\\')||!Byte(uint8(C)))return false;}
            else if(C<32){if(!Ascii("\\u00")||!Byte(Hex[C>>4])||!Byte(Hex[C&15]))return false;}
            else
            {
                if constexpr(sizeof(TCHAR)==2)
                {
                    if(C>=0xd800&&C<=0xdbff)
                    {
                        if(++I>=Text.Len())return Fail(Why,TEXT("Unpaired native high surrogate"));const uint32 Low=uint32(Text[I]);
                        if(Low<0xdc00||Low>0xdfff)return Fail(Why,TEXT("Unpaired native high surrogate"));C=0x10000+((C-0xd800)<<10)+(Low-0xdc00);
                    }
                    else if(C>=0xdc00&&C<=0xdfff)return Fail(Why,TEXT("Unpaired native low surrogate"));
                }
                if(C>0x10ffff||(C>=0xd800&&C<=0xdfff))return Fail(Why,TEXT("Invalid native Unicode scalar"));
                if(!Utf8(C))return false;
            }
        }
        return Byte('"');
    }
    bool Value(const FNode& Node,int32 Depth)
    {
        if(!Node.IsValid()||Depth>MaxDepth||++Nodes>MaxNodes)return Fail(Why,TEXT("Canonical node/depth limit exceeded"));
        if(Node->Type==EJson::String)return String(Node->AsString());
        if(Node->Type==EJson::Boolean)return Ascii(Node->AsBool()?"true":"false");
        if(Node->Type==EJson::Null)return Ascii("null");
        if(Node->Type==EJson::Array)
        {
            const auto& Array=Node->AsArray();if(Array.Num()>MaxElements||!Byte('['))return Fail(Why,TEXT("Canonical array limit exceeded"));bool First=true;
            for(const auto& Child:Array){if(!First&&!Byte(','))return false;First=false;if(!Value(Child,Depth+1))return false;}return Byte(']');
        }
        if(Node->Type==EJson::Object)
        {
            const auto Object=Node->AsObject();if(!Object.IsValid()||Object->Values.Num()>MaxObjectFields||!Byte('{'))return Fail(Why,TEXT("Canonical object field limit exceeded"));
            TArray<FString> Keys;Object->Values.GetKeys(Keys);Keys.Sort([](const FString& A,const FString& B){return A.Compare(B,ESearchCase::CaseSensitive)<0;});bool First=true;
            for(const auto& Key:Keys){if(!First&&!Byte(','))return false;First=false;if(!String(Key)||!Byte(':')||!Value(Object->Values[Key],Depth+1))return false;}return Byte('}');
        }
        return Fail(Why,TEXT("Unsupported canonical JSON value type"));
    }
public:
    explicit FCanonicalWriter(FString& Diagnostic):Why(Diagnostic){}
    bool Write(const FNode& Node,TArray<uint8>& Out)
    {if(!Value(Node,0)||!Good)return false;Out=MoveTemp(Bytes);return true;}
};

struct FArchive
{
    bool Reading=false,Good=true;FString& Why;uint64 Storage=0;int32 Nodes=0;uint8 CodecVersion=1;
    explicit FArchive(bool Read,FString& Diagnostic):Reading(Read),Why(Diagnostic){}
    void Reject(const TCHAR* Message){Good=false;Fail(Why,Message);}
    bool Allocate(uint64 Count,uint64 Size)
    {
        if(Count>uint64(MaxElements)||(Size!=0&&Count>(MaxTypedStorage-Storage)/Size)){Reject(TEXT("Typed container/allocation limit exceeded"));return false;}
        Storage+=Count*Size;return true;
    }
    bool Node(){if(++Nodes>MaxNodes){Reject(TEXT("Typed value node limit exceeded"));return false;}return Good;}
};
template<class T>bool Transfer(FArchive&,FNode&,T&);
class FObject
{
    FArchive& Archive;FObjectPtr Object;int32 Used=0;
public:
    FObject(FArchive& A,FNode& Node):Archive(A)
    {
        if(!A.Good)return;
        if(A.Reading){if(!Node.IsValid()||Node->Type!=EJson::Object){A.Reject(TEXT("Expected a complete named-field object"));return;}Object=Node->AsObject();}
        else{Object=MakeShared<FJsonObject>();Node=MakeShared<FJsonValueObject>(Object);}
    }
    bool Reading()const{return Archive.Reading;}
    uint8 CodecVersion()const{return Archive.CodecVersion;}
    void Reject(const TCHAR* Why){Archive.Reject(Why);}
    bool Good()const{return Archive.Good;}
    template<class T>void Field(const TCHAR* Name,T& Value)
    {
        if(!Archive.Good)return;++Used;FNode Node;
        if(Archive.Reading)
        {
            bool Found=false;
            for(const auto& Entry:Object->Values)if(Entry.Key.Equals(Name,ESearchCase::CaseSensitive))
            {Node=Entry.Value;Found=true;break;}
            if(!Found||!Node.IsValid()){Archive.Reject(TEXT("Missing mandatory exact-case named field"));return;}
        }
        if(!Transfer(Archive,Node,Value))return;
        if(!Archive.Reading)Object->SetField(Name,MoveTemp(Node));
    }
    bool Finish()
    {if(Archive.Good&&(!Object.IsValid()||Object->Values.Num()!=Used))Archive.Reject(TEXT("Unknown or repeated schema field"));return Archive.Good;}
};

// Every finite enum domain that appears in the schema is explicit. Unknown
// future enumerators require a deliberate wire/schema/owner extension.
template<class T>bool EnumWithin(T V,T Last)
{
    using U=std::underlying_type_t<T>;const U Number=static_cast<U>(V);
    if constexpr(std::is_signed_v<U>){if(Number<0)return false;}
    return Number<=static_cast<U>(Last);
}
#define ENUM_DOMAIN(T,Last) bool KnownEnum(T V){return EnumWithin(V,T::Last);}
ENUM_DOMAIN(EDungeonRunScope,BoundDevelopmentV2)
ENUM_DOMAIN(EDungeonRunGeometryKind,SceneExplorationV1)
ENUM_DOMAIN(EDungeonFighterOwnerKind,StoneGuard)
ENUM_DOMAIN(EDungeonEquipmentRunConfig,FirstBatch)
ENUM_DOMAIN(EDungeonEquipmentActionKind,SwitchWeapon)
ENUM_DOMAIN(EDungeonEquipmentFailure,InternalConsistency)
ENUM_DOMAIN(DungeonContentCombat::EWeapon,STF001)
ENUM_DOMAIN(DungeonContentCombat::EShape,GroundRectangle)
ENUM_DOMAIN(DungeonContentCombat::EPhase,Recovery)
ENUM_DOMAIN(DungeonContentCombat::EEventKind,Interrupted)
ENUM_DOMAIN(DungeonWeaponActions::EAction,Reload)
ENUM_DOMAIN(DungeonWeaponActions::EEvent,ReloadCancelled)
ENUM_DOMAIN(DungeonWeaponActions::EOriginPolicy,GroundProjection)
ENUM_DOMAIN(DungeonWeaponActions::ERegistrationKind,ResolvedImport)
ENUM_DOMAIN(DungeonWeaponActions::EFocusChange,ExternalRestore)
ENUM_DOMAIN(DungeonWeaponActions::EWeaponMutation,ReloadCompleted)
ENUM_DOMAIN(DungeonDodge::EPhase,Dead)
ENUM_DOMAIN(DungeonDodge::EBlock,Body)
ENUM_DOMAIN(DungeonDodge::EFinish,Death)
ENUM_DOMAIN(DungeonStoneKnight::EPhase,Dead)
ENUM_DOMAIN(DungeonStoneKnight::EAttack,Shield)
ENUM_DOMAIN(DungeonStoneKnight::EStop,ValidHit)
ENUM_DOMAIN(DungeonStoneBat::EPhase,Dead)
ENUM_DOMAIN(DungeonStoneBat::EAttack,Wing)
ENUM_DOMAIN(DungeonStoneBat::EEventKind,DescentDue)
ENUM_DOMAIN(DungeonStoneGuard::EPhase,Dead)
ENUM_DOMAIN(DungeonStoneGuard::EAttack,Stomp)
ENUM_DOMAIN(DungeonStoneGuard::EEventKind,RewardClaimed)
ENUM_DOMAIN(DungeonWeaponPoseSocket::EClip,Reload)
ENUM_DOMAIN(DungeonEquipmentStats::EPackage,Cursed)
ENUM_DOMAIN(DungeonEquipmentStats::EError,NotImplemented)
ENUM_DOMAIN(DungeonEquipmentInventory::EAction,Drop)
ENUM_DOMAIN(DungeonEquipmentInventory::EError,NotOwnedWeapon)
ENUM_DOMAIN(EDungeonWorldProjectileStop,BlockedBody)
ENUM_DOMAIN(EDungeonWorldWeaponEventKind,BurnExpired)
ENUM_DOMAIN(EDungeonSceneObjectKind,Exit)
ENUM_DOMAIN(EDungeonSceneInteractionKind,Exit)
ENUM_DOMAIN(EDungeonSceneFailure,InvalidRequest)
ENUM_DOMAIN(EDungeonRunRewardKind,Axe)
ENUM_DOMAIN(EDungeonRunRewardSourceKind,RoomClearAxe)
#undef ENUM_DOMAIN

// The following production field declarations are an exhaustive traversal of
// the real snapshot/owner headers. They are not a test-oracle or byte fixture.
void Fields(FObject& O,FGuid& S)
{
    O.Field(TEXT("A"),S.A);O.Field(TEXT("B"),S.B);O.Field(TEXT("C"),S.C);O.Field(TEXT("D"),S.D);
}
void Fields(FObject& O,FVector2D& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);
}
void Fields(FObject& O,FVector& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);O.Field(TEXT("Z"),S.Z);
}
void Fields(FObject& O,FQuat& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);O.Field(TEXT("Z"),S.Z);O.Field(TEXT("W"),S.W);
}
void Fields(FObject& O,FBox2D& S)
{
    O.Field(TEXT("Min"),S.Min);O.Field(TEXT("Max"),S.Max);O.Field(TEXT("bIsValid"),S.bIsValid);
}
void Fields(FObject& O,DungeonContentCombat::FActionState& S)
{
    O.Field(TEXT("Active"),S.Active);O.Field(TEXT("Locked"),S.Locked);O.Field(TEXT("StartedAirborne"),S.StartedAirborne);O.Field(TEXT("WindowIssued"),S.WindowIssued);
    O.Field(TEXT("Phase"),S.Phase);O.Field(TEXT("Weapon"),S.Weapon);O.Field(TEXT("WeaponInstanceId"),S.WeaponInstanceId);O.Field(TEXT("AttackId"),S.AttackId);
    O.Field(TEXT("Stage"),S.Stage);O.Field(TEXT("Facing"),S.Facing);O.Field(TEXT("Start"),S.Start);O.Field(TEXT("LockTime"),S.LockTime);
    O.Field(TEXT("ActiveStart"),S.ActiveStart);O.Field(TEXT("ActiveEnd"),S.ActiveEnd);O.Field(TEXT("End"),S.End);O.Field(TEXT("Damage"),S.Damage);
    O.Field(TEXT("Stagger"),S.Stagger);O.Field(TEXT("MinRange"),S.MinRange);O.Field(TEXT("Range"),S.Range);O.Field(TEXT("Depth"),S.Depth);
    O.Field(TEXT("MoveMultiplier"),S.MoveMultiplier);O.Field(TEXT("ActionSpeedPct"),S.ActionSpeedPct);O.Field(TEXT("Shape"),S.Shape);O.Field(TEXT("Critical"),S.Critical);
    O.Field(TEXT("CritMultiplier"),S.CritMultiplier);
}
void Fields(FObject& O,DungeonContentCombat::FCombatEvent& S)
{
    O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("Stage"),S.Stage);O.Field(TEXT("SubhitId"),S.SubhitId);
    O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("WindowEnd"),S.WindowEnd);O.Field(TEXT("Action"),S.Action);
}
void Fields(FObject& O,DungeonContentCombat::FWindowReceipt& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("SubhitId"),S.SubhitId);O.Field(TEXT("Start"),S.Start);
    O.Field(TEXT("End"),S.End);O.Field(TEXT("FrozenAction"),S.FrozenAction);
}
void Fields(FObject& O,DungeonContentCombat::FHitReceipt& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("TargetId"),S.TargetId);O.Field(TEXT("SubhitId"),S.SubhitId);
}
void Fields(FObject& O,DungeonContentCombat::FCombatState& S)
{
    O.Field(TEXT("Version"),S.Version);O.Field(TEXT("Weapon"),S.Weapon);O.Field(TEXT("WeaponInstanceId"),S.WeaponInstanceId);O.Field(TEXT("NextAttackId"),S.NextAttackId);
    O.Field(TEXT("NextEventId"),S.NextEventId);O.Field(TEXT("Time"),S.Time);O.Field(TEXT("ComboExpiry"),S.ComboExpiry);O.Field(TEXT("NextComboStage"),S.NextComboStage);
    O.Field(TEXT("ComboReady"),S.ComboReady);O.Field(TEXT("PendingPrimary"),S.PendingPrimary);O.Field(TEXT("Grounded"),S.Grounded);O.Field(TEXT("AirPrimarySpent"),S.AirPrimarySpent);
    O.Field(TEXT("Dead"),S.Dead);O.Field(TEXT("Action"),S.Action);O.Field(TEXT("IssuedWindows"),S.IssuedWindows);O.Field(TEXT("HitReceipts"),S.HitReceipts);
    O.Field(TEXT("PendingEvents"),S.PendingEvents);
}
void Fields(FObject& O,DungeonWeaponActions::FOrigin& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);O.Field(TEXT("Height"),S.Height);
}
void Fields(FObject& O,DungeonWeaponActions::FInstance& S)
{
    O.Field(TEXT("Weapon"),S.Weapon);O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("Ammo"),S.Ammo);O.Field(TEXT("ReservedAmmo"),S.ReservedAmmo);
    O.Field(TEXT("CooldownDeadline"),S.CooldownDeadline);
}
void Fields(FObject& O,DungeonWeaponActions::FRegistration& S)
{
    O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("Initial"),S.Initial);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("ReceiptId"),S.ReceiptId);
    O.Field(TEXT("ActionCursor"),S.ActionCursor);O.Field(TEXT("EventCursor"),S.EventCursor);
}
void Fields(FObject& O,DungeonWeaponActions::FBudget& S)
{
    O.Field(TEXT("Focus"),S.Focus);O.Field(TEXT("ReservedFocus"),S.ReservedFocus);O.Field(TEXT("LastActualSpend"),S.LastActualSpend);O.Field(TEXT("HasActualSpend"),S.HasActualSpend);
    O.Field(TEXT("Grounded"),S.Grounded);O.Field(TEXT("AirPrimarySpent"),S.AirPrimarySpent);O.Field(TEXT("Dead"),S.Dead);
}
void Fields(FObject& O,DungeonWeaponActions::FAction& S)
{
    O.Field(TEXT("Type"),S.Type);O.Field(TEXT("Phase"),S.Phase);O.Field(TEXT("Weapon"),S.Weapon);O.Field(TEXT("InstanceId"),S.InstanceId);
    O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("Active"),S.Active);O.Field(TEXT("Locked"),S.Locked);O.Field(TEXT("StartedAirborne"),S.StartedAirborne);
    O.Field(TEXT("ForwardStepIssued"),S.ForwardStepIssued);O.Field(TEXT("NextSubhit"),S.NextSubhit);O.Field(TEXT("Facing"),S.Facing);O.Field(TEXT("Start"),S.Start);
    O.Field(TEXT("LockAt"),S.LockAt);O.Field(TEXT("ActiveAt"),S.ActiveAt);O.Field(TEXT("ActiveEnd"),S.ActiveEnd);O.Field(TEXT("End"),S.End);
    O.Field(TEXT("SpeedPct"),S.SpeedPct);O.Field(TEXT("DamagePct"),S.DamagePct);O.Field(TEXT("StaggerPct"),S.StaggerPct);O.Field(TEXT("ReachPct"),S.ReachPct);
    O.Field(TEXT("CritMultiplier"),S.CritMultiplier);O.Field(TEXT("AmmoCost"),S.AmmoCost);O.Field(TEXT("FocusCost"),S.FocusCost);O.Field(TEXT("CooldownDuration"),S.CooldownDuration);
    O.Field(TEXT("ReloadSpeedPct"),S.ReloadSpeedPct);O.Field(TEXT("FocusCostPct"),S.FocusCostPct);O.Field(TEXT("SkillCooldownPct"),S.SkillCooldownPct);O.Field(TEXT("Critical"),S.Critical);
    O.Field(TEXT("Terminal"),S.Terminal);
}
void Fields(FObject& O,DungeonWeaponActions::FEvent& S)
{
    O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("SubhitId"),S.SubhitId);
    O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("WindowEnd"),S.WindowEnd);O.Field(TEXT("Damage"),S.Damage);
    O.Field(TEXT("Stagger"),S.Stagger);O.Field(TEXT("MinRange"),S.MinRange);O.Field(TEXT("Range"),S.Range);O.Field(TEXT("Depth"),S.Depth);
    O.Field(TEXT("ProjectileSpeed"),S.ProjectileSpeed);O.Field(TEXT("SecondTargetRatio"),S.SecondTargetRatio);O.Field(TEXT("BurnDps"),S.BurnDps);O.Field(TEXT("BurnDuration"),S.BurnDuration);
    O.Field(TEXT("ForwardStep"),S.ForwardStep);O.Field(TEXT("AmmoConsumed"),S.AmmoConsumed);O.Field(TEXT("FocusConsumed"),S.FocusConsumed);O.Field(TEXT("MaxTargets"),S.MaxTargets);
    O.Field(TEXT("Shape"),S.Shape);O.Field(TEXT("OriginPolicy"),S.OriginPolicy);O.Field(TEXT("Origin"),S.Origin);O.Field(TEXT("Action"),S.Action);
}
void Fields(FObject& O,DungeonWeaponActions::FFocusReceipt& S)
{
    O.Field(TEXT("MutationId"),S.MutationId);O.Field(TEXT("ReceiptId"),S.ReceiptId);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("AtTime"),S.AtTime);
    O.Field(TEXT("Requested"),S.Requested);O.Field(TEXT("Applied"),S.Applied);O.Field(TEXT("Before"),S.Before);O.Field(TEXT("After"),S.After);
    O.Field(TEXT("ReservedBefore"),S.ReservedBefore);O.Field(TEXT("RegeneratedBefore"),S.RegeneratedBefore);
}
void Fields(FObject& O,DungeonWeaponActions::FWeaponRuntimeReceipt& S)
{
    O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("BeforeAmmo"),S.BeforeAmmo);
    O.Field(TEXT("AfterAmmo"),S.AfterAmmo);O.Field(TEXT("BeforeCooldown"),S.BeforeCooldown);O.Field(TEXT("AfterCooldown"),S.AfterCooldown);O.Field(TEXT("SubhitId"),S.SubhitId);
    O.Field(TEXT("Action"),S.Action);
}
void Fields(FObject& O,DungeonWeaponActions::FState& S)
{
    O.Field(TEXT("Version"),S.Version);O.Field(TEXT("Time"),S.Time);O.Field(TEXT("LastReloadCancelTime"),S.LastReloadCancelTime);O.Field(TEXT("EquippedId"),S.EquippedId);
    O.Field(TEXT("NextActionId"),S.NextActionId);O.Field(TEXT("NextEventId"),S.NextEventId);O.Field(TEXT("AutoReloadPendingId"),S.AutoReloadPendingId);O.Field(TEXT("Budget"),S.Budget);
    O.Field(TEXT("Action"),S.Action);O.Field(TEXT("Instances"),S.Instances);O.Field(TEXT("PendingEvents"),S.PendingEvents);O.Field(TEXT("Issued"),S.Issued);
    O.Field(TEXT("InitialFocus"),S.InitialFocus);O.Field(TEXT("AccruedFocus"),S.AccruedFocus);O.Field(TEXT("NextFocusMutationId"),S.NextFocusMutationId);O.Field(TEXT("FocusHistory"),S.FocusHistory);
    O.Field(TEXT("Registrations"),S.Registrations);O.Field(TEXT("NextImportReceiptId"),S.NextImportReceiptId);O.Field(TEXT("WeaponRuntimeHistory"),S.WeaponRuntimeHistory);
}
void Fields(FObject& O,DungeonDodge::FPoint& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);
}
void Fields(FObject& O,DungeonDodge::FPositionReceipt& S)
{
    O.Field(TEXT("Id"),S.Id);O.Field(TEXT("AfterActionId"),S.AfterActionId);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("Position"),S.Position);
}
void Fields(FObject& O,DungeonDodge::FRecord& S)
{
    O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("StartEventId"),S.StartEventId);O.Field(TEXT("BlockEventId"),S.BlockEventId);O.Field(TEXT("FinishEventId"),S.FinishEventId);
    O.Field(TEXT("Origin"),S.Origin);O.Field(TEXT("Direction"),S.Direction);O.Field(TEXT("Start"),S.Start);O.Field(TEXT("End"),S.End);
    O.Field(TEXT("ReadyAt"),S.ReadyAt);O.Field(TEXT("Travelled"),S.Travelled);O.Field(TEXT("BlockedAt"),S.BlockedAt);O.Field(TEXT("FinishedAt"),S.FinishedAt);
    O.Field(TEXT("Block"),S.Block);O.Field(TEXT("Finish"),S.Finish);O.Field(TEXT("OriginReceipt"),S.OriginReceipt);
}
void Fields(FObject& O,DungeonDodge::FState& S)
{
    O.Field(TEXT("Version"),S.Version);O.Field(TEXT("OwnerId"),S.OwnerId);O.Field(TEXT("NextActionId"),S.NextActionId);O.Field(TEXT("NextEventId"),S.NextEventId);
    O.Field(TEXT("DeathEventId"),S.DeathEventId);O.Field(TEXT("NextPositionReceiptId"),S.NextPositionReceiptId);O.Field(TEXT("InitialTime"),S.InitialTime);O.Field(TEXT("Time"),S.Time);
    O.Field(TEXT("ReadyAt"),S.ReadyAt);O.Field(TEXT("DeadAt"),S.DeadAt);O.Field(TEXT("InitialPosition"),S.InitialPosition);O.Field(TEXT("Position"),S.Position);
    O.Field(TEXT("Phase"),S.Phase);O.Field(TEXT("Records"),S.Records);O.Field(TEXT("LastPositionReceipt"),S.LastPositionReceipt);
}
void Fields(FObject& O,DungeonStoneKnight::FPoint& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);
}
void Fields(FObject& O,DungeonStoneKnight::FAction& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("InProgress"),S.InProgress);O.Field(TEXT("Locked"),S.Locked);
    O.Field(TEXT("ActiveIssued"),S.ActiveIssued);O.Field(TEXT("Start"),S.Start);O.Field(TEXT("LockAt"),S.LockAt);O.Field(TEXT("ActiveAt"),S.ActiveAt);
    O.Field(TEXT("PlannedActiveEnd"),S.PlannedActiveEnd);O.Field(TEXT("ActiveEnd"),S.ActiveEnd);O.Field(TEXT("RecoveryEnd"),S.RecoveryEnd);O.Field(TEXT("Damage"),S.Damage);
    O.Field(TEXT("Stagger"),S.Stagger);O.Field(TEXT("Origin"),S.Origin);O.Field(TEXT("Target"),S.Target);O.Field(TEXT("Direction"),S.Direction);
    O.Field(TEXT("Stop"),S.Stop);
}
void Fields(FObject& O,DungeonStoneKnight::FActiveReceipt& S)
{
    O.Field(TEXT("FrozenAction"),S.FrozenAction);O.Field(TEXT("End"),S.End);O.Field(TEXT("EventId"),S.EventId);
}
void Fields(FObject& O,DungeonStoneKnight::FHitReceipt& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("TargetId"),S.TargetId);
}
void Fields(FObject& O,DungeonStoneKnight::FState& S)
{
    O.Field(TEXT("Version"),S.Version);O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("NextAttackId"),S.NextAttackId);O.Field(TEXT("NextEventId"),S.NextEventId);
    O.Field(TEXT("Time"),S.Time);O.Field(TEXT("HP"),S.HP);O.Field(TEXT("PoiseAccum"),S.PoiseAccum);O.Field(TEXT("LastPoiseAt"),S.LastPoiseAt);
    O.Field(TEXT("ProtectionUntil"),S.ProtectionUntil);O.Field(TEXT("StunUntil"),S.StunUntil);O.Field(TEXT("CombatStartedAt"),S.CombatStartedAt);O.Field(TEXT("WakeStartedAt"),S.WakeStartedAt);
    O.Field(TEXT("WakeEnd"),S.WakeEnd);O.Field(TEXT("ChargeReadyAt"),S.ChargeReadyAt);O.Field(TEXT("ShieldReadyAt"),S.ShieldReadyAt);O.Field(TEXT("WakeQueued"),S.WakeQueued);
    O.Field(TEXT("Awakened"),S.Awakened);O.Field(TEXT("RewardClaimed"),S.RewardClaimed);O.Field(TEXT("Phase"),S.Phase);O.Field(TEXT("Position"),S.Position);
    O.Field(TEXT("Action"),S.Action);O.Field(TEXT("ActiveReceipts"),S.ActiveReceipts);O.Field(TEXT("HitReceipts"),S.HitReceipts);
}
void Fields(FObject& O,DungeonStoneBat::FPoint& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);O.Field(TEXT("Z"),S.Z);
}
void Fields(FObject& O,DungeonStoneBat::FAction& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("StartEventId"),S.StartEventId);O.Field(TEXT("LockEventId"),S.LockEventId);O.Field(TEXT("WindowEventId"),S.WindowEventId);
    O.Field(TEXT("FinishEventId"),S.FinishEventId);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("InProgress"),S.InProgress);O.Field(TEXT("Locked"),S.Locked);
    O.Field(TEXT("Emitted"),S.Emitted);O.Field(TEXT("Interrupted"),S.Interrupted);O.Field(TEXT("Missed"),S.Missed);O.Field(TEXT("PathBlocked"),S.PathBlocked);
    O.Field(TEXT("EndpointFound"),S.EndpointFound);O.Field(TEXT("Start"),S.Start);O.Field(TEXT("LockAt"),S.LockAt);O.Field(TEXT("ActiveAt"),S.ActiveAt);
    O.Field(TEXT("ActiveEnd"),S.ActiveEnd);O.Field(TEXT("NominalEnd"),S.NominalEnd);O.Field(TEXT("CooldownDeadline"),S.CooldownDeadline);O.Field(TEXT("InterruptedAt"),S.InterruptedAt);
    O.Field(TEXT("CompletedAt"),S.CompletedAt);O.Field(TEXT("Damage"),S.Damage);O.Field(TEXT("Stagger"),S.Stagger);O.Field(TEXT("RadiusX"),S.RadiusX);
    O.Field(TEXT("RadiusY"),S.RadiusY);O.Field(TEXT("HorizontalBudget"),S.HorizontalBudget);O.Field(TEXT("HorizontalSpeed"),S.HorizontalSpeed);O.Field(TEXT("Origin"),S.Origin);
    O.Field(TEXT("LockedTarget"),S.LockedTarget);O.Field(TEXT("Endpoint"),S.Endpoint);
}
void Fields(FObject& O,DungeonStoneBat::FEvent& S)
{
    O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("TargetId"),S.TargetId);O.Field(TEXT("Kind"),S.Kind);
    O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("EndTime"),S.EndTime);O.Field(TEXT("Amount"),S.Amount);O.Field(TEXT("From"),S.From);
    O.Field(TEXT("To"),S.To);O.Field(TEXT("Action"),S.Action);
}
void Fields(FObject& O,DungeonStoneBat::FIncomingHit& S)
{
    O.Field(TEXT("ReceiptId"),S.ReceiptId);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("HPLoss"),S.HPLoss);O.Field(TEXT("Stagger"),S.Stagger);
}
void Fields(FObject& O,DungeonStoneBat::FHitReceipt& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("TargetId"),S.TargetId);O.Field(TEXT("AtTime"),S.AtTime);
}
void Fields(FObject& O,DungeonStoneBat::FState& S)
{
    O.Field(TEXT("Version"),S.Version);O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("NextAttackId"),S.NextAttackId);O.Field(TEXT("NextEventId"),S.NextEventId);
    O.Field(TEXT("LastDamageReceiptId"),S.LastDamageReceiptId);O.Field(TEXT("InitialTime"),S.InitialTime);O.Field(TEXT("Time"),S.Time);O.Field(TEXT("HP"),S.HP);
    O.Field(TEXT("PoiseAccum"),S.PoiseAccum);O.Field(TEXT("PoiseDecayOrigin"),S.PoiseDecayOrigin);O.Field(TEXT("LastPoiseAt"),S.LastPoiseAt);O.Field(TEXT("ProtectionUntil"),S.ProtectionUntil);
    O.Field(TEXT("StunUntil"),S.StunUntil);O.Field(TEXT("CombatStartedAt"),S.CombatStartedAt);O.Field(TEXT("WakeStartedAt"),S.WakeStartedAt);O.Field(TEXT("WakeEnd"),S.WakeEnd);
    O.Field(TEXT("PeckReadyAt"),S.PeckReadyAt);O.Field(TEXT("WingReadyAt"),S.WingReadyAt);O.Field(TEXT("LowStartedAt"),S.LowStartedAt);O.Field(TEXT("LowReadyAt"),S.LowReadyAt);
    O.Field(TEXT("RiseStartedAt"),S.RiseStartedAt);O.Field(TEXT("HighIdleEligibleSince"),S.HighIdleEligibleSince);O.Field(TEXT("WakeQueued"),S.WakeQueued);O.Field(TEXT("Awakened"),S.Awakened);
    O.Field(TEXT("PendingLow"),S.PendingLow);O.Field(TEXT("RewardClaimed"),S.RewardClaimed);O.Field(TEXT("LowLegal"),S.LowLegal);O.Field(TEXT("Phase"),S.Phase);
    O.Field(TEXT("ResumePhase"),S.ResumePhase);O.Field(TEXT("InitialPosition"),S.InitialPosition);O.Field(TEXT("Position"),S.Position);O.Field(TEXT("RiseOrigin"),S.RiseOrigin);
    O.Field(TEXT("Action"),S.Action);O.Field(TEXT("Actions"),S.Actions);O.Field(TEXT("ReceivedHits"),S.ReceivedHits);O.Field(TEXT("HitReceipts"),S.HitReceipts);
    O.Field(TEXT("Issued"),S.Issued);
}
void Fields(FObject& O,DungeonWeaponPoseSocket::FResolved& S)
{
    O.Field(TEXT("Supported"),S.Supported);O.Field(TEXT("CustomOverride"),S.CustomOverride);O.Field(TEXT("GroundPoseFallback"),S.GroundPoseFallback);O.Field(TEXT("Clip"),S.Clip);
    O.Field(TEXT("Frame"),S.Frame);O.Field(TEXT("WeaponStateIndex"),S.WeaponStateIndex);O.Field(TEXT("SampleTime"),S.SampleTime);O.Field(TEXT("InstanceId"),S.InstanceId);
    O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("Facing"),S.Facing);O.Field(TEXT("RootX"),S.RootX);O.Field(TEXT("RootY"),S.RootY);
    O.Field(TEXT("BodySize"),S.BodySize);O.Field(TEXT("GripX"),S.GripX);O.Field(TEXT("GripY"),S.GripY);O.Field(TEXT("SupportX"),S.SupportX);
    O.Field(TEXT("SupportY"),S.SupportY);O.Field(TEXT("ComponentSupportX"),S.ComponentSupportX);O.Field(TEXT("ComponentSupportY"),S.ComponentSupportY);O.Field(TEXT("ComponentEmitX"),S.ComponentEmitX);
    O.Field(TEXT("ComponentEmitY"),S.ComponentEmitY);O.Field(TEXT("ComponentGripX"),S.ComponentGripX);O.Field(TEXT("ComponentGripY"),S.ComponentGripY);O.Field(TEXT("EmitX"),S.EmitX);
    O.Field(TEXT("EmitY"),S.EmitY);O.Field(TEXT("Angle"),S.Angle);O.Field(TEXT("Scale"),S.Scale);O.Field(TEXT("ActorOrigin"),S.ActorOrigin);
    O.Field(TEXT("CombatOrigin"),S.CombatOrigin);O.Field(TEXT("PresentationOrigin"),S.PresentationOrigin);
}
void Fields(FObject& O,DungeonEquipmentStats::FValues& S)
{
    O.Field(TEXT("Values"),S.Values);
}
void Fields(FObject& O,DungeonEquipmentStats::FQuantile& S)
{
    O.Field(TEXT("Numerator"),S.Numerator);O.Field(TEXT("Denominator"),S.Denominator);
}
void Fields(FObject& O,DungeonEquipmentStats::FResolved& S)
{
    O.Field(TEXT("Error"),S.Error);O.Field(TEXT("RawBonus"),S.RawBonus);O.Field(TEXT("Final"),S.Final);O.Field(TEXT("DamageMultiplier"),S.DamageMultiplier);
    O.Field(TEXT("StaggerMultiplier"),S.StaggerMultiplier);O.Field(TEXT("ActionTimeScale"),S.ActionTimeScale);O.Field(TEXT("ReachMultiplier"),S.ReachMultiplier);O.Field(TEXT("CritChancePct"),S.CritChancePct);
    O.Field(TEXT("CritMultiplier"),S.CritMultiplier);O.Field(TEXT("SkillCooldownMultiplier"),S.SkillCooldownMultiplier);O.Field(TEXT("FocusCostMultiplier"),S.FocusCostMultiplier);O.Field(TEXT("ReloadSeconds"),S.ReloadSeconds);
    O.Field(TEXT("PrimaryFocusCost"),S.PrimaryFocusCost);O.Field(TEXT("SkillFocusCost"),S.SkillFocusCost);O.Field(TEXT("Armor"),S.Armor);O.Field(TEXT("Ward"),S.Ward);
    O.Field(TEXT("Poise"),S.Poise);O.Field(TEXT("PhysicalMitigation"),S.PhysicalMitigation);O.Field(TEXT("MagicMitigation"),S.MagicMitigation);O.Field(TEXT("MaxHP"),S.MaxHP);
    O.Field(TEXT("CurrentHP"),S.CurrentHP);O.Field(TEXT("IdleMoveMultiplier"),S.IdleMoveMultiplier);O.Field(TEXT("MoveSpeed"),S.MoveSpeed);O.Field(TEXT("FocusRegen"),S.FocusRegen);
    O.Field(TEXT("FocusDelay"),S.FocusDelay);O.Field(TEXT("HealingMultiplier"),S.HealingMultiplier);O.Field(TEXT("PhysicalVulnerabilityMultiplier"),S.PhysicalVulnerabilityMultiplier);O.Field(TEXT("MagicVulnerabilityMultiplier"),S.MagicVulnerabilityMultiplier);
}
void Fields(FObject& O,DungeonEquipmentInventory::FStoredAffix& S)
{
    O.Field(TEXT("Id"),S.Id);O.Field(TEXT("Magnitude"),S.Magnitude);O.Field(TEXT("OriginalQ"),S.OriginalQ);
}
void Fields(FObject& O,DungeonEquipmentInventory::FItem& S)
{
    O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("Version"),S.Version);O.Field(TEXT("ContentId"),S.ContentId);O.Field(TEXT("Grade"),S.Grade);
    O.Field(TEXT("Package"),S.Package);O.Field(TEXT("Tier"),S.Tier);O.Field(TEXT("Affixes"),S.Affixes);O.Field(TEXT("Ammo"),S.Ammo);
    O.Field(TEXT("SkillCooldownDeadline"),S.SkillCooldownDeadline);
}
void Fields(FObject& O,DungeonEquipmentInventory::FPlan& S)
{
    O.Field(TEXT("Action"),S.Action);O.Field(TEXT("Slot"),S.Slot);O.Field(TEXT("BaseRevision"),S.BaseRevision);O.Field(TEXT("SourceId"),S.SourceId);
    O.Field(TEXT("SourceVersion"),S.SourceVersion);O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("InstanceVersion"),S.InstanceVersion);O.Field(TEXT("ReplacedId"),S.ReplacedId);
}
void Fields(FObject& O,DungeonEquipmentInventory::FResult& S)
{
    O.Field(TEXT("Error"),S.Error);O.Field(TEXT("Replayed"),S.Replayed);O.Field(TEXT("Revision"),S.Revision);O.Field(TEXT("AcquiredId"),S.AcquiredId);
    O.Field(TEXT("DroppedId"),S.DroppedId);O.Field(TEXT("DroppedSourceId"),S.DroppedSourceId);O.Field(TEXT("ActiveSlot"),S.ActiveSlot);
}
void Fields(FObject& O,DungeonEquipmentInventory::FSource& S)
{
    O.Field(TEXT("SourceId"),S.SourceId);O.Field(TEXT("Version"),S.Version);O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("Available"),S.Available);
    O.Field(TEXT("SpawnItem"),S.SpawnItem);O.Field(TEXT("CreatedRevision"),S.CreatedRevision);
}
void Fields(FObject& O,DungeonEquipmentInventory::FOperation& S)
{
    O.Field(TEXT("OperationId"),S.OperationId);O.Field(TEXT("Request"),S.Request);O.Field(TEXT("DropSourceId"),S.DropSourceId);O.Field(TEXT("Result"),S.Result);
}
void Fields(FObject& O,DungeonEquipmentInventory::FRuntimeReceipt& S)
{
    O.Field(TEXT("ReceiptId"),S.ReceiptId);O.Field(TEXT("BaseRevision"),S.BaseRevision);O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("BeforeVersion"),S.BeforeVersion);
    O.Field(TEXT("AfterVersion"),S.AfterVersion);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("BeforeAmmo"),S.BeforeAmmo);O.Field(TEXT("Ammo"),S.Ammo);
    O.Field(TEXT("BeforeCooldown"),S.BeforeCooldown);O.Field(TEXT("SkillCooldownDeadline"),S.SkillCooldownDeadline);O.Field(TEXT("Result"),S.Result);
}
void Fields(FObject& O,DungeonEquipmentInventory::FState& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("RunId"),S.RunId);O.Field(TEXT("OwnerId"),S.OwnerId);O.Field(TEXT("Revision"),S.Revision);
    O.Field(TEXT("StarterId"),S.StarterId);O.Field(TEXT("Weapons"),S.Weapons);O.Field(TEXT("Armor"),S.Armor);O.Field(TEXT("ActiveSlot"),S.ActiveSlot);
    O.Field(TEXT("Items"),S.Items);O.Field(TEXT("Sources"),S.Sources);O.Field(TEXT("Operations"),S.Operations);O.Field(TEXT("InitialStarter"),S.InitialStarter);
    O.Field(TEXT("NextRuntimeReceiptId"),S.NextRuntimeReceiptId);O.Field(TEXT("RuntimeUpdates"),S.RuntimeUpdates);
}
void Fields(FObject& O,FDungeonEquipmentAffixView& S)
{
    O.Field(TEXT("Id"),S.Id);O.Field(TEXT("Magnitude"),S.Magnitude);O.Field(TEXT("OriginalQ"),S.OriginalQ);
}
void Fields(FObject& O,FDungeonEquipmentSlotView& S)
{
    O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("Version"),S.Version);O.Field(TEXT("ContentId"),S.ContentId);O.Field(TEXT("Grade"),S.Grade);
    O.Field(TEXT("Tier"),S.Tier);O.Field(TEXT("Package"),S.Package);O.Field(TEXT("Affixes"),S.Affixes);O.Field(TEXT("Ammo"),S.Ammo);
    O.Field(TEXT("CooldownDeadline"),S.CooldownDeadline);
}
void Fields(FObject& O,FDungeonEquipmentActionView& S)
{
    O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("Active"),S.Active);O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("OperationId"),S.OperationId);
    O.Field(TEXT("SourceId"),S.SourceId);O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("Slot"),S.Slot);O.Field(TEXT("Start"),S.Start);
    O.Field(TEXT("Deadline"),S.Deadline);
}
void Fields(FObject& O,FDungeonEquipmentSourceView& S)
{
    O.Field(TEXT("SourceId"),S.SourceId);O.Field(TEXT("InstanceId"),S.InstanceId);O.Field(TEXT("Version"),S.Version);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);
    O.Field(TEXT("LogicalKey"),S.LogicalKey);O.Field(TEXT("Position"),S.Position);O.Field(TEXT("Settled"),S.Settled);O.Field(TEXT("Consumed"),S.Consumed);
    O.Field(TEXT("Item"),S.Item);
}
void Fields(FObject& O,FDungeonEquipmentView& S)
{
    O.Field(TEXT("Bound"),S.Bound);O.Field(TEXT("Config"),S.Config);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("RunAlias"),S.RunAlias);
    O.Field(TEXT("OwnerId"),S.OwnerId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("Revision"),S.Revision);O.Field(TEXT("ActiveSlot"),S.ActiveSlot);
    O.Field(TEXT("Slots"),S.Slots);O.Field(TEXT("SelectedSourceId"),S.SelectedSourceId);O.Field(TEXT("NeedsSlotSelection"),S.NeedsSlotSelection);O.Field(TEXT("SelectionSlot"),S.SelectionSlot);
    O.Field(TEXT("Action"),S.Action);O.Field(TEXT("LastFailure"),S.LastFailure);O.Field(TEXT("FailureText"),S.FailureText);O.Field(TEXT("Stats"),S.Stats);
    O.Field(TEXT("NextInstanceId"),S.NextInstanceId);O.Field(TEXT("NextSourceId"),S.NextSourceId);O.Field(TEXT("NextOperationId"),S.NextOperationId);O.Field(TEXT("NextEquipmentActionId"),S.NextEquipmentActionId);
    O.Field(TEXT("NextRuntimeReceiptId"),S.NextRuntimeReceiptId);O.Field(TEXT("NextImportReceiptId"),S.NextImportReceiptId);O.Field(TEXT("NextFocusReceiptId"),S.NextFocusReceiptId);O.Field(TEXT("CombatSeed"),S.CombatSeed);
    O.Field(TEXT("NextCritDraw"),S.NextCritDraw);O.Field(TEXT("DeveloperCatalogIds"),S.DeveloperCatalogIds);
}
void Fields(FObject& O,FDungeonEquipmentCritReceipt& S)
{
    O.Field(TEXT("WeaponAction"),S.WeaponAction);O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("Draw"),S.Draw);
    O.Field(TEXT("Bits"),S.Bits);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("ChancePct"),S.ChancePct);O.Field(TEXT("Critical"),S.Critical);
}
void Fields(FObject& O,FDungeonEquipmentRuntimeSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("View"),S.View);O.Field(TEXT("HasInventory"),S.HasInventory);O.Field(TEXT("InventoryState"),S.InventoryState);
    O.Field(TEXT("Sources"),S.Sources);O.Field(TEXT("PendingPlan"),S.PendingPlan);O.Field(TEXT("PendingDropPosition"),S.PendingDropPosition);O.Field(TEXT("PendingHasDrop"),S.PendingHasDrop);
    O.Field(TEXT("CritReceipts"),S.CritReceipts);
}
void Fields(FObject& O,FDungeonWorldWeaponKey& S)
{
    O.Field(TEXT("OwnerId"),S.OwnerId);O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("SubhitId"),S.SubhitId);
    O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);
}
void Fields(FObject& O,FDungeonFighterEmissionPoseSnapshot& S)
{
    O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("SubhitId"),S.SubhitId);O.Field(TEXT("Pose"),S.Pose);
}
void Fields(FObject& O,FDungeonFighterSkillHitSnapshot& S)
{
    O.Field(TEXT("ActionId"),S.ActionId);O.Field(TEXT("SubhitId"),S.SubhitId);O.Field(TEXT("TargetId"),S.TargetId);
}
void Fields(FObject& O,FDungeonPlayerKernelSnapshot& S)
{
    O.Field(TEXT("Combat"),S.Combat);O.Field(TEXT("WeaponActions"),S.WeaponActions);O.Field(TEXT("Dodge"),S.Dodge);
}
void Fields(FObject& O,DungeonStoneGuard::FPoint& S)
{
    O.Field(TEXT("X"),S.X);O.Field(TEXT("Y"),S.Y);O.Field(TEXT("Z"),S.Z);
}
void Fields(FObject& O,DungeonStoneGuard::FPolicy& S)
{
    O.Field(TEXT("ExtremelyCloseRadius"),S.ExtremelyCloseRadius);
}
void Fields(FObject& O,DungeonStoneGuard::FAction& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("InProgress"),S.InProgress);O.Field(TEXT("Locked"),S.Locked);
    O.Field(TEXT("WindowIssued"),S.WindowIssued);O.Field(TEXT("Interrupted"),S.Interrupted);O.Field(TEXT("Start"),S.Start);O.Field(TEXT("LockAt"),S.LockAt);
    O.Field(TEXT("ActiveAt"),S.ActiveAt);O.Field(TEXT("ActiveEnd"),S.ActiveEnd);O.Field(TEXT("RecoveryEnd"),S.RecoveryEnd);O.Field(TEXT("CooldownEnd"),S.CooldownEnd);
    O.Field(TEXT("InterruptedAt"),S.InterruptedAt);O.Field(TEXT("CompletedAt"),S.CompletedAt);O.Field(TEXT("Damage"),S.Damage);O.Field(TEXT("Stagger"),S.Stagger);
    O.Field(TEXT("Origin"),S.Origin);O.Field(TEXT("LockedCenter"),S.LockedCenter);O.Field(TEXT("Target"),S.Target);O.Field(TEXT("Facing"),S.Facing);
}
void Fields(FObject& O,DungeonStoneGuard::FDamageWindow& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("Start"),S.Start);
    O.Field(TEXT("End"),S.End);O.Field(TEXT("Damage"),S.Damage);O.Field(TEXT("Stagger"),S.Stagger);O.Field(TEXT("Center"),S.Center);
    O.Field(TEXT("Facing"),S.Facing);
}
void Fields(FObject& O,DungeonStoneGuard::FWindowClosure& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("AtTime"),S.AtTime);
}
void Fields(FObject& O,DungeonStoneGuard::FHitReceipt& S)
{
    O.Field(TEXT("AttackId"),S.AttackId);O.Field(TEXT("TargetId"),S.TargetId);O.Field(TEXT("AtTime"),S.AtTime);
}
void Fields(FObject& O,DungeonStoneGuard::FReceivedHit& S)
{
    O.Field(TEXT("ReceiptId"),S.ReceiptId);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("ActualHPLoss"),S.ActualHPLoss);O.Field(TEXT("Stagger"),S.Stagger);
}
void Fields(FObject& O,DungeonStoneGuard::FEvent& S)
{
    O.Field(TEXT("EventId"),S.EventId);O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("TargetId"),S.TargetId);O.Field(TEXT("Kind"),S.Kind);
    O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("EndTime"),S.EndTime);O.Field(TEXT("Amount"),S.Amount);O.Field(TEXT("From"),S.From);
    O.Field(TEXT("To"),S.To);O.Field(TEXT("Action"),S.Action);
}
void Fields(FObject& O,DungeonStoneGuard::FState& S)
{
    O.Field(TEXT("Version"),S.Version);O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("NextAttackId"),S.NextAttackId);O.Field(TEXT("NextEventId"),S.NextEventId);
    O.Field(TEXT("LastDamageReceiptId"),S.LastDamageReceiptId);O.Field(TEXT("InitialTime"),S.InitialTime);O.Field(TEXT("Time"),S.Time);O.Field(TEXT("HP"),S.HP);
    O.Field(TEXT("PoiseAccum"),S.PoiseAccum);O.Field(TEXT("PoiseDecayOrigin"),S.PoiseDecayOrigin);O.Field(TEXT("LastPoiseAt"),S.LastPoiseAt);O.Field(TEXT("ProtectionUntil"),S.ProtectionUntil);
    O.Field(TEXT("StunUntil"),S.StunUntil);O.Field(TEXT("CombatStartedAt"),S.CombatStartedAt);O.Field(TEXT("WakeStartedAt"),S.WakeStartedAt);O.Field(TEXT("WakeEnd"),S.WakeEnd);
    O.Field(TEXT("AxeReadyAt"),S.AxeReadyAt);O.Field(TEXT("StompReadyAt"),S.StompReadyAt);O.Field(TEXT("OccupiedUntil"),S.OccupiedUntil);O.Field(TEXT("IdleReadyAt"),S.IdleReadyAt);
    O.Field(TEXT("WakeQueued"),S.WakeQueued);O.Field(TEXT("Awakened"),S.Awakened);O.Field(TEXT("RewardClaimed"),S.RewardClaimed);O.Field(TEXT("Phase"),S.Phase);
    O.Field(TEXT("InitialPosition"),S.InitialPosition);O.Field(TEXT("Position"),S.Position);O.Field(TEXT("Facing"),S.Facing);O.Field(TEXT("Action"),S.Action);
    O.Field(TEXT("Windows"),S.Windows);O.Field(TEXT("Closures"),S.Closures);O.Field(TEXT("HitReceipts"),S.HitReceipts);O.Field(TEXT("ReceivedHits"),S.ReceivedHits);
    O.Field(TEXT("Issued"),S.Issued);
}
void Fields(FObject& O,FDungeonStoneGuardOwnerSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("Policy"),S.Policy);O.Field(TEXT("Kernel"),S.Kernel);O.Field(TEXT("DeathObserved"),S.DeathObserved);
}
void Fields(FObject& O,FDungeonFighterOwnerSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("EntityId"),S.EntityId);
    O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("GroundPosition"),S.GroundPosition);O.Field(TEXT("Health"),S.Health);O.Field(TEXT("MaxHealth"),S.MaxHealth);
    O.Field(TEXT("JumpHeight"),S.JumpHeight);O.Field(TEXT("JumpVelocity"),S.JumpVelocity);O.Field(TEXT("Facing"),S.Facing);O.Field(TEXT("Enemy"),S.Enemy);
    O.Field(TEXT("AIEnabled"),S.AIEnabled);O.Field(TEXT("Dead"),S.Dead);O.Field(TEXT("DeathReported"),S.DeathReported);O.Field(TEXT("Coins"),S.Coins);
    O.Field(TEXT("EnemyContentId"),S.EnemyContentId);O.Field(TEXT("WeaponId"),S.WeaponId);O.Field(TEXT("ArmorId"),S.ArmorId);O.Field(TEXT("FocusMirror"),S.FocusMirror);
    O.Field(TEXT("InvulnerableTime"),S.InvulnerableTime);O.Field(TEXT("HurtTime"),S.HurtTime);O.Field(TEXT("AttackCooldown"),S.AttackCooldown);O.Field(TEXT("PoiseAccumulation"),S.PoiseAccumulation);
    O.Field(TEXT("PoiseDecayDelay"),S.PoiseDecayDelay);O.Field(TEXT("PoiseProtection"),S.PoiseProtection);O.Field(TEXT("AirPrimarySpent"),S.AirPrimarySpent);O.Field(TEXT("HurtProtectionSource"),S.HurtProtectionSource);
    O.Field(TEXT("LastSkillEventId"),S.LastSkillEventId);O.Field(TEXT("EmissionPoseSockets"),S.EmissionPoseSockets);O.Field(TEXT("SkillWindows"),S.SkillWindows);O.Field(TEXT("SkillHitReceipts"),S.SkillHitReceipts);
    O.Field(TEXT("AttackElapsed"),S.AttackElapsed);O.Field(TEXT("ArmorChangeRemaining"),S.ArmorChangeRemaining);O.Field(TEXT("FocusConsumeAge"),S.FocusConsumeAge);O.Field(TEXT("AttackResolved"),S.AttackResolved);
    O.Field(TEXT("HasAxe"),S.HasAxe);O.Field(TEXT("PendingArmorId"),S.PendingArmorId);O.Field(TEXT("AttackTime"),S.AttackTime);O.Field(TEXT("HitFlash"),S.HitFlash);
    O.Field(TEXT("AnimationTime"),S.AnimationTime);O.Field(TEXT("LandingVisualAge"),S.LandingVisualAge);O.Field(TEXT("ComboStage"),S.ComboStage);O.Field(TEXT("Moving"),S.Moving);
    O.Field(TEXT("AnimationName"),S.AnimationName);O.Field(TEXT("AttackPhase"),S.AttackPhase);O.Field(TEXT("HeightAnchorRelative"),S.HeightAnchorRelative);O.Field(TEXT("CustomMuzzle"),S.CustomMuzzle);
    O.Field(TEXT("CustomMuzzleRelative"),S.CustomMuzzleRelative);O.Field(TEXT("BatObservedHeight"),S.BatObservedHeight);O.Field(TEXT("Player"),S.Player);O.Field(TEXT("Knight"),S.Knight);
    O.Field(TEXT("Bat"),S.Bat);
    if(O.CodecVersion()==2)O.Field(TEXT("Guard"),S.Guard);
    else if(S.Schema!=2||S.Kind==EDungeonFighterOwnerKind::StoneGuard||S.Guard.IsSet())
        O.Reject(TEXT("Legacy bound-run-v1 cannot contain a Guard owner or new owner schema"));
}
void Fields(FObject& O,FDungeonWorldProjectile& S)
{
    O.Field(TEXT("Key"),S.Key);O.Field(TEXT("Source"),S.Source);O.Field(TEXT("Position"),S.Position);O.Field(TEXT("Traveled"),S.Traveled);
    O.Field(TEXT("Active"),S.Active);O.Field(TEXT("Stop"),S.Stop);O.Field(TEXT("HasPoseSocket"),S.HasPoseSocket);O.Field(TEXT("PoseSocket"),S.PoseSocket);
    O.Field(TEXT("RangeAnchor"),S.RangeAnchor);O.Field(TEXT("UsesActorRangeAnchor"),S.UsesActorRangeAnchor);O.Field(TEXT("LaunchForwardDistance"),S.LaunchForwardDistance);O.Field(TEXT("LaunchClearancePending"),S.LaunchClearancePending);
    O.Field(TEXT("LaunchObstructed"),S.LaunchObstructed);
}
void Fields(FObject& O,FDungeonWorldWeaponWindow& S)
{
    O.Field(TEXT("Key"),S.Key);O.Field(TEXT("Source"),S.Source);O.Field(TEXT("Active"),S.Active);
}
void Fields(FObject& O,FDungeonWorldWeaponHitReceipt& S)
{
    O.Field(TEXT("Key"),S.Key);O.Field(TEXT("TargetId"),S.TargetId);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("Damage"),S.Damage);
    O.Field(TEXT("Stagger"),S.Stagger);O.Field(TEXT("Magic"),S.Magic);O.Field(TEXT("HasPoseSocket"),S.HasPoseSocket);O.Field(TEXT("PoseSocket"),S.PoseSocket);
    O.Field(TEXT("RangeAnchor"),S.RangeAnchor);O.Field(TEXT("LaunchObstructed"),S.LaunchObstructed);
}
void Fields(FObject& O,FDungeonWorldBurn& S)
{
    O.Field(TEXT("Key"),S.Key);O.Field(TEXT("TargetId"),S.TargetId);O.Field(TEXT("Dps"),S.Dps);O.Field(TEXT("AppliedAt"),S.AppliedAt);
    O.Field(TEXT("ExpiresAt"),S.ExpiresAt);O.Field(TEXT("NextTickAt"),S.NextTickAt);O.Field(TEXT("Active"),S.Active);
}
void Fields(FObject& O,FDungeonWorldActorBinding& S)
{
    O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("ContentId"),S.ContentId);
}
void Fields(FObject& O,FDungeonWorldWeaponEvent& S)
{
    O.Field(TEXT("Sequence"),S.Sequence);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("Key"),S.Key);O.Field(TEXT("TargetId"),S.TargetId);
    O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("Position"),S.Position);O.Field(TEXT("Height"),S.Height);O.Field(TEXT("Damage"),S.Damage);
    O.Field(TEXT("Stagger"),S.Stagger);O.Field(TEXT("ActualHPLoss"),S.ActualHPLoss);O.Field(TEXT("Magic"),S.Magic);O.Field(TEXT("HasPoseSocket"),S.HasPoseSocket);
    O.Field(TEXT("PoseSocket"),S.PoseSocket);O.Field(TEXT("RangeAnchor"),S.RangeAnchor);O.Field(TEXT("LaunchObstructed"),S.LaunchObstructed);
}
void Fields(FObject& O,FDungeonWeaponWorldState& S)
{
    O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("Time"),S.Time);O.Field(TEXT("NextEventSequence"),S.NextEventSequence);
    O.Field(TEXT("NextEntityId"),S.NextEntityId);O.Field(TEXT("ActorBindings"),S.ActorBindings);O.Field(TEXT("Projectiles"),S.Projectiles);O.Field(TEXT("Windows"),S.Windows);
    O.Field(TEXT("HitReceipts"),S.HitReceipts);O.Field(TEXT("Burns"),S.Burns);O.Field(TEXT("Events"),S.Events);
}
void Fields(FObject& O,FDungeonWeaponWorldSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("State"),S.State);
}
void Fields(FObject& O,DungeonRoomLayout::FDescription& S)
{
    O.Field(TEXT("Id"),S.Id);O.Field(TEXT("Version"),S.Version);O.Field(TEXT("Entry"),S.Entry);O.Field(TEXT("Exit"),S.Exit);
    O.Field(TEXT("ExitHalfExtent"),S.ExitHalfExtent);O.Field(TEXT("Barrier"),S.Barrier);O.Field(TEXT("Survey"),S.Survey);
}
void Fields(FObject& O,FDungeonSceneObjectView& S)
{
    O.Field(TEXT("ObjectId"),S.ObjectId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("Position"),S.Position);
    O.Field(TEXT("Surveyed"),S.Surveyed);O.Field(TEXT("SurveyCount"),S.SurveyCount);
}
void Fields(FObject& O,FDungeonSceneRoomView& S)
{
    O.Field(TEXT("Active"),S.Active);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("Layout"),S.Layout);
    O.Field(TEXT("Objects"),S.Objects);
}
void Fields(FObject& O,FDungeonSceneInteractionView& S)
{
    O.Field(TEXT("Pending"),S.Pending);O.Field(TEXT("NeedsConfirmation"),S.NeedsConfirmation);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);
    O.Field(TEXT("ObjectId"),S.ObjectId);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("LastFailure"),S.LastFailure);
}
void Fields(FObject& O,FDungeonSceneObjectsSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("CurrentRoom"),S.CurrentRoom);O.Field(TEXT("Rooms"),S.Rooms);O.Field(TEXT("Interaction"),S.Interaction);
}
void Fields(FObject& O,FDungeonRunRewardActorFact& S)
{
    O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("ContentId"),S.ContentId);O.Field(TEXT("Enemy"),S.Enemy);
    O.Field(TEXT("Dead"),S.Dead);O.Field(TEXT("DeathReported"),S.DeathReported);O.Field(TEXT("RewardClaimed"),S.RewardClaimed);
}
void Fields(FObject& O,FDungeonRunRewardDeathRequest& S)
{
    O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("ContentId"),S.ContentId);O.Field(TEXT("AtTime"),S.AtTime);
    O.Field(TEXT("Position"),S.Position);O.Field(TEXT("FirstDeath"),S.FirstDeath);O.Field(TEXT("RoomCleared"),S.RoomCleared);
}
void Fields(FObject& O,FDungeonRunRewardDeathFact& S)
{
    O.Field(TEXT("Death"),S.Death);O.Field(TEXT("SourceIds"),S.SourceIds);
}
void Fields(FObject& O,FDungeonRunRewardSource& S)
{
    O.Field(TEXT("SourceId"),S.SourceId);O.Field(TEXT("ObjectId"),S.ObjectId);O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);
    O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("AtTime"),S.AtTime);
}
void Fields(FObject& O,FDungeonRunRewardObject& S)
{
    O.Field(TEXT("ObjectId"),S.ObjectId);O.Field(TEXT("SourceId"),S.SourceId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("Kind"),S.Kind);
    O.Field(TEXT("Position"),S.Position);O.Field(TEXT("ResolvedAmount"),S.ResolvedAmount);O.Field(TEXT("Consumed"),S.Consumed);O.Field(TEXT("Retired"),S.Retired);
    O.Field(TEXT("CollectionOperationId"),S.CollectionOperationId);O.Field(TEXT("RetiredAt"),S.RetiredAt);
}
void Fields(FObject& O,FDungeonRunRewardCollectRequest& S)
{
    O.Field(TEXT("OperationId"),S.OperationId);O.Field(TEXT("ObjectId"),S.ObjectId);O.Field(TEXT("SourceId"),S.SourceId);O.Field(TEXT("OwnerId"),S.OwnerId);
    O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("BeforeCoins"),S.BeforeCoins);
}
void Fields(FObject& O,FDungeonRunRewardCollection& S)
{
    O.Field(TEXT("Request"),S.Request);O.Field(TEXT("AfterCoins"),S.AfterCoins);
}
void Fields(FObject& O,FDungeonRunRewardRetiredEntity& S)
{
    O.Field(TEXT("Actor"),S.Actor);O.Field(TEXT("RetiredAt"),S.RetiredAt);
}
void Fields(FObject& O,FDungeonRunRewardRoomExit& S)
{
    O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("NextRoomInstanceId"),S.NextRoomInstanceId);O.Field(TEXT("AtTime"),S.AtTime);O.Field(TEXT("EntityIds"),S.EntityIds);
    O.Field(TEXT("ObjectIds"),S.ObjectIds);
}
void Fields(FObject& O,FDungeonRunRewardSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("Bound"),S.Bound);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("OwnerId"),S.OwnerId);
    O.Field(TEXT("CurrentRoomInstanceId"),S.CurrentRoomInstanceId);O.Field(TEXT("NextSourceId"),S.NextSourceId);O.Field(TEXT("NextObjectId"),S.NextObjectId);O.Field(TEXT("NextOperationId"),S.NextOperationId);
    O.Field(TEXT("InitialCoins"),S.InitialCoins);O.Field(TEXT("Deaths"),S.Deaths);O.Field(TEXT("Sources"),S.Sources);O.Field(TEXT("Objects"),S.Objects);
    O.Field(TEXT("Collections"),S.Collections);O.Field(TEXT("RetiredEntities"),S.RetiredEntities);O.Field(TEXT("RoomExits"),S.RoomExits);
}
void Fields(FObject& O,DungeonExploration::FBounds& S)
{
    O.Field(TEXT("MinX"),S.MinX);O.Field(TEXT("MaxX"),S.MaxX);O.Field(TEXT("MinY"),S.MinY);O.Field(TEXT("MaxY"),S.MaxY);
}
void Fields(FObject& O,DungeonExploration::FState& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("Bounds"),S.Bounds);O.Field(TEXT("RoomId"),S.RoomId);O.Field(TEXT("Memory"),S.Memory);
}
void Fields(FObject& O,FDungeonRunExplorationRoom& S)
{
    O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("RoomNumber"),S.RoomNumber);O.Field(TEXT("State"),S.State);
}
void Fields(FObject& O,FDungeonRunExplorationSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("CurrentRoomInstanceId"),S.CurrentRoomInstanceId);O.Field(TEXT("Rooms"),S.Rooms);
}
void Fields(FObject& O,FDungeonActionAudioWeaponCursor& S)
{
    O.Field(TEXT("Attached"),S.Attached);O.Field(TEXT("DrawObserved"),S.DrawObserved);O.Field(TEXT("InsertObserved"),S.InsertObserved);O.Field(TEXT("LastEventId"),S.LastEventId);
    O.Field(TEXT("RuntimeReceiptCount"),S.RuntimeReceiptCount);O.Field(TEXT("LastObservedTime"),S.LastObservedTime);O.Field(TEXT("Reload"),S.Reload);
}
void Fields(FObject& O,FDungeonRunWeaponAudioCursor& S)
{
    O.Field(TEXT("OwnerId"),S.OwnerId);O.Field(TEXT("Cursor"),S.Cursor);
}
void Fields(FObject& O,FDungeonRunStoneAudioSeed& S)
{
    O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("NextEventId"),S.NextEventId);
}
void Fields(FObject& O,FDungeonRunAudioContinuation& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("NextActionSequence"),S.NextActionSequence);
    O.Field(TEXT("WorldHistoryThrough"),S.WorldHistoryThrough);O.Field(TEXT("WeaponCursors"),S.WeaponCursors);O.Field(TEXT("StoneSeeds"),S.StoneSeeds);
}
void Fields(FObject& O,FDungeonRunGeometrySnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("Kind"),S.Kind);
}
void Fields(FObject& O,FDungeonRunPickupSnapshot& S)
{
    O.Field(TEXT("Position"),S.Position);O.Field(TEXT("Kind"),S.Kind);O.Field(TEXT("Consumed"),S.Consumed);O.Field(TEXT("RunGuid"),S.RunGuid);
    O.Field(TEXT("ObjectId"),S.ObjectId);O.Field(TEXT("SourceId"),S.SourceId);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);
}
void Fields(FObject& O,FDungeonRunSnapshot& S)
{
    O.Field(TEXT("Schema"),S.Schema);O.Field(TEXT("Scope"),S.Scope);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("OwnerId"),S.OwnerId);
    O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("RoomNumber"),S.RoomNumber);O.Field(TEXT("SimulationTime"),S.SimulationTime);O.Field(TEXT("LastStoneWakeStartedAt"),S.LastStoneWakeStartedAt);
    O.Field(TEXT("RoomCleared"),S.RoomCleared);O.Field(TEXT("GameOver"),S.GameOver);O.Field(TEXT("WaitingForStart"),S.WaitingForStart);O.Field(TEXT("SceneCommitRequested"),S.SceneCommitRequested);
    O.Field(TEXT("SceneEquipmentTargetLost"),S.SceneEquipmentTargetLost);O.Field(TEXT("LastMessage"),S.LastMessage);O.Field(TEXT("SceneEncounterEntityId"),S.SceneEncounterEntityId);O.Field(TEXT("Geometry"),S.Geometry);
    O.Field(TEXT("Equipment"),S.Equipment);O.Field(TEXT("Scene"),S.Scene);O.Field(TEXT("WeaponWorld"),S.WeaponWorld);O.Field(TEXT("Fighters"),S.Fighters);
    O.Field(TEXT("EnemyOrder"),S.EnemyOrder);O.Field(TEXT("Rewards"),S.Rewards);O.Field(TEXT("Pickups"),S.Pickups);O.Field(TEXT("Exploration"),S.Exploration);
    O.Field(TEXT("Audio"),S.Audio);
}
void Fields(FObject& O,FTransform& S)
{
    FVector Translation=S.GetTranslation(),Scale=S.GetScale3D();FQuat Rotation=S.GetRotation();
    O.Field(TEXT("Translation"),Translation);O.Field(TEXT("Scale"),Scale);O.Field(TEXT("Rotation"),Rotation);
    if(O.Reading()&&O.Good())S.SetComponents(Rotation,Translation,Scale);
}

template<class T>struct TContainer {static constexpr int Kind=0;};
template<class T,class Allocator>struct TContainer<std::vector<T,Allocator>> {static constexpr int Kind=1;using Element=T;};
template<class T,class Allocator>struct TContainer<TArray<T,Allocator>> {static constexpr int Kind=2;using Element=T;};
template<class T,std::size_t Count>struct TContainer<std::array<T,Count>> {static constexpr int Kind=3;using Element=T;static constexpr std::size_t Size=Count;};
template<class T>struct TContainer<TOptional<T>> {static constexpr int Kind=4;using Element=T;};

template<class T>bool Integer(const FString& Text,T& Value)
{
    static_assert(std::is_integral_v<T>&&!std::is_same_v<T,bool>);
    if(Text.IsEmpty()||Text.Len()>21)return false;int32 At=0;bool Negative=false;
    if(Text[0]=='-'){if constexpr(std::is_signed_v<T>){Negative=true;++At;}else return false;}
    if(At==Text.Len()||Text[At]<'0'||Text[At]>'9'||(Text[At]=='0'&&Text.Len()-At!=1))return false;
    uint64 Limit=uint64(std::numeric_limits<T>::max());if(Negative)++Limit;uint64 Magnitude=0;
    for(;At<Text.Len();++At)
    {
        const TCHAR C=Text[At];if(C<'0'||C>'9')return false;const uint64 Digit=uint64(C-'0');
        if(Magnitude>(Limit-Digit)/10||Digit>Limit)return false;Magnitude=Magnitude*10+Digit;
    }
    if(Negative)
    {
        if(!Magnitude)return false;
        if constexpr(std::is_signed_v<T>)
        {
            if(Magnitude==uint64(std::numeric_limits<T>::max())+1)Value=std::numeric_limits<T>::min();
            else Value=-static_cast<T>(Magnitude);
        }
    }
    else Value=static_cast<T>(Magnitude);
    return true;
}
template<class T>FString Decimal(T Value)
{
    if constexpr(std::is_signed_v<T>)return FString::Printf(TEXT("%lld"),static_cast<long long>(Value));
    else return FString::Printf(TEXT("%llu"),static_cast<unsigned long long>(Value));
}
template<class T>bool HexFloat(const FString& Text,T& Value)
{
    static_assert(std::is_floating_point_v<T>&&std::numeric_limits<T>::is_iec559&&(sizeof(T)==4||sizeof(T)==8));
    if(Text.Len()!=int32(sizeof(T)*2))return false;uint64 Bits=0;
    for(int32 I=0;I<Text.Len();++I)
    {
        const TCHAR C=Text[I];if(!((C>='0'&&C<='9')||(C>='a'&&C<='f')))return false;
        Bits=(Bits<<4)|uint64(C<='9'?C-'0':C-'a'+10);
    }
    if constexpr(sizeof(T)==4){const uint32 Narrow=uint32(Bits);FMemory::Memcpy(&Value,&Narrow,4);}
    else FMemory::Memcpy(&Value,&Bits,8);
    return std::isfinite(Value);
}
template<class T>FString FloatBits(T Value)
{
    if constexpr(sizeof(T)==4){uint32 Bits;FMemory::Memcpy(&Bits,&Value,4);return FString::Printf(TEXT("%08x"),Bits);}
    else{uint64 Bits;FMemory::Memcpy(&Bits,&Value,8);return FString::Printf(TEXT("%016llx"),static_cast<unsigned long long>(Bits));}
}

template<class T>bool Transfer(FArchive& A,FNode& Node,T& Value)
{
    if(!A.Good||!A.Node())return false;
    const auto Require=[&](EJson Type)
    {if(A.Reading&&(!Node.IsValid()||Node->Type!=Type)){A.Reject(TEXT("Wrong JSON token type for required field"));return false;}return true;};
    if constexpr(std::is_same_v<T,bool>)
    {
        if(!Require(EJson::Boolean))return false;
        if(A.Reading)Value=Node->AsBool();else Node=MakeShared<FJsonValueBoolean>(Value);return true;
    }
    else if constexpr(std::is_enum_v<T>)
    {
        using U=std::underlying_type_t<T>;U Number=static_cast<U>(Value);
        if(!Transfer(A,Node,Number))return false;const T Candidate=static_cast<T>(Number);
        if(!KnownEnum(Candidate)){A.Reject(TEXT("Unknown persisted enum value"));return false;}
        if(A.Reading)Value=Candidate;return true;
    }
    else if constexpr(std::is_integral_v<T>)
    {
        if(!Require(EJson::String))return false;
        if(A.Reading){if(!Integer(Node->AsString(),Value)){A.Reject(TEXT("Noncanonical or out-of-width decimal integer"));return false;}}
        else Node=MakeShared<FJsonValueString>(Decimal(Value));return true;
    }
    else if constexpr(std::is_floating_point_v<T>)
    {
        if(!Require(EJson::String))return false;
        if(A.Reading){if(!HexFloat(Node->AsString(),Value)){A.Reject(TEXT("Noncanonical, out-of-width or nonfinite IEEE value"));return false;}}
        else
        {
            if(!std::isfinite(Value)){A.Reject(TEXT("Cannot encode a nonfinite IEEE value"));return false;}
            Node=MakeShared<FJsonValueString>(FloatBits(Value));
        }
        return true;
    }
    else if constexpr(std::is_same_v<T,FString>)
    {
        if(!Require(EJson::String))return false;const auto& String=A.Reading?Node->AsString():Value;
        if(!A.Allocate(uint64(String.Len()),sizeof(TCHAR)))return false;
        if(A.Reading)Value=String;else Node=MakeShared<FJsonValueString>(Value);return true;
    }
    else if constexpr(std::is_same_v<T,std::string>)
    {
        FString Text;
        if(A.Reading)
        {
            if(!Require(EJson::String))return false;Text=Node->AsString();
            if(!A.Allocate(uint64(Text.Len()),sizeof(TCHAR)))return false;FTCHARToUTF8 Utf8(*Text,Text.Len());
            if(!A.Allocate(uint64(Utf8.Length()),1))return false;Value.assign(Utf8.Get(),std::size_t(Utf8.Length()));
        }
        else
        {
            if(!A.Allocate(uint64(Value.size()),1)||!NativeUtf8(Value,Text)){A.Reject(TEXT("Invalid native UTF-8 string or allocation limit"));return false;}
            Node=MakeShared<FJsonValueString>(MoveTemp(Text));
        }
        return true;
    }
    else if constexpr(std::is_same_v<T,FName>)
    {
        FString Text=A.Reading?FString():Value.ToString();
        if(!Transfer(A,Node,Text))return false;
        if(A.Reading)
        {
            if(Text.Len()>=NAME_SIZE){A.Reject(TEXT("Persisted FName exceeds native width"));return false;}
            for(int32 I=0;I<Text.Len();++I)if(!Text[I]){A.Reject(TEXT("Persisted FName contains embedded NUL"));return false;}
            Value=FName(*Text);
        }
        return true;
    }
    else if constexpr(TContainer<T>::Kind==4)
    {
        if(A.Reading)
        {
            if(!Node.IsValid()){A.Reject(TEXT("Missing explicit optional value"));return false;}
            if(Node->Type==EJson::Null){Value.Reset();return true;}Value.Emplace();
        }
        else if(!Value.IsSet()){Node=MakeShared<FJsonValueNull>();return true;}
        return Transfer(A,Node,Value.GetValue());
    }
    else if constexpr(TContainer<T>::Kind>=1&&TContainer<T>::Kind<=3)
    {
        using Element=typename TContainer<T>::Element;int32 Count=0;
        if(A.Reading)
        {
            if(!Require(EJson::Array))return false;Count=Node->AsArray().Num();
            if constexpr(TContainer<T>::Kind==3)
            {if(uint64(Count)!=TContainer<T>::Size){A.Reject(TEXT("Wrong fixed-array width"));return false;}}
        }
        else
        {
            uint64 Size;
            if constexpr(TContainer<T>::Kind==2)Size=uint64(Value.Num());else Size=uint64(Value.size());
            if(Size>uint64(MaxElements)){A.Reject(TEXT("Typed array element limit exceeded"));return false;}Count=int32(Size);
        }
        if(!A.Allocate(uint64(Count),sizeof(Element)))return false;
        if(A.Reading)
        {
            if constexpr(TContainer<T>::Kind==1)Value.resize(std::size_t(Count));
            else if constexpr(TContainer<T>::Kind==2)Value.SetNum(Count);
            const auto& Array=Node->AsArray();
            for(int32 I=0;I<Count;++I){FNode Child=Array[I];if(!Transfer(A,Child,Value[I]))return false;}
        }
        else
        {
            TArray<FNode> Array;Array.Reserve(Count);
            for(int32 I=0;I<Count;++I){FNode Child;if(!Transfer(A,Child,Value[I]))return false;Array.Add(MoveTemp(Child));}
            Node=MakeShared<FJsonValueArray>(MoveTemp(Array));
        }
        return true;
    }
    else if constexpr(std::is_same_v<T,TMap<uint64,FDungeonSceneRoomView>>)
    {
        if(!Require(EJson::Array))return false;
        const int32 Count=A.Reading?Node->AsArray().Num():Value.Num();
        if(!A.Allocate(uint64(Count),sizeof(TPair<uint64,FDungeonSceneRoomView>)+3*sizeof(void*)))return false;
        if(A.Reading)
        {
            Value.Reset();uint64 Previous=0;bool First=true;
            for(const auto& Entry:Node->AsArray())
            {
                FNode Child=Entry;FObject Object(A,Child);uint64 Key=0;FDungeonSceneRoomView Room;
                Object.Field(TEXT("Key"),Key);Object.Field(TEXT("Value"),Room);if(!Object.Finish())return false;
                if(!First&&Key<=Previous){A.Reject(TEXT("Map keys are duplicated or not in numeric order"));return false;}
                First=false;Previous=Key;Value.Add(Key,MoveTemp(Room));
            }
        }
        else
        {
            TArray<uint64> Keys;Value.GetKeys(Keys);Keys.Sort();TArray<FNode> Array;Array.Reserve(Keys.Num());
            for(uint64 Key:Keys)
            {
                FNode Child;FObject Object(A,Child);Object.Field(TEXT("Key"),Key);Object.Field(TEXT("Value"),Value.FindChecked(Key));
                if(!Object.Finish())return false;Array.Add(MoveTemp(Child));
            }
            Node=MakeShared<FJsonValueArray>(MoveTemp(Array));
        }
        return true;
    }
    else
    {
        FObject Object(A,Node);if(!A.Good)return false;Fields(Object,Value);return Object.Finish();
    }
}

bool Document(FArchive& Archive,FNode& Node,FDungeonRunSnapshot& Snapshot)
{
    FObject Envelope(Archive,Node);FString Codec=Snapshot.Schema==2?TEXT("bound-run-v2"):TEXT("bound-run-v1");
    // Decode the explicit discriminator before selecting any owner field layout.
    Envelope.Field(TEXT("codec"),Codec);
    if(Codec.Equals(TEXT("bound-run-v1"),ESearchCase::CaseSensitive))Archive.CodecVersion=1;
    else if(Codec.Equals(TEXT("bound-run-v2"),ESearchCase::CaseSensitive))Archive.CodecVersion=2;
    else{Archive.Reject(TEXT("Unknown Run codec version"));return false;}
    Envelope.Field(TEXT("snapshot"),Snapshot);
    if(!Envelope.Finish())return false;
    if(Archive.CodecVersion==1?(Snapshot.Schema!=1||Snapshot.Scope!=EDungeonRunScope::BoundDevelopmentV1)
        :(Snapshot.Schema!=2||Snapshot.Scope!=EDungeonRunScope::BoundDevelopmentV2))
    {Archive.Reject(TEXT("Run codec version and complete root schema/scope disagree"));return false;}
    return Archive.Good;
}
bool Serialize(FDungeonRunSnapshot& Snapshot,TArray<uint8>& Bytes,FString& Why)
{
    FArchive Archive(false,Why);FNode Node;
    if(!Document(Archive,Node,Snapshot))return false;
    FCanonicalWriter Writer(Why);return Writer.Write(Node,Bytes);
}
} // anonymous namespace

bool Encode(const FDungeonRunSnapshot& Saved,TArray<uint8>& Out,FString& Diagnostic)
{
    Diagnostic.Reset();FDungeonValidatedRun Validated;
    if(!FDungeonRunAggregate::Validate(Saved,Validated,Diagnostic))return false;
    // Serialization operates on a separate owning copy, never live owner state.
    FDungeonRunSnapshot Candidate=*Validated.Get();TArray<uint8> Bytes;
    if(!Serialize(Candidate,Bytes,Diagnostic))return false;
    Out=MoveTemp(Bytes);Diagnostic.Reset();return true;
}
bool Decode(const TArray<uint8>& Payload,FDungeonValidatedRun& Out,FString& Diagnostic)
{
    Diagnostic.Reset();FNode Node;FStrictParser Parser(Payload,Diagnostic);
    if(!Parser.Parse(Node))return false;
    FDungeonRunSnapshot Candidate;FArchive Archive(true,Diagnostic);
    if(!Document(Archive,Node,Candidate))return false;
    // Re-emit the actual typed values, not the permissive parsed DOM. Reject
    // alternate escapes/order and any native conversion that would change bytes.
    TArray<uint8> Canonical;if(!Serialize(Candidate,Canonical,Diagnostic))return false;
    if(Canonical!=Payload)return Fail(Diagnostic,TEXT("Payload is not the exact canonical representation of its native values"));
    FDungeonValidatedRun Sealed;
    if(!FDungeonRunAggregate::Validate(Candidate,Sealed,Diagnostic))return false;
    Out=MoveTemp(Sealed);Diagnostic.Reset();return true;
}
}
