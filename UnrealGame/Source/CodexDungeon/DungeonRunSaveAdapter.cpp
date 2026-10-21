#include "DungeonRunSaveAdapter.h"
#include "Misc/Paths.h"
#include <cmath>

namespace DungeonRunSaveAdapter
{
namespace
{
constexpr int32 MaxBytes=64*1024*1024;
constexpr int32 MaxStringUnits=1048576;
constexpr int32 MaxDepth=128;
bool Fail(FString& Diagnostic,const TCHAR* Message){Diagnostic=Message;return false;}
bool Exact(const FString& Left,const FString& Right)
{return Left.Equals(Right,ESearchCase::CaseSensitive);}
uint64 ClockBits(double Value){uint64 Bits=0;FMemory::Memcpy(&Bits,&Value,sizeof(Bits));return Bits;}
bool VersionsMatch(const Store::FVersions& Versions)
{
    // FVersions::operator== uses FString's case-insensitive equality. This
    // protocol's descriptors are ordinal, including in the Store callback.
    return Exact(Versions.Schema,CurrentVersions.Schema)
        &&Exact(Versions.ContentRules,CurrentVersions.ContentRules)
        &&Exact(Versions.Coordinates,CurrentVersions.Coordinates);
}
bool ContextValid(const FReadContext& Context,FString& Diagnostic)
{
    if(Context.Scope!=EScope::BoundDevelopmentRunV1)
        return Fail(Diagnostic,TEXT("Only real bound-development Run owners are supported; complete Profile owners are unavailable"));
    const auto& Directory=Context.ProfilesDirectory;
    if(!Context.ProfileId.IsValid()||Directory.IsEmpty()||Directory.Len()>32767||FPaths::IsRelative(Directory))
        return Fail(Diagnostic,TEXT("Run-only context requires a valid Profile and absolute bounded namespace directory"));
#if PLATFORM_WINDOWS
    // UE's IsRelative also calls F:child and /child rooted on Windows; both
    // depend on process drive state and therefore are not absolute contexts.
    const bool DriveAbsolute=Directory.Len()>=3&&FChar::IsAlpha(Directory[0])&&Directory[1]==':'&&Directory[2]=='/';
    const bool NetworkAbsolute=Directory.StartsWith(TEXT("//"),ESearchCase::CaseSensitive)
        &&Directory.Len()>2&&Directory[2]!='/'&&Directory.Find(TEXT("/"),ESearchCase::CaseSensitive,ESearchDir::FromStart,2)>2;
    if(!DriveAbsolute&&!NetworkAbsolute)return Fail(Diagnostic,TEXT("Windows namespace must use an absolute drive or network path"));
#endif
    for(TCHAR Unit:Directory)if(uint32(Unit)<32)
        return Fail(Diagnostic,TEXT("Namespace directory contains an embedded NUL or control character"));
    FString Normalized=Directory;FPaths::NormalizeDirectoryName(Normalized);
    if(!FPaths::CollapseRelativeDirectories(Normalized)||!Exact(Normalized,Directory)
        ||!Exact(FPaths::GetCleanFilename(Directory),FString(DirectoryName)))
        return Fail(Diagnostic,TEXT("Run-only namespace must be normalized and end exactly in BoundRunOnly-v1"));
    return true;
}
bool DiskMatches(const Store::FGenerationStore& Disk,const FReadContext& Context,FString& Diagnostic)
{
    if(!ContextValid(Context,Diagnostic))return false;
    // This spelling follows the actual Store implementation, independently of
    // the compact lowercase GUID representation used inside the payload.
    FString Expected=Context.ProfilesDirectory/Context.ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower);
    FPaths::NormalizeDirectoryName(Expected);
    return Exact(Disk.GetProfileDirectory(),Expected)
        ?true:Fail(Diagnostic,TEXT("Store profile directory does not match the isolated run-only context"));
}
bool HeaderValid(const Store::FGeneration& Generation,const FReadContext& Context,FString& Diagnostic)
{
    if(!ContextValid(Context,Diagnostic))return false;
    if(Generation.ProfileId!=Context.ProfileId||!Generation.GenerationId
        ||Generation.ParentGeneration>=Generation.GenerationId||Generation.RestoredFromGeneration!=0)
        return Fail(Diagnostic,TEXT("Run-only generation Profile/identity/parent or ordinary-publication scope is invalid"));
    if(!VersionsMatch(Generation.Versions))
        return Fail(Diagnostic,TEXT("Unknown or non-exact run-only schema/content/coordinate descriptors"));
    if(Generation.BuildId.IsEmpty()||Generation.BuildId.Len()>MaxStringUnits)
        return Fail(Diagnostic,TEXT("Build identity must be nonempty and within the counted string limit"));
    if(!Generation.RunSimulationTime.IsSet()||!std::isfinite(Generation.RunSimulationTime.GetValue())
        ||Generation.RunSimulationTime.GetValue()<0.)
        return Fail(Diagnostic,TEXT("Run-only generation requires its original finite nonnegative root clock"));
    return true;
}
bool RunMatches(const FDungeonRunSnapshot& Saved,const FReadContext& Context,FString& Diagnostic)
{
    // CodecV2 is a native-owner capability, never an implicit diskV1 upgrade.
    if(Saved.Schema!=1||Saved.Scope!=EDungeonRunScope::BoundDevelopmentV1)
        return Fail(Diagnostic,TEXT("BoundRunOnly-v1 refuses newer Run schema/scope; no implicit disk migration"));
    if(Context.ExpectedRunGuid.IsValid()&&Context.ExpectedRunGuid!=Saved.RunGuid)
        return Fail(Diagnostic,TEXT("Decoded Run does not match the caller's expected Run identity"));
    if(Context.ExpectedOwnerId&&Context.ExpectedOwnerId!=Saved.OwnerId)
        return Fail(Diagnostic,TEXT("Decoded Run does not match the caller's expected owner identity"));
    return true;
}

// Bounded direct byte writer. Metadata strings are counted native strings;
// valid Unicode is emitted literally, controls use lowercase \u00xx, and no
// FString terminator-based conversion can lose an embedded NUL.
class FWireWriter
{
public:
    TArray<uint8> Bytes;
    FString& Diagnostic;
    explicit FWireWriter(FString& Why):Diagnostic(Why){}
    bool Append(const uint8* Data,int32 Count)
    {
        if(Count<0||int64(Bytes.Num())+Count>MaxBytes)
            return Fail(Diagnostic,TEXT("Run-only canonical envelope exceeds 64 MiB"));
        if(Count)Bytes.Append(Data,Count);return true;
    }
    bool Byte(uint8 Value){return Append(&Value,1);}
    bool Literal(const ANSICHAR* Value)
    {return Append(reinterpret_cast<const uint8*>(Value),FCStringAnsi::Strlen(Value));}
    bool Scalar(uint32 Value)
    {
        uint8 Encoded[4];int32 Count=0;
        if(Value<=0x7f){Encoded[0]=uint8(Value);Count=1;}
        else if(Value<=0x7ff){Encoded[0]=uint8(0xc0|(Value>>6));Encoded[1]=uint8(0x80|(Value&63));Count=2;}
        else if(Value<=0xffff){Encoded[0]=uint8(0xe0|(Value>>12));Encoded[1]=uint8(0x80|((Value>>6)&63));Encoded[2]=uint8(0x80|(Value&63));Count=3;}
        else if(Value<=0x10ffff){Encoded[0]=uint8(0xf0|(Value>>18));Encoded[1]=uint8(0x80|((Value>>12)&63));Encoded[2]=uint8(0x80|((Value>>6)&63));Encoded[3]=uint8(0x80|(Value&63));Count=4;}
        else return Fail(Diagnostic,TEXT("Native metadata contains a non-Unicode scalar"));
        return Append(Encoded,Count);
    }
    bool Quoted(const FString& Text)
    {
        if(Text.Len()>MaxStringUnits)return Fail(Diagnostic,TEXT("Native metadata string exceeds counted unit limit"));
        if(!Byte('"'))return false;
        static constexpr ANSICHAR Hex[]="0123456789abcdef";
        for(int32 Index=0;Index<Text.Len();++Index)
        {
            uint32 Point=uint32(Text[Index]);
            if constexpr(sizeof(TCHAR)==2)
            {
                if(Point>=0xd800&&Point<=0xdbff)
                {
                    if(Index+1>=Text.Len())return Fail(Diagnostic,TEXT("Native metadata ends with an unpaired high surrogate"));
                    const uint32 Low=uint32(Text[++Index]);
                    if(Low<0xdc00||Low>0xdfff)return Fail(Diagnostic,TEXT("Native metadata contains an unpaired high surrogate"));
                    Point=0x10000+((Point-0xd800)<<10)+(Low-0xdc00);
                }
                else if(Point>=0xdc00&&Point<=0xdfff)return Fail(Diagnostic,TEXT("Native metadata contains an unpaired low surrogate"));
            }
            else if(Point>=0xd800&&Point<=0xdfff)return Fail(Diagnostic,TEXT("Native metadata contains a surrogate scalar"));
            if(Point=='"'||Point=='\\'){if(!Byte('\\')||!Byte(uint8(Point)))return false;}
            else if(Point<32)
            {const uint8 Escape[]={'\\','u','0','0',uint8(Hex[Point>>4]),uint8(Hex[Point&15])};if(!Append(Escape,6))return false;}
            else if(!Scalar(Point))return false;
        }
        return Byte('"');
    }
};
bool Prefix(const Store::FGeneration& Generation,FWireWriter& Writer)
{
    return Writer.Literal("{\"adapter\":\"bound-run-only-v1\",\"buildId\":")&&Writer.Quoted(Generation.BuildId)
        &&Writer.Literal(",\"generationId\":")&&Writer.Quoted(LexToString(Generation.GenerationId))
        &&Writer.Literal(",\"parentGeneration\":")&&Writer.Quoted(LexToString(Generation.ParentGeneration))
        &&Writer.Literal(",\"profileId\":")&&Writer.Quoted(Generation.ProfileId.ToString(EGuidFormats::Digits).ToLower())
        &&Writer.Literal(",\"run\":");
}
bool Suffix(const Store::FGeneration& Generation,const FDungeonRunSnapshot& Saved,FWireWriter& Writer)
{
    return Writer.Literal(",\"runGuid\":")&&Writer.Quoted(Saved.RunGuid.ToString(EGuidFormats::Digits).ToLower())
        &&Writer.Literal(",\"runSimulationTime\":")&&Writer.Quoted(FString::Printf(TEXT("%016llx"),ClockBits(Saved.SimulationTime)))
        &&Writer.Literal(",\"scope\":\"BoundDevelopmentRunV1\",\"versions\":{\"contentRules\":")&&Writer.Quoted(Generation.Versions.ContentRules)
        &&Writer.Literal(",\"coordinates\":")&&Writer.Quoted(Generation.Versions.Coordinates)
        &&Writer.Literal(",\"schema\":")&&Writer.Quoted(Generation.Versions.Schema)&&Writer.Literal("}}");
}

// Locate the nested Codec object without a permissive DOM or reencoding it.
// Bracket types, escaped string boundaries, raw controls and total wrapper
// depth are bounded here; the Codec independently validates every nested token,
// strict UTF-8, duplicates, unknown fields, canonical scalars and native owners.
bool RunObjectEnd(const TArray<uint8>& Payload,int32 Begin,int32& End,FString& Diagnostic)
{
    if(Begin<0||Begin>=Payload.Num()||Payload[Begin]!='{')
        return Fail(Diagnostic,TEXT("Canonical run-only envelope has no required Codec object"));
    uint8 Stack[MaxDepth];int32 Count=0;bool InString=false,Escaped=false;
    for(int32 Position=Begin;Position<Payload.Num();++Position)
    {
        const uint8 Value=Payload[Position];
        if(InString)
        {
            if(Value<32)return Fail(Diagnostic,TEXT("Unescaped ASCII control in nested Codec string"));
            if(Escaped){Escaped=false;continue;}
            if(Value=='\\'){Escaped=true;continue;}
            if(Value=='"')InString=false;
            continue;
        }
        if(Value=='"'){InString=true;continue;}
        if(Value=='{'||Value=='[')
        {
            // One additional level is the enclosing adapter object.
            if(Count+2>MaxDepth)return Fail(Diagnostic,TEXT("Run-only envelope exceeds depth 128"));
            Stack[Count++]=Value;continue;
        }
        if(Value=='}'||Value==']')
        {
            if(!Count||Stack[Count-1]!=(Value=='}'?'{':'['))
                return Fail(Diagnostic,TEXT("Nested Codec has mismatched container boundaries"));
            --Count;if(!Count){End=Position+1;return true;}
        }
    }
    return Fail(Diagnostic,TEXT("Nested Codec object or string is incomplete"));
}
bool Envelope(const Store::FGeneration& Generation,const FDungeonRunSnapshot& Saved,
    const TArray<uint8>& RunBytes,TArray<uint8>& Out,FString& Diagnostic)
{
    int32 End=0;if(!RunObjectEnd(RunBytes,0,End,Diagnostic)||End!=RunBytes.Num())
        return Fail(Diagnostic,TEXT("Codec object is not a complete bounded nested document"));
    FWireWriter Writer(Diagnostic);
    if(!Prefix(Generation,Writer)||!Writer.Append(RunBytes.GetData(),RunBytes.Num())||!Suffix(Generation,Saved,Writer))return false;
    Out=MoveTemp(Writer.Bytes);return true;
}
FReadResult ReadFailure(Store::EStatus Status,const FString& Diagnostic)
{FReadResult Result;Result.Status=Status;Result.Diagnostic=Diagnostic;return Result;}
} // anonymous namespace

