#include "DungeonSaveGenerationStore.h"
#include "HAL/FileManager.h"
#include "Misc/Crc.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/ScopeLock.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include <cmath>
#if PLATFORM_WINDOWS
#include "Windows/WindowsHWrapper.h"
#include "Windows/AllowWindowsPlatformTypes.h"
#include <bcrypt.h>
#include "Windows/HideWindowsPlatformTypes.h"
#pragma comment(lib,"bcrypt.lib")
#endif

namespace DungeonSaveGenerationStore
{
namespace
{
// Explicit implementation allocation limits, not a measured full-game budget.
constexpr int64 MaxEncodedBytes=64ll*1024*1024;
constexpr int32 MaxJsonDepth=128;
constexpr int32 ContainerVersion=1;
TArray<uint8> Utf8(const FString& S)
{
    FTCHARToUTF8 C(*S);TArray<uint8> B;B.Append(reinterpret_cast<const uint8*>(C.Get()),C.Length());return B;
}
bool Text(const TArray<uint8>& B,FString& Out)
{
    if(B.IsEmpty()||B.Num()>MaxEncodedBytes)return false;
    FUTF8ToTCHAR C(reinterpret_cast<const ANSICHAR*>(B.GetData()),B.Num());
    Out=FString(C.Length(),C.Get());return Utf8(Out)==B; // Reject replacement/invalid UTF-8, including BOM differences.
}
FString Quote(const FString& S)
{
    FString Out;auto W=TJsonWriterFactory<TCHAR,TCondensedJsonPrintPolicy<TCHAR>>::Create(&Out);
    W->WriteArrayStart();W->WriteValue(S);W->WriteArrayEnd();W->Close();return Out.Mid(1,Out.Len()-2);
}
FString Decimal(uint64 V){return LexToString(V);}
bool UInt(const FString& S,uint64& Out)
{
    if(S.IsEmpty()||(S.Len()>1&&S[0]=='0'))return false;Out=0;
    for(TCHAR C:S)
    {
        if(C<'0'||C>'9')return false;const uint64 N=uint64(C-'0');
        if(Out>(TNumericLimits<uint64>::Max()-N)/10)return false;Out=Out*10+N;
    }return true;
}
bool StringField(const TSharedPtr<FJsonObject>& O,const TCHAR* K,FString& Out)
{
    const auto* P=O->Values.Find(K);if(!P||!P->IsValid()||(*P)->Type!=EJson::String)return false;
    Out=(*P)->AsString();return true;
}
bool UIntField(const TSharedPtr<FJsonObject>& O,const TCHAR* K,uint64& Out)
{FString S;return StringField(O,K,S)&&UInt(S,Out);}
bool NumberField(const TSharedPtr<FJsonObject>& O,const TCHAR* K,double& Out)
{
    const auto* P=O->Values.Find(K);if(!P||!P->IsValid()||(*P)->Type!=EJson::Number)return false;
    Out=(*P)->AsNumber();return std::isfinite(Out);
}

// UE's DOM silently replaces duplicate object keys. Scan the original bytes
// first, decoding escaped keys so "a" and "\u0061" also conflict.
struct FStrictJson
{
    const TArray<uint8>& B;int32 I=0,PayloadBegin=-1,PayloadEnd=-1;
    explicit FStrictJson(const TArray<uint8>& Bytes):B(Bytes){}
    void White(){while(I<B.Num()&&(B[I]==' '||B[I]=='\n'||B[I]=='\r'||B[I]=='\t'))++I;}
    bool Take(uint8 C){White();if(I>=B.Num()||B[I]!=C)return false;++I;return true;}
    bool String(FString* Decoded=nullptr)
    {
        if(I>=B.Num()||B[I]!='"')return false;const int32 Start=I++;
        while(I<B.Num())
        {
            const uint8 C=B[I++];if(C<32)return false;
            if(C=='"')
            {
                if(Decoded)
                {
                    TArray<uint8> Slice;Slice.Append(B.GetData()+Start,I-Start);FString Raw;
                    if(!Text(Slice,Raw))return false;TSharedPtr<FJsonObject> Object;
                    if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(TEXT("{\"key\":")+Raw+TEXT("}")),Object))return false;
                    *Decoded=Object->GetStringField(TEXT("key"));
                }return true;
            }
            if(C=='\\')
            {
                if(I>=B.Num())return false;const uint8 E=B[I++];
                if(E=='u')
                {for(int32 N=0;N<4;++N){if(I>=B.Num()||!((B[I]>='0'&&B[I]<='9')||(B[I]>='a'&&B[I]<='f')||(B[I]>='A'&&B[I]<='F')))return false;++I;}}
                else if(E!='"'&&E!='\\'&&E!='/'&&E!='b'&&E!='f'&&E!='n'&&E!='r'&&E!='t')return false;
            }
        }return false;
    }
    bool Value(int32 Depth)
    {
        if(Depth>MaxJsonDepth)return false;White();if(I>=B.Num())return false;const uint8 C=B[I];
        if(C=='{')
        {
            ++I;White();if(I<B.Num()&&B[I]=='}'){++I;return true;}TSet<FString> Keys;
            for(;;)
            {
                White();FString Key;if(!String(&Key)||Keys.Contains(Key)||!Take(':'))return false;Keys.Add(Key);
                White();const int32 Begin=I;if(!Value(Depth+1))return false;
                if(Depth==0&&Key==TEXT("payload")){PayloadBegin=Begin;PayloadEnd=I;}
                White();if(I<B.Num()&&B[I]=='}'){++I;return true;}if(!Take(','))return false;
            }
        }
        if(C=='[')
        {
            ++I;White();if(I<B.Num()&&B[I]==']'){++I;return true;}
            for(;;){if(!Value(Depth+1))return false;White();if(I<B.Num()&&B[I]==']'){++I;return true;}if(!Take(','))return false;}
        }
        if(C=='"')return String();
        for(const ANSICHAR* Literal:{"true","false","null"})
        {
            const int32 Len=FCStringAnsi::Strlen(Literal);
            if(I+Len<=B.Num()&&FMemory::Memcmp(B.GetData()+I,Literal,Len)==0){I+=Len;return true;}
        }
        const int32 Start=I;if(B[I]=='-')++I;if(I>=B.Num())return false;
        if(B[I]=='0')++I;
        else{if(B[I]<'1'||B[I]>'9')return false;while(I<B.Num()&&B[I]>='0'&&B[I]<='9')++I;}
        if(I<B.Num()&&B[I]=='.'){++I;const int32 At=I;while(I<B.Num()&&B[I]>='0'&&B[I]<='9')++I;if(I==At)return false;}
        if(I<B.Num()&&(B[I]=='e'||B[I]=='E'))
        {++I;if(I<B.Num()&&(B[I]=='+'||B[I]=='-'))++I;const int32 At=I;while(I<B.Num()&&B[I]>='0'&&B[I]<='9')++I;if(I==At)return false;}
        TArray<uint8> Slice;Slice.Append(B.GetData()+Start,I-Start);FString N;
        return Text(Slice,N)&&std::isfinite(FCString::Atod(*N));
    }
    bool Object(TSharedPtr<FJsonObject>& Out)
    {
        FString S;if(!Text(B,S)||B[0]!='{'||B.Last()!='}'||!Value(0)||I!=B.Num())return false;
        return FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(S),Out)&&Out.IsValid();
    }
};
struct FMarker
{
    int32 Format=ContainerVersion;FGuid Profile;uint64 Generation=0,Parent=0,Length=0;
    FString Sha,Digest;uint32 Crc=0;
};
FString MarkerBody(const FMarker& M,bool WithDigest)
{
    FString S=TEXT("{\"container_version\":")+LexToString(M.Format)+TEXT(",\"ProfileID\":")+Quote(M.Profile.ToString(EGuidFormats::DigitsWithHyphensLower))
        +TEXT(",\"GenerationID\":")+Quote(Decimal(M.Generation))+TEXT(",\"parent_generation\":")+Quote(Decimal(M.Parent))
        +TEXT(",\"bundle_byte_length\":")+Quote(Decimal(M.Length))+TEXT(",\"bundle_sha256\":")+Quote(M.Sha)
        +TEXT(",\"bundle_crc32\":")+Quote(Decimal(M.Crc));
    if(WithDigest)S+=TEXT(",\"marker_integrity_digest\":")+Quote(M.Digest);return S+TEXT("}");
}
bool ParseMarker(const TArray<uint8>& B,FMarker& M)
{
    TSharedPtr<FJsonObject> O;FStrictJson Scan(B);double Format=0;uint64 Crc=0;FString Profile;
    if(!Scan.Object(O)||O->Values.Num()!=8||!NumberField(O,TEXT("container_version"),Format)||Format<1||Format>MAX_int32||std::floor(Format)!=Format
        ||!StringField(O,TEXT("ProfileID"),Profile)||!FGuid::Parse(Profile,M.Profile)||!M.Profile.IsValid()
        ||!UIntField(O,TEXT("GenerationID"),M.Generation)||!M.Generation||!UIntField(O,TEXT("parent_generation"),M.Parent)||M.Parent>=M.Generation
        ||!UIntField(O,TEXT("bundle_byte_length"),M.Length)||!M.Length||M.Length>uint64(MaxEncodedBytes)
        ||!StringField(O,TEXT("bundle_sha256"),M.Sha)||M.Sha.Len()!=64||!UIntField(O,TEXT("bundle_crc32"),Crc)||Crc>MAX_uint32
        ||!StringField(O,TEXT("marker_integrity_digest"),M.Digest)||M.Digest.Len()!=64)return false;
    M.Format=int32(Format);M.Crc=uint32(Crc);
    return !M.Sha.Contains(TEXT("\n"))&&FGenerationStore::Sha256(Utf8(MarkerBody(M,false)))==M.Digest;
}
bool Encode(const FGeneration& G,TArray<uint8>& Out)
{
    TSharedPtr<FJsonObject> Payload;FStrictJson Check(G.CanonicalPayload);FString P;
    if(!G.ProfileId.IsValid()||!G.GenerationId||G.ParentGeneration>=G.GenerationId||G.RestoredFromGeneration>=G.GenerationId||G.Versions.Schema.IsEmpty()
        ||G.Versions.ContentRules.IsEmpty()||G.Versions.Coordinates.IsEmpty()||G.BuildId.IsEmpty()
        ||(G.RunSimulationTime.IsSet()&&(!std::isfinite(G.RunSimulationTime.GetValue())||G.RunSimulationTime.GetValue()<0.))
        ||!Check.Object(Payload)||!Text(G.CanonicalPayload,P))return false;
    FString S=TEXT("{\"container_version\":1,\"ProfileID\":")+Quote(G.ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower))
        +TEXT(",\"GenerationID\":")+Quote(Decimal(G.GenerationId))+TEXT(",\"parent_generation\":")+Quote(Decimal(G.ParentGeneration))
        +TEXT(",\"schema_version\":")+Quote(G.Versions.Schema)+TEXT(",\"content_rules_version\":")+Quote(G.Versions.ContentRules)
        +TEXT(",\"coordinate_version\":")+Quote(G.Versions.Coordinates)+TEXT(",\"build_id\":")+Quote(G.BuildId)
        +TEXT(",\"run_sim_time_or_null\":")+(G.RunSimulationTime.IsSet()?FString::Printf(TEXT("%.17g"),G.RunSimulationTime.GetValue()):FString(TEXT("null")))
        +TEXT(",\"restored_from_generation\":")+Quote(Decimal(G.RestoredFromGeneration))+TEXT(",\"payload\":")+P+TEXT("}");
    Out=Utf8(S);return Out.Num()<=MaxEncodedBytes;
}
bool Decode(const TArray<uint8>& B,FGeneration& G)
{
    FStrictJson Scan(B);TSharedPtr<FJsonObject> O;FString Profile;double Format=0;
    if(!Scan.Object(O)||O->Values.Num()!=11||!NumberField(O,TEXT("container_version"),Format)||Format!=ContainerVersion
        ||!StringField(O,TEXT("ProfileID"),Profile)||!FGuid::Parse(Profile,G.ProfileId)
        ||!UIntField(O,TEXT("GenerationID"),G.GenerationId)||!UIntField(O,TEXT("parent_generation"),G.ParentGeneration)
        ||!StringField(O,TEXT("schema_version"),G.Versions.Schema)||!StringField(O,TEXT("content_rules_version"),G.Versions.ContentRules)
        ||!StringField(O,TEXT("coordinate_version"),G.Versions.Coordinates)||!StringField(O,TEXT("build_id"),G.BuildId)
        ||!UIntField(O,TEXT("restored_from_generation"),G.RestoredFromGeneration)||G.RestoredFromGeneration>=G.GenerationId
        ||Scan.PayloadBegin<0||Scan.PayloadEnd<=Scan.PayloadBegin)return false;
    const auto* Time=O->Values.Find(TEXT("run_sim_time_or_null"));if(!Time||!Time->IsValid())return false;
    if((*Time)->Type==EJson::Number){const double T=(*Time)->AsNumber();if(!std::isfinite(T)||T<0.)return false;G.RunSimulationTime=T;}
    else if((*Time)->Type!=EJson::Null)return false;
    G.CanonicalPayload.Append(B.GetData()+Scan.PayloadBegin,Scan.PayloadEnd-Scan.PayloadBegin);
    TArray<uint8> Reencoded;return Encode(G,Reencoded)&&Reencoded==B; // Exact known header encoding; never discard unknown fields.
}
bool Read(const FString& Path,TArray<uint8>& B)
{
    const int64 Size=IFileManager::Get().FileSize(*Path);
    return Size>=0&&Size<=MaxEncodedBytes&&FFileHelper::LoadFileToArray(B,*Path)&&B.Num()==Size;
}
FCommitResult Failure(EStatus S,const TCHAR* Why)
{FCommitResult R;R.Status=S;R.Diagnostic=Why;return R;}
FCommitResult Receipt(const FMarker& M,bool Replay=false)
{
    FCommitResult R;R.Status=EStatus::Ok;R.GenerationId=M.Generation;R.BundleSha256=M.Sha;
    R.BundleCrc32=M.Crc;R.BundleByteLength=int64(M.Length);R.Replayed=Replay;return R;
}
}