bool MakeGeneration(const FDungeonRunSnapshot& Saved,const FWriteRequest& Request,
    Store::FGeneration& Out,FString& Diagnostic)
{
    Diagnostic.Reset();
    if(!ContextValid(Request.Context,Diagnostic))return false;
    if(!Request.RunGuid.IsValid()||Request.RunGuid!=Saved.RunGuid||!Request.OwnerId||Request.OwnerId!=Saved.OwnerId)
        return Fail(Diagnostic,TEXT("Write request must name the actual completed Run and owner"));
    if(!RunMatches(Saved,Request.Context,Diagnostic))return false;
    Store::FGeneration Candidate;Candidate.ProfileId=Request.Context.ProfileId;
    Candidate.GenerationId=Request.GenerationId;Candidate.ParentGeneration=Request.ParentGeneration;
    Candidate.Versions=CurrentVersions;Candidate.BuildId=Request.BuildId;Candidate.RunSimulationTime=Saved.SimulationTime;
    if(!HeaderValid(Candidate,Request.Context,Diagnostic))return false;
    TArray<uint8> RunBytes;
    // Encode independently performs the complete real Aggregate validation;
    // no test oracle or hand-picked owner subset participates in production.
    if(!DungeonRunSnapshotCodec::Encode(Saved,RunBytes,Diagnostic)
        ||!Envelope(Candidate,Saved,RunBytes,Candidate.CanonicalPayload,Diagnostic))return false;
    Out=MoveTemp(Candidate);Diagnostic.Reset();return true;
}
bool ValidateGeneration(const Store::FGeneration& Generation,const FReadContext& Context,
    FDungeonValidatedRun& Out,FString& Diagnostic)
{
    Diagnostic.Reset();if(!HeaderValid(Generation,Context,Diagnostic))return false;
    const auto& Payload=Generation.CanonicalPayload;
    if(Payload.IsEmpty()||Payload.Num()>MaxBytes)return Fail(Diagnostic,TEXT("Run-only envelope is empty or exceeds 64 MiB"));
    FWireWriter ExpectedPrefix(Diagnostic);
    if(!Prefix(Generation,ExpectedPrefix))return false;
    const int32 Begin=ExpectedPrefix.Bytes.Num();
    // Exact prefix and suffix make all wrapper fields mandatory, correctly
    // typed, uniquely named and canonical. Alternate escapes/order, whitespace,
    // duplicate (also escaped) keys and unknown keys cannot match these bytes.
    if(Payload.Num()<=Begin||FMemory::Memcmp(Payload.GetData(),ExpectedPrefix.Bytes.GetData(),Begin)!=0)
        return Fail(Diagnostic,TEXT("Canonical adapter prefix differs from the complete generation header"));
    int32 End=0;if(!RunObjectEnd(Payload,Begin,End,Diagnostic))return false;
    TArray<uint8> RunBytes;RunBytes.Append(Payload.GetData()+Begin,End-Begin);
    FDungeonValidatedRun Candidate;
    if(!DungeonRunSnapshotCodec::Decode(RunBytes,Candidate,Diagnostic))return false;
    if(!Candidate.IsValid()||!Candidate.Get())return Fail(Diagnostic,TEXT("Codec did not return a sealed complete Run"));
    const auto& Saved=*Candidate.Get();
    if(ClockBits(Generation.RunSimulationTime.GetValue())!=ClockBits(Saved.SimulationTime))
        return Fail(Diagnostic,TEXT("Enclosing generation clock does not exactly match decoded root clock bits"));
    if(!RunMatches(Saved,Context,Diagnostic))return false;
    FWireWriter ExpectedSuffix(Diagnostic);if(!Suffix(Generation,Saved,ExpectedSuffix))return false;
    if(Payload.Num()-End!=ExpectedSuffix.Bytes.Num()
        ||FMemory::Memcmp(Payload.GetData()+End,ExpectedSuffix.Bytes.GetData(),ExpectedSuffix.Bytes.Num())!=0)
        return Fail(Diagnostic,TEXT("Canonical adapter suffix differs from decoded Run identity/clock or exact descriptors"));
    Out=MoveTemp(Candidate);Diagnostic.Reset();return true;
}
Store::FCommitResult Commit(Store::FGenerationStore& Disk,const FDungeonRunSnapshot& Saved,
    const FWriteRequest& Request,Store::EFaultPoint Fault)
{
    FString Diagnostic;
    if(!DiskMatches(Disk,Request.Context,Diagnostic))
    {Store::FCommitResult Result;Result.Status=Store::EStatus::InvalidRequest;Result.Diagnostic=Diagnostic;return Result;}
    Store::FGeneration Candidate;
    if(!MakeGeneration(Saved,Request,Candidate,Diagnostic))
    {Store::FCommitResult Result;Result.Status=Store::EStatus::InvalidRequest;Result.Diagnostic=Diagnostic;return Result;}
    const Store::FPayloadValidator Validator=[&](const Store::FGeneration& Generation,FString& Why)
    {FDungeonValidatedRun Sealed;return ValidateGeneration(Generation,Request.Context,Sealed,Why);};
    // Store owns lease/fault/publication/head rules; preserve all of its receipts
    // and ambiguity flags rather than manufacturing an acknowledgement.
    return Disk.Commit(Candidate,Validator,Fault);
}
FReadResult Load(const Store::FGenerationStore& Disk,const FReadContext& Context,FLoadedRun& Out)
{
    FString Diagnostic;if(!DiskMatches(Disk,Context,Diagnostic))return ReadFailure(Store::EStatus::InvalidRequest,Diagnostic);
    FDungeonValidatedRun Sealed;
    const Store::FPayloadValidator Validator=[&](const Store::FGeneration& Generation,FString& Why)
    {return ValidateGeneration(Generation,Context,Sealed,Why);};
    auto Read=Disk.Load(Validator);FReadResult Result;
    Result.Status=Read.Status;Result.Slot=Read.Slot;Result.ObservedHeadGeneration=Read.ObservedHeadGeneration;Result.Diagnostic=Read.Diagnostic;
    if(Read.Status!=Store::EStatus::Ok)return Result;
    if(!Sealed.IsValid())
    {Result.Status=Store::EStatus::RecoveryRequired;Result.Diagnostic=TEXT("Selected head did not produce a sealed complete Run");return Result;}
    FLoadedRun Candidate;Candidate.Generation=MoveTemp(Read.Generation);Candidate.Run=MoveTemp(Sealed);
    Candidate.Slot=Read.Slot;Candidate.ObservedHeadGeneration=Read.ObservedHeadGeneration;
    Out=MoveTemp(Candidate);Result.Diagnostic.Reset();return Result;
}
FReadResult LoadAndPrepare(ADungeonGameMode& Game,const Store::FGenerationStore& Disk,
    const FReadContext& Context,FDungeonPreparedRun& OutPrepared,FLoadedRun& OutLoaded)
{
    FLoadedRun Loaded;auto Result=Load(Disk,Context,Loaded);
    if(Result.Status!=Store::EStatus::Ok)return Result;
    FDungeonPreparedRun Prepared;FString Diagnostic;
    if(!FDungeonRunInstaller::Prepare(Game,Loaded.Run,Prepared,Diagnostic))
    {Result.Status=Store::EStatus::ValidatorRejected;Result.Diagnostic=Diagnostic;return Result;}
    // Neither external output is published until the complete existing owner
    // group has actually prepared. Failure RAII owns only temporary resources.
    OutPrepared=MoveTemp(Prepared);OutLoaded=MoveTemp(Loaded);Result.Diagnostic.Reset();return Result;
}
}