struct FGenerationStore::FImpl
{
    FString Directory;FGuid Profile;FVersions Supported;bool RequestValid=false;
    mutable FCriticalSection Mutex;
#if PLATFORM_WINDOWS
    HANDLE Writer=INVALID_HANDLE_VALUE;
#endif
    bool Held() const
    {
#if PLATFORM_WINDOWS
        return Writer!=INVALID_HANDLE_VALUE;
#else
        return false;
#endif
    }
    FString File(ESlot Slot,const TCHAR* Suffix) const
    {return Directory/(FString(Slot==ESlot::A?TEXT("slot-A."):TEXT("slot-B."))+Suffix);}
    struct FInspection
    {
        EStatus Status=EStatus::Empty;FMarker Markers[2];bool Present[2]={false,false};
        uint64 Head=0;ESlot Slot=ESlot::A;bool UnknownHead=false;FString Why;
    };
    // The existing Load predicate, shared unchanged with every normal commit
    // and same-generation replay. A new marker must not wash a broken chain.
    bool ParentRelationship(const FInspection& I,const FGeneration& Head) const
    {
        if(!I.Present[0]||!I.Present[1])return true;
        const auto& Other=I.Markers[1-int32(I.Slot)];
        return Other.Generation==I.Head||Head.ParentGeneration==Other.Generation
            ||(Head.RestoredFromGeneration==Other.Generation&&Head.ParentGeneration>Other.Generation);
    }
    bool HistoryEvidence(const TCHAR* Name) const
    {
        const FString P=Directory/Name;
#if PLATFORM_WINDOWS
        const DWORD Attributes=::GetFileAttributesW(*P);
        if(Attributes==INVALID_FILE_ATTRIBUTES)
        {const DWORD E=::GetLastError();return E!=ERROR_FILE_NOT_FOUND&&E!=ERROR_PATH_NOT_FOUND;}
        if(!(Attributes&FILE_ATTRIBUTE_DIRECTORY))return true; // Known directory name occupied by a file.
        WIN32_FIND_DATAW Data;const HANDLE Search=::FindFirstFileW(*(P/TEXT("*")),&Data);
        if(Search==INVALID_HANDLE_VALUE)
        {const DWORD E=::GetLastError();return E!=ERROR_FILE_NOT_FOUND&&E!=ERROR_NO_MORE_FILES;}
        bool Found=false;
        do
        {
            if(FCString::Strcmp(Data.cFileName,TEXT("."))&&FCString::Strcmp(Data.cFileName,TEXT("..")))
            {Found=true;break;}
        }while(::FindNextFileW(Search,&Data));
        const DWORD EndError=::GetLastError();::FindClose(Search);
        return Found||EndError!=ERROR_NO_MORE_FILES; // Failed enumeration is unresolved evidence, not an empty history.
#else
        // Writes are unsupported here; never infer a fresh profile from a
        // history path whose contents this Windows primitive cannot inspect.
        return IFileManager::Get().FileExists(*P)||IFileManager::Get().DirectoryExists(*P);
#endif
    }
    FInspection Inspect() const
    {
        FInspection R;if(!RequestValid){R.Status=EStatus::InvalidRequest;return R;}
        if(!IFileManager::Get().DirectoryExists(*Directory))
        {
            if(IFileManager::Get().FileExists(*Directory))
            {R.Status=EStatus::RecoveryRequired;R.UnknownHead=true;R.Why=TEXT("Profile directory collides with existing evidence");}
            return R;
        }
        TArray<FString> Names;IFileManager::Get().FindFiles(Names,*(Directory/TEXT("*")),true,true);
        const TSet<FString> Allowed={TEXT("slot-A.bundle.json"),TEXT("slot-A.commit.json"),TEXT("slot-B.bundle.json"),TEXT("slot-B.commit.json"),TEXT("writer.lock"),TEXT("temporary"),TEXT("recovery"),TEXT("migration")};
        for(const FString& Name:Names)if(!Allowed.Contains(Name))
        {R.Status=EStatus::RecoveryRequired;R.UnknownHead=true;R.Why=TEXT("Unresolved existing profile evidence");return R;}
        for(int32 N=0;N<2;++N)
        {
            const ESlot Slot=N?ESlot::B:ESlot::A;const FString P=File(Slot,TEXT("commit.json"));
            R.Present[N]=IFileManager::Get().FileExists(*P);if(!R.Present[N])continue;TArray<uint8> B;
            if(!Read(P,B)||!ParseMarker(B,R.Markers[N])||R.Markers[N].Profile!=Profile)
            {R.Status=EStatus::RecoveryRequired;R.UnknownHead=true;R.Why=TEXT("Unknown/malformed marker; highest generation cannot be established");return R;}
            if(R.Markers[N].Generation>R.Head){R.Head=R.Markers[N].Generation;R.Slot=Slot;}
        }
        if(!R.Head)
        {
            if(HistoryEvidence(TEXT("recovery"))||HistoryEvidence(TEXT("migration")))
            {
                R.Status=EStatus::RecoveryRequired;R.UnknownHead=true;
                R.Why=TEXT("Existing recovery/migration evidence without a trustworthy root generation");return R;
            }
            if(IFileManager::Get().FileExists(*File(ESlot::A,TEXT("bundle.json")))||IFileManager::Get().FileExists(*File(ESlot::B,TEXT("bundle.json"))))
            {R.Status=EStatus::RecoveryRequired;R.Why=TEXT("Unmarked bundle is evidence, never default bootstrap");}
            return R;
        }
        if(R.Present[0]&&R.Present[1])
        {
            const auto& A=R.Markers[0];const auto& B=R.Markers[1];
            if(A.Generation==B.Generation&&(A.Sha!=B.Sha||A.Length!=B.Length||A.Crc!=B.Crc||A.Parent!=B.Parent))
            {R.Status=EStatus::Conflict;R.Why=TEXT("Same generation has different digests");return R;}
        }
        R.Status=EStatus::Ok;return R;
    }
    bool Bundle(const FMarker& M,ESlot Slot,FGeneration& G,TArray<uint8>* Bytes=nullptr) const
    {
        TArray<uint8> B;if(M.Format!=ContainerVersion||!Read(File(Slot,TEXT("bundle.json")),B)||uint64(B.Num())!=M.Length
            ||FCrc::MemCrc32(B.GetData(),B.Num())!=M.Crc||FGenerationStore::Sha256(B)!=M.Sha||!Decode(B,G)
            ||G.ProfileId!=Profile||G.GenerationId!=M.Generation||G.ParentGeneration!=M.Parent)return false;
        if(Bytes)*Bytes=MoveTemp(B);return true;
    }
    FLoadResult Load(const FPayloadValidator& Validator) const
    {
        FLoadResult R;if(!Validator){R.Status=EStatus::InvalidRequest;R.Diagnostic=TEXT("Caller semantic validator is mandatory");return R;}
        const auto I=Inspect();R.Status=I.Status;R.ObservedHeadGeneration=I.Head;R.Slot=I.Slot;R.Diagnostic=I.Why;
        if(I.Status!=EStatus::Ok)return R;
        if(!Bundle(I.Markers[int32(I.Slot)],I.Slot,R.Generation)||!(R.Generation.Versions==Supported))
        {R.Status=EStatus::RecoveryRequired;R.Generation={};R.Diagnostic=TEXT("Highest published bytes or versions are invalid/unsupported; no fallback");return R;}
        if(!ParentRelationship(I,R.Generation))
        {R.Status=EStatus::RecoveryRequired;R.Generation={};R.Diagnostic=TEXT("Unexplained generation-parent gap");return R;}
        if(!Validator(R.Generation,R.Diagnostic)){R.Status=EStatus::RecoveryRequired;R.Generation={};return R;}
        R.Status=EStatus::Ok;return R;
    }
    EStatus WriteTemp(const FString& P,const TArray<uint8>& B,bool Marker,EFaultPoint Fault) const
    {
#if PLATFORM_WINDOWS
        const HANDLE H=::CreateFileW(*P,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,nullptr);
        if(H==INVALID_HANDLE_VALUE)return EStatus::IoFailure;
        const auto Close=[H](){::CloseHandle(H);};DWORD Written=0;
        const EFaultPoint Partial=Marker?EFaultPoint::PartialMarkerWrite:EFaultPoint::PartialBundleWrite;
        const int32 Count=Fault==Partial?FMath::Max(1,B.Num()/2):B.Num();
        const bool Wrote=::WriteFile(H,B.GetData(),DWORD(Count),&Written,nullptr)!=0&&Written==DWORD(Count);
        if(!Wrote){Close();return EStatus::IoFailure;}
        if(Fault==Partial||Fault==(Marker?EFaultPoint::MarkerWrittenBeforeFlush:EFaultPoint::BundleWrittenBeforeFlush))
        {Close();return EStatus::InjectedFailure;}
        const bool Flushed=::FlushFileBuffers(H)!=0;Close();if(!Flushed)return EStatus::IoFailure;
        if(Fault==(Marker?EFaultPoint::MarkerFlushed:EFaultPoint::BundleFlushed))return EStatus::InjectedFailure;
        TArray<uint8> Actual;if(!Read(P,Actual)||Actual!=B)return EStatus::IoFailure;
        const FString ActualSha=FGenerationStore::Sha256(Actual),ExpectedSha=FGenerationStore::Sha256(B);
        if(ActualSha.Len()!=64||ExpectedSha.Len()!=64||ActualSha!=ExpectedSha
            ||FCrc::MemCrc32(Actual.GetData(),Actual.Num())!=FCrc::MemCrc32(B.GetData(),B.Num()))return EStatus::IoFailure;
        if(Fault==(Marker?EFaultPoint::MarkerReadBack:EFaultPoint::BundleReadBack))return EStatus::InjectedFailure;
        return EStatus::Ok;
#else
        return EStatus::UnsupportedPlatform;
#endif
    }
    bool Install(const FString& From,const FString& To) const
    {
#if PLATFORM_WINDOWS
        // Both paths are below this one profile directory. COPY_ALLOWED is
        // deliberately absent: publication must remain a same-volume rename.
        return ::MoveFileExW(*From,*To,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
        return false;
#endif
    }
    FCommitResult Commit(const FGeneration& G,const FPayloadValidator& Validator,EFaultPoint Fault,bool Recovery=false)
    {
        if(!Held())return Failure(EStatus::WriterBusy,TEXT("No exclusive profile writer lease"));
        if(uint8(Fault)>uint8(EFaultPoint::AfterMarkerPublish))return Failure(EStatus::InvalidRequest,TEXT("Unknown diagnostic IO boundary"));
        TArray<uint8> B;
        if(!Validator||G.ProfileId!=Profile||!(G.Versions==Supported)||!Encode(G,B)||(!Recovery&&G.RestoredFromGeneration))
            return Failure(EStatus::InvalidRequest,TEXT("Invalid known whole-generation candidate"));
        FString Why;if(!Validator(G,Why)){auto R=Failure(EStatus::ValidatorRejected,TEXT("Caller semantic validator rejected candidate"));R.Diagnostic=Why;return R;}
        FMarker M;M.Profile=Profile;M.Generation=G.GenerationId;M.Parent=G.ParentGeneration;M.Length=B.Num();
        M.Sha=FGenerationStore::Sha256(B);M.Crc=FCrc::MemCrc32(B.GetData(),B.Num());
        M.Digest=FGenerationStore::Sha256(Utf8(MarkerBody(M,false)));
        if(M.Sha.Len()!=64||M.Digest.Len()!=64)return Failure(EStatus::IoFailure,TEXT("Native SHA256 unavailable"));
        const auto I=Inspect();
        if(I.Status==EStatus::Conflict)return Failure(EStatus::Conflict,TEXT("Conflicting existing generations"));
        if(I.UnknownHead)return Failure(EStatus::RecoveryRequired,TEXT("Unresolved highest-generation evidence"));
        if(I.Status!=EStatus::Ok&&I.Status!=EStatus::Empty)
        {
            // A failed first publication may have installed exactly this same
            // private candidate. Only its identical retry may finish bootstrap.
            TArray<uint8> Existing;
            const bool FirstRetry=!Recovery&&I.Head==0&&G.GenerationId==1&&G.ParentGeneration==0
                &&!IFileManager::Get().FileExists(*File(ESlot::B,TEXT("bundle.json")))
                &&Read(File(ESlot::A,TEXT("bundle.json")),Existing)&&Existing==B;
            if(!FirstRetry)return Failure(EStatus::RecoveryRequired,TEXT("Existing evidence is not a fresh profile"));
        }
        if(I.Head)
        {
            const auto& Head=I.Markers[int32(I.Slot)];
            if(G.GenerationId==I.Head)
            {
                FGeneration Existing;if(!Bundle(Head,I.Slot,Existing))return Failure(EStatus::RecoveryRequired,TEXT("Published retry head is corrupt"));
                if(!(Existing.Versions==Supported))return Failure(EStatus::RecoveryRequired,TEXT("Published retry head has unknown versions"));
                if(!ParentRelationship(I,Existing))return Failure(EStatus::RecoveryRequired,TEXT("Published retry head has unresolved parent gap"));
                return Head.Sha==M.Sha&&Head.Length==M.Length&&Head.Crc==M.Crc?Receipt(Head,true):Failure(EStatus::Conflict,TEXT("Generation reused with different bytes"));
            }
            if(!Recovery)
            {
                FGeneration Existing;
                if(!Bundle(Head,I.Slot,Existing)||!(Existing.Versions==Supported)||!ParentRelationship(I,Existing)||!Validator(Existing,Why))
                    return Failure(EStatus::RecoveryRequired,TEXT("Normal commit cannot replace corrupt/unknown/semantically invalid head"));
            }
        }
        if(I.Head==TNumericLimits<uint64>::Max()||G.GenerationId!=I.Head+1||G.ParentGeneration!=I.Head)
            return Failure(EStatus::InvalidRequest,TEXT("Generation/parent must advance the observed head exactly once"));
        // Explicit recovery preserves the verified selected backup and replaces
        // the damaged/newer head only after its originals have been archived.
        const ESlot Target=I.Head?(Recovery?I.Slot:(I.Slot==ESlot::A?ESlot::B:ESlot::A)):ESlot::A;
        if(Recovery&&G.RestoredFromGeneration==0)return Failure(EStatus::InvalidRequest,TEXT("Recovery requires verified backup audit"));
        const FString Attempt=Directory/TEXT("temporary")/(Decimal(G.GenerationId)+TEXT("-")+FGuid::NewGuid().ToString(EGuidFormats::Digits));
        if(!IFileManager::Get().MakeDirectory(*Attempt,true))return Failure(EStatus::IoFailure,TEXT("Cannot create isolated candidate directory"));
        const FString TempBundle=Attempt/TEXT("bundle.json"),TempMarker=Attempt/TEXT("commit.json");
        EStatus Result=WriteTemp(TempBundle,B,false,Fault);
        if(Result!=EStatus::Ok)return Failure(Result,TEXT("Candidate bundle write/flush/readback failed"));
        if(!Install(TempBundle,File(Target,TEXT("bundle.json"))))return Failure(EStatus::IoFailure,TEXT("Inactive bundle install failed"));
        if(Fault==EFaultPoint::BundleInstalled)return Failure(EStatus::InjectedFailure,TEXT("Stopped after inactive bundle installation"));
        FGeneration Verify;TArray<uint8> Installed;
        if(!Bundle(M,Target,Verify,&Installed)||Installed!=B)return Failure(EStatus::IoFailure,TEXT("Installed inactive bundle failed exact validation"));
        Result=WriteTemp(TempMarker,Utf8(MarkerBody(M,true)),true,Fault);
        if(Result!=EStatus::Ok)return Failure(Result,TEXT("Candidate marker write/flush/readback failed"));
        if(Fault==EFaultPoint::BeforeMarkerPublish)return Failure(EStatus::InjectedFailure,TEXT("Stopped before marker publication"));
        if(!Install(TempMarker,File(Target,TEXT("commit.json"))))
        {auto R=Failure(EStatus::IoFailure,TEXT("Marker publication failed; inspect before retry"));R.PublicationMayHaveSucceeded=true;return R;}
        if(Fault==EFaultPoint::AfterMarkerPublish)
        {auto R=Failure(EStatus::InjectedFailure,TEXT("Published marker, acknowledgement intentionally lost"));R.PublicationMayHaveSucceeded=true;return R;}
        const auto Published=Load(Validator);
        if(Published.Status!=EStatus::Ok||Published.Generation.GenerationId!=G.GenerationId)
        {auto R=Failure(EStatus::IoFailure,TEXT("Published generation readback failed; inspect before retry"));R.PublicationMayHaveSucceeded=true;return R;}
        return Receipt(M);
    }
};

FGenerationStore::FGenerationStore(const FString& Root,const FGuid& Profile,const FVersions& Supported)
    :Impl(MakeUnique<FImpl>())
{
    Impl->Profile=Profile;Impl->Supported=Supported;
    Impl->RequestValid=!Root.IsEmpty()&&Profile.IsValid()&&!Supported.Schema.IsEmpty()&&!Supported.ContentRules.IsEmpty()&&!Supported.Coordinates.IsEmpty();
    Impl->Directory=FPaths::ConvertRelativePathToFull(Root/Profile.ToString(EGuidFormats::DigitsWithHyphensLower));
    FPaths::NormalizeDirectoryName(Impl->Directory);
}
FGenerationStore::~FGenerationStore(){CloseWriter();}
EStatus FGenerationStore::OpenWriter()
{
    FScopeLock Lock(&Impl->Mutex);
    if(!Impl->RequestValid)return EStatus::InvalidRequest;if(Impl->Held())return EStatus::Ok;
#if PLATFORM_WINDOWS
    if(!IFileManager::Get().MakeDirectory(*Impl->Directory,true))return EStatus::IoFailure;
    Impl->Writer=::CreateFileW(*(Impl->Directory/TEXT("writer.lock")),GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(Impl->Writer==INVALID_HANDLE_VALUE)return ::GetLastError()==ERROR_SHARING_VIOLATION?EStatus::WriterBusy:EStatus::IoFailure;
    return EStatus::Ok;
#else
    return EStatus::UnsupportedPlatform;
#endif
}
void FGenerationStore::CloseWriter()
{
    FScopeLock Lock(&Impl->Mutex);
#if PLATFORM_WINDOWS
    if(Impl->Held()){::CloseHandle(Impl->Writer);Impl->Writer=INVALID_HANDLE_VALUE;}
#endif
}
FString FGenerationStore::GetProfileDirectory() const{return Impl->Directory;}
FLoadResult FGenerationStore::Load(const FPayloadValidator& Validator) const
{FScopeLock Lock(&Impl->Mutex);return Impl->Load(Validator);}
FCommitResult FGenerationStore::Commit(const FGeneration& Candidate,const FPayloadValidator& Validator,EFaultPoint Fault)
{FScopeLock Lock(&Impl->Mutex);const FGeneration Immutable=Candidate;return Impl->Commit(Immutable,Validator,Fault);}
FCommitResult FGenerationStore::Recover(ESlot Selected,const FPayloadValidator& Validator,EFaultPoint Fault)
{
    FScopeLock Lock(&Impl->Mutex);
    if(!Impl->Held())return Failure(EStatus::WriterBusy,TEXT("Explicit recovery requires writer lease"));
    if(Selected!=ESlot::A&&Selected!=ESlot::B)return Failure(EStatus::InvalidRequest,TEXT("Unknown selected backup slot"));
    if(uint8(Fault)>uint8(EFaultPoint::AfterMarkerPublish))return Failure(EStatus::InvalidRequest,TEXT("Unknown recovery IO boundary"));
    if(!Validator)return Failure(EStatus::InvalidRequest,TEXT("Recovery semantic validator is mandatory"));
    const auto I=Impl->Inspect();
    if(I.UnknownHead||!I.Head||I.Status==EStatus::Conflict||I.Head==TNumericLimits<uint64>::Max()||!I.Present[int32(Selected)])
        return Failure(EStatus::RecoveryRequired,TEXT("Cannot guess recovery generation or missing backup"));
    FGeneration Backup;FString Why;
    if(!Impl->Bundle(I.Markers[int32(Selected)],Selected,Backup)||!(Backup.Versions==Impl->Supported)||!Validator(Backup,Why))
        return Failure(EStatus::RecoveryRequired,TEXT("Explicitly selected backup is not a supported verified whole generation"));
    FGeneration Head;
    if(Impl->Bundle(I.Markers[int32(I.Slot)],I.Slot,Head)&&Head.RestoredFromGeneration==Backup.GenerationId
        &&Head.CanonicalPayload==Backup.CanonicalPayload&&Head.Versions==Backup.Versions)
        return Receipt(I.Markers[int32(I.Slot)],true);
    if(Selected==I.Slot)return Failure(EStatus::InvalidRequest,TEXT("Select an older whole backup, not the current head"));
    const FString Archive=Impl->Directory/TEXT("recovery")/(Decimal(I.Head+1)+TEXT("-")+FGuid::NewGuid().ToString(EGuidFormats::Digits));
    if(!IFileManager::Get().MakeDirectory(*Archive,true))return Failure(EStatus::IoFailure,TEXT("Cannot preserve recovery originals"));
    // Retain all four originals, including malformed/corrupt bytes, unchanged.
    for(ESlot Slot:{ESlot::A,ESlot::B})for(const TCHAR* Suffix:{TEXT("bundle.json"),TEXT("commit.json")})
    {
        const FString Source=Impl->File(Slot,Suffix);if(!IFileManager::Get().FileExists(*Source))continue;
        TArray<uint8> B;if(!Read(Source,B))return Failure(EStatus::IoFailure,TEXT("Cannot read bounded original recovery evidence; originals retained"));
        const FString Destination=Archive/FPaths::GetCleanFilename(Source);
        const EStatus W=Impl->WriteTemp(Destination,B,false,EFaultPoint::None);
        if(W!=EStatus::Ok)return Failure(EStatus::IoFailure,TEXT("Original evidence could not be durably archived"));
    }
    Backup.RestoredFromGeneration=Backup.GenerationId;Backup.GenerationId=I.Head+1;Backup.ParentGeneration=I.Head;
    auto R=Impl->Commit(Backup,Validator,Fault,true);R.RecoveryArchiveDirectory=Archive;return R;
}
FString FGenerationStore::Sha256(const TArray<uint8>& B)
{
#if PLATFORM_WINDOWS
    BCRYPT_ALG_HANDLE Algorithm=nullptr;BCRYPT_HASH_HANDLE Hash=nullptr;FString Result;
    if(::BCryptOpenAlgorithmProvider(&Algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)return {};
    DWORD Size=0,Got=0;TArray<uint8> Object;
    if(::BCryptGetProperty(Algorithm,BCRYPT_OBJECT_LENGTH,reinterpret_cast<PUCHAR>(&Size),sizeof(Size),&Got,0)>=0&&Got==sizeof(Size)&&Size>0)
    {
        Object.SetNumUninitialized(int32(Size));uint8 Digest[32];
        if(::BCryptCreateHash(Algorithm,&Hash,Object.GetData(),Size,nullptr,0,0)>=0
            &&::BCryptHashData(Hash,const_cast<PUCHAR>(B.GetData()),ULONG(B.Num()),0)>=0
            &&::BCryptFinishHash(Hash,Digest,sizeof(Digest),0)>=0)Result=BytesToHex(Digest,sizeof(Digest)).ToLower();
    }
    if(Hash)::BCryptDestroyHash(Hash);::BCryptCloseAlgorithmProvider(Algorithm,0);return Result;
#else
    return {};
#endif
}
}
