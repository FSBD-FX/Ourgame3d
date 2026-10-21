#include "DungeonFairytaleWalkProbe.h"
#include "DungeonHUD.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonFairytaleSwordWalkProfile.h"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "UnrealClient.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Misc/App.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
namespace
{
using FObject=TSharedPtr<FJsonObject>;
namespace Walk=DungeonFairytaleSwordWalkV001;
void Id(FObject O,const TCHAR* K,uint64 V){O->SetStringField(K,LexToString(V));}
TArray<TSharedPtr<FJsonValue>> XY(FVector2D P){return {MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y)};}
FString Bits(double V){uint64 B=0;FMemory::Memcpy(&B,&V,8);return FString::Printf(TEXT("%016llx"),(unsigned long long)B);}
const TCHAR* Phase(int32 S)
{
    static const TCHAR* Names[]={TEXT("start"),TEXT("baseline"),TEXT("pickup"),TEXT("light_ready"),TEXT("left_cycle"),TEXT("left_release_idle"),TEXT("left_combo"),TEXT("left_after_combo_walk"),TEXT("turn_idle"),TEXT("right_cycle"),TEXT("right_release_idle"),TEXT("right_combo"),TEXT("right_after_combo_walk"),TEXT("final_idle"),TEXT("complete")};
    return S>=0&&S<15?Names[S]:TEXT("invalid");
}
FObject ProfileFacts()
{
    auto O=MakeShared<FJsonObject>();const auto& P=Walk::Profile();
    O->SetBoolField(TEXT("configured"),Walk::Valid());O->SetBoolField(TEXT("source_closure_verified"),P.SourceClosureVerified);
    O->SetNumberField(TEXT("cycle_distance"),P.Gait.CycleDistance);O->SetNumberField(TEXT("cycle_seconds"),P.Gait.CycleSeconds);
    TArray<TSharedPtr<FJsonValue>> Durations,Frames;
    for(double V:P.Gait.Durations)Durations.Add(MakeShared<FJsonValueNumber>(V));O->SetArrayField(TEXT("durations"),Durations);
    for(const auto& F:P.Frames)
    {
        auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("measurements_supplied"),F.MeasurementsSupplied);
        R->SetStringField(TEXT("Body"),F.Body);R->SetStringField(TEXT("BodyRest"),F.BodyRest);R->SetStringField(TEXT("NearArmWithoutHand"),F.NearArmWithoutHand);
        R->SetStringField(TEXT("HelmetForeground"),F.HelmetForeground);R->SetStringField(TEXT("NearHand"),F.NearHand);
        R->SetStringField(TEXT("ShoulderFar"),F.ShoulderFar);R->SetStringField(TEXT("Chest"),F.Chest);R->SetStringField(TEXT("ShoulderNear"),F.ShoulderNear);
        R->SetArrayField(TEXT("root"),XY(F.Marker.Root));R->SetArrayField(TEXT("grip"),XY(F.Marker.Grip));R->SetArrayField(TEXT("axis"),XY(F.Marker.Axis));
        Frames.Add(MakeShared<FJsonValueObject>(R));
    }
    O->SetArrayField(TEXT("frames"),Frames);return O;
}
}
struct FDungeonFairytaleWalkProofState
{
    FString Directory;FGuid Run;
    TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
    TMap<FKey,bool> Keys;FKey PulseKey;
    uint64 OwnerId=0,RestartSerial=0,SwordId=0,LightId=0,SourceId=0,InitialOperation=0,InitialOperations=0,LightVersion=0,QueuedAttack=0;
    int32 Step=0,IdleSeen[15]={},Masks[2]={},ComboMasks[2][3]={},PostWalkSeen[2]={};
    uint64 AttackIds[2][3]={};double Distances[2]={},PostDistances[2]={};
    bool Stopped=false,Prewarm=false,Started=false,FinishOnFrame=false,Complete=false;
    double Warm=0.,Start=0.,Stop=0.,StepStart=0.,ReleaseAt=0.,NeutralUntil=0.;
    TSharedPtr<FJsonObject> Report=MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> Observations,Offsets,Inputs,Steps;
    void Key(FKey K,bool Down)
    {
        if(Keys.FindRef(K)==Down)return;
        if(auto C=Controller.Get())
        {
            C->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);
            auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("key"),K.ToString());R->SetBoolField(TEXT("down"),Down);
            R->SetNumberField(TEXT("wall_offset_s"),Started?FPlatformTime::Seconds()-Start:0.);
            R->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);Inputs.Add(MakeShared<FJsonValueObject>(R));
        }
    }
    bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
    bool Pulse(FKey K){if(!CanPulse())return false;Key(K,true);PulseKey=K;ReleaseAt=FPlatformTime::Seconds()+.08;return true;}
    void Next(int32 S)
    {
        Step=S;StepStart=FPlatformTime::Seconds();auto R=MakeShared<FJsonObject>();R->SetNumberField(TEXT("step"),S);R->SetStringField(TEXT("phase"),Phase(S));
        R->SetNumberField(TEXT("wall_offset_s"),StepStart-Start);R->SetNumberField(TEXT("sim"),Game->GetSimulationTime());Steps.Add(MakeShared<FJsonValueObject>(R));
    }
    void Finish(const FString& Why=FString())
    {
        if(Stopped)return;Stopped=true;Stop=FPlatformTime::Seconds();GIsDumpingMovie=0;
        for(FKey K:{EKeys::Enter,EKeys::E,EKeys::A,EKeys::D,EKeys::J})Key(K,false);
        const bool Flushed=FlushFastLosslessProofScreenshots();
        Report->SetStringField(TEXT("schema"),TEXT("fairytale-walk-native-input-flow-v1"));Report->SetBoolField(TEXT("passed"),Why.IsEmpty()&&Complete&&Flushed&&!Observations.IsEmpty());Report->SetStringField(TEXT("failure"),Why);
        Id(Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Report->SetBoolField(TEXT("flow_complete"),Complete);
        Report->SetBoolField(TEXT("native_async_capture_requested"),true);Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);Report->SetBoolField(TEXT("capture_stop_before_flush"),true);
        Report->SetNumberField(TEXT("flush_completed_monotonic_s"),FPlatformTime::Seconds());Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);Report->SetNumberField(TEXT("formal_complete_units"),0);
        Report->SetBoolField(TEXT("wall_stop_visually_recorded"),false);Report->SetBoolField(TEXT("art_accepted"),false);Report->SetBoolField(TEXT("game_tick_called_manually"),false);
        Report->SetStringField(TEXT("scope"),TEXT("Actual Enter/E single QA LGT commit, held A/D each full physical cycle/six phases, release Idle, two distinct native J three-stage chains and real resumed Walk. Same actual SWD/LGT instances, original native viewport CRC/FIFO capture. No wall-stop visual recording, formal loot/reward/full equipment action/art/audio/save/full unit acceptance."));
        Id(Report,TEXT("sword_id"),SwordId);Id(Report,TEXT("light_id"),LightId);Id(Report,TEXT("light_version"),LightVersion);Id(Report,TEXT("source_id"),SourceId);
        Id(Report,TEXT("initial_operation"),InitialOperation);Id(Report,TEXT("initial_operation_count"),InitialOperations);Id(Report,TEXT("restart_serial"),Game.IsValid()?Game->GetRunRestartSerial():0);
        Report->SetArrayField(TEXT("observations"),Observations);Report->SetArrayField(TEXT("normal_input_requests"),Inputs);Report->SetArrayField(TEXT("phasechecks"),Steps);
        auto T=MakeShared<FJsonObject>();T->SetNumberField(TEXT("capture_start_monotonic_s"),Start);T->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);
        T->SetNumberField(TEXT("requested_video_wall_duration_s"),Started?Stop-Start:0.);T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),T);Report->SetNumberField(TEXT("duration_s"),Started?Stop-Start:0.);
        FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),W);const FString Path=Directory/TEXT("runtime-report.json");
        const bool Written=!Directory.IsEmpty()&&!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
        if(!Why.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Fairytale Walk proof failed: %s"),*Why);
        FPlatformMisc::RequestExitWithStatus(false,Why.IsEmpty()&&Complete&&Written&&Flushed&&!Observations.IsEmpty()?0:3);
    }
    bool Need(bool V,const FString& Why){if(!V)Finish(Why);return V;}
    void Observe()
    {
        if(Stopped)return;
        if(Prewarm&&!Started){if(!Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Native prewarm missing")))return;Start=StepStart=FPlatformTime::Seconds();Started=true;GIsDumpingMovie=-1;return;}
        if(!Started)return;auto G=Game.Get();auto H=HUD.Get();auto P=G?G->GetPlayerFighter():nullptr;
        if(!Need(G&&H&&P,TEXT("Native player/GameMode/HUD absent")))return;
        const auto& V=G->GetEquipmentView();if(!Need(V.Bound&&V.ActiveSlot>=0&&V.ActiveSlot<2,TEXT("Native draw has no valid bound active slot")))return;const auto& D=H->GetFairytaleSwordDraw();const auto& A=P->GetMeleeCombatState().Action;
        FDungeonCompletedGroundMotion M;const bool Motion=P->QueryCompletedGroundMotion(M);
        auto R=MakeShared<FJsonObject>();const double Offset=FPlatformTime::Seconds()-Start;Offsets.Add(MakeShared<FJsonValueNumber>(Offset));
        R->SetNumberField(TEXT("wall_offset_s"),Offset);R->SetNumberField(TEXT("flow_step"),Step);R->SetStringField(TEXT("flow_phase"),Phase(Step));
        R->SetNumberField(TEXT("sim"),G->GetSimulationTime());R->SetStringField(TEXT("simulation_bits"),Bits(G->GetSimulationTime()));Id(R,TEXT("draw_id"),D.DrawId);
        R->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits).ToLower());Id(R,TEXT("owner_id"),V.OwnerId);Id(R,TEXT("sword_id"),V.Slots[V.ActiveSlot].InstanceId);Id(R,TEXT("light_id"),V.Slots[2].InstanceId);Id(R,TEXT("light_version"),V.Slots[2].Version);
        Id(R,TEXT("next_operation"),V.NextOperationId);const auto I=G->GetEquipmentInventoryState();Id(R,TEXT("operations"),I?I->Operations.size():0);
        R->SetBoolField(TEXT("active"),D.Active);R->SetBoolField(TEXT("supported"),D.Supported);R->SetBoolField(TEXT("texture_ready"),D.TextureReady);R->SetBoolField(TEXT("armor_ready"),D.ArmorReady);R->SetBoolField(TEXT("armor_drawn"),D.ArmorDrawn);
        R->SetBoolField(TEXT("binding_valid"),D.EquipmentBindingValid);R->SetStringField(TEXT("clip"),D.Clip);R->SetNumberField(TEXT("frame"),D.Frame);R->SetNumberField(TEXT("facing"),D.Facing);R->SetNumberField(TEXT("stage"),D.Stage);Id(R,TEXT("action_id"),D.ActionId);Id(R,TEXT("instance_id"),D.InstanceId);
        R->SetStringField(TEXT("texture"),D.TexturePath);R->SetStringField(TEXT("weapon"),D.WeaponPath);R->SetNumberField(TEXT("weapon_scale"),D.WeaponScale);R->SetNumberField(TEXT("weapon_angle"),D.WeaponAngle);R->SetNumberField(TEXT("weapon_width"),D.WeaponWidth);R->SetNumberField(TEXT("canvas_size"),D.CanvasSize);
        R->SetStringField(TEXT("animation"),P->AnimationName);R->SetStringField(TEXT("animation_time_bits"),Bits(P->AnimationTime));R->SetArrayField(TEXT("ground"),XY(P->GetGroundPosition()));R->SetArrayField(TEXT("root"),XY(D.Root));R->SetArrayField(TEXT("grip"),XY(D.Grip));R->SetArrayField(TEXT("grip_screen"),XY(D.GripScreen));
        R->SetBoolField(TEXT("walk_pose"),D.WalkPose);R->SetNumberField(TEXT("walk_phase"),D.WalkPhase);R->SetNumberField(TEXT("cycle_distance"),D.WalkCycleDistance);R->SetBoolField(TEXT("ordinary_walk_owner"),P->IsOrdinaryGroundWalkPose());
        R->SetBoolField(TEXT("pending_equipment"),V.Action.Active);R->SetNumberField(TEXT("equipment_start"),V.Action.Start);R->SetNumberField(TEXT("equipment_deadline"),V.Action.Deadline);Id(R,TEXT("pending_instance_id"),V.Action.InstanceId);
        R->SetBoolField(TEXT("melee_active"),A.Active);R->SetBoolField(TEXT("melee_pending"),P->GetMeleeCombatState().PendingPrimary);Id(R,TEXT("melee_attack_id"),A.AttackId);Id(R,TEXT("melee_weapon_id"),A.WeaponInstanceId);R->SetNumberField(TEXT("melee_stage"),A.Stage);R->SetNumberField(TEXT("melee_facing"),A.Facing);R->SetNumberField(TEXT("action_start"),A.Start);R->SetNumberField(TEXT("active_end"),A.ActiveEnd);R->SetNumberField(TEXT("action_end"),A.End);R->SetNumberField(TEXT("owner_pose_frame"),P->GetPrimaryPoseFrame());
        R->SetBoolField(TEXT("held_A"),Controller->IsInputKeyDown(EKeys::A));R->SetBoolField(TEXT("held_D"),Controller->IsInputKeyDown(EKeys::D));R->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());R->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());
        TArray<TSharedPtr<FJsonValue>> Stack;for(const auto& Path:D.DrawStack)Stack.Add(MakeShared<FJsonValueString>(Path));R->SetArrayField(TEXT("draw_stack"),Stack);
        TArray<TSharedPtr<FJsonValue>> Rendered,ArmorPaths;
        for(const auto& Path:H->GetRenderedPlayerDrawStack())Rendered.Add(MakeShared<FJsonValueString>(Path));
        for(const auto& Path:H->GetRenderedArmorLayerPaths())ArmorPaths.Add(MakeShared<FJsonValueString>(Path));
        R->SetArrayField(TEXT("rendered_player_stack"),Rendered);R->SetArrayField(TEXT("rendered_armor_paths"),ArmorPaths);
        R->SetBoolField(TEXT("rendered_armor_used"),H->GetRenderedArmorLayersUsed());
        if(!Need(H->GetRenderedPlayerDrawStack()==D.DrawStack,TEXT("Actual rendered player stack differs from same-draw record")))return;
        auto Q=MakeShared<FJsonObject>();Q->SetBoolField(TEXT("query_ok"),Motion);Q->SetBoolField(TEXT("published"),M.Published);Q->SetBoolField(TEXT("grounded"),M.Grounded);Q->SetBoolField(TEXT("ordinary_eligible"),M.OrdinaryEligible);Q->SetBoolField(TEXT("had_move_intent"),M.HadMoveIntent);
        Q->SetNumberField(TEXT("from_time"),M.FromTime);Q->SetNumberField(TEXT("to_time"),M.ToTime);Q->SetNumberField(TEXT("accepted_distance"),M.AcceptedDistance);Q->SetNumberField(TEXT("walk_distance"),M.WalkDistance);Q->SetArrayField(TEXT("from"),XY(M.From));Q->SetArrayField(TEXT("to"),XY(M.To));Id(Q,TEXT("owner_id"),M.OwnerId);R->SetObjectField(TEXT("motion"),Q);
        if(!Need(D.Active&&D.TextureReady&&D.EquipmentBindingValid&&!H->GetInterfaceVisible()&&H->GetRenderedTextDrawCalls()==0&&D.SimulationTime==G->GetSimulationTime(),TEXT("Native draw resources/binding/UI/clock failed")))return;
        const bool Light=LightId&&V.Slots[2].InstanceId==LightId;
        if(Light&&(!Need(D.ArmorDrawn&&D.ArmorReady&&!D.WeaponPath.IsEmpty()&&D.InstanceId==SwordId,TEXT("Same committed LGT/SWD lost armor/weapon layers"))))return;
        const bool Idle=D.Clip==TEXT("sword_ready_idle")&&P->AnimationName==TEXT("idle")&&!A.Active&&!V.Action.Active&&!P->GetMeleeCombatState().PendingPrimary;
        if(Idle&&Step>=0&&Step<15)++IdleSeen[Step];
        if(D.Clip==TEXT("sword_walk"))
        {
            if(!Need(Light&&D.WalkPose&&P->IsOrdinaryGroundWalkPose()&&Motion&&M.Grounded&&M.OrdinaryEligible&&M.HadMoveIntent&&M.WalkDistance>0.&&M.ToTime==G->GetSimulationTime()&&D.Frame>=0&&D.Frame<6&&D.Stage==-1&&!A.Active,TEXT("Walk not corroborated by completed native motion")))return;
            const auto* F=Walk::Find(D.Frame);TArray<FString> Expected={F->BodyRest,F->ShoulderFar,F->Chest,F->NearArmWithoutHand,F->ShoulderNear,F->HelmetForeground,D.WeaponPath,F->NearHand};
            if(!Need(D.DrawStack==Expected&&D.TexturePath==F->Body&&H->GetRenderedPlayerDrawStack()==Expected
                &&H->GetRenderedArmorLayersUsed()&&H->GetRenderedArmorLayerPaths()==TArray<FString>{F->ShoulderFar,F->Chest,F->ShoulderNear},TEXT("Walk exact seven body/armor layers plus sword differ")))return;
            const int32 Side=D.Facing<0?0:1;
            if(Step==4||Step==9){Masks[Side]|=1<<D.Frame;Distances[Side]+=M.WalkDistance;}
            if(Step==7||Step==12){++PostWalkSeen[Side];PostDistances[Side]+=M.WalkDistance;}
        }
        if(Step==6||Step==11)
        {
            if(A.Active)
            {
                const int32 Side=Step==6?0:1,Stage=int32(A.Stage);
                if(!Need(Stage>=0&&Stage<3&&D.Facing==(Side?1:-1)&&A.Facing==D.Facing&&D.ActionId==A.AttackId&&A.WeaponInstanceId==SwordId&&D.Frame==P->GetPrimaryPoseFrame()&&D.Frame>=0&&D.Frame<6&&D.Clip==FString::Printf(TEXT("sword_primary_%d"),Stage+1),TEXT("Actual J chain owner/facing/pose/frame mismatch")))return;
                if(!AttackIds[Side][Stage])AttackIds[Side][Stage]=A.AttackId;
                if(!Need(AttackIds[Side][Stage]==A.AttackId,TEXT("Repeated attack used for same side/stage")))return;
                ComboMasks[Side][Stage]|=1<<D.Frame;
            }
        }
        Observations.Add(MakeShared<FJsonValueObject>(R));if(FinishOnFrame)Finish();
    }
    bool ComboComplete(int32 Side)const{for(int32 S=0;S<3;++S)if(ComboMasks[Side][S]!=63||!AttackIds[Side][S])return false;return true;}
    void Tick(ADungeonFairytaleWalkProbe& Actor)
    {
        if(Stopped)return;const double Now=FPlatformTime::Seconds();
        auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
        if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){Game=G;Controller=C;HUD=H;C->AddTickPrerequisiteActor(&Actor);return;}
        if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.034;}
        if(!Started){if(!Prewarm&&Now-Warm>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}else if(Now-Warm>17.)Finish(TEXT("Native prewarm timeout"));return;}
        if(!Need(Now-Start<45.&&Now-StepStart<12.,TEXT("Native Walk scene/input timeout")))return;if(FinishOnFrame)return;
        auto P=G?G->GetPlayerFighter():nullptr;
        if(!Need(G&&C&&H&&P&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&C->GetPawn()==P&&!P->bDead&&!G->bGameOver,TEXT("Native authoritative player world changed")))return;
        const auto& V=G->GetEquipmentView();const auto I=G->GetEquipmentInventoryState();
        if(!Need(I&&V.Bound&&V.ActiveSlot>=0&&V.ActiveSlot<2,TEXT("Actual bound inventory missing")))return;
        if(!Run.IsValid()){Run=V.RunGuid;OwnerId=V.OwnerId;RestartSerial=G->GetRunRestartSerial();SwordId=V.Slots[V.ActiveSlot].InstanceId;InitialOperation=V.NextOperationId;InitialOperations=I->Operations.size();if(!Need(!I->Armor&&P->WeaponId==TEXT("WPN-SWD-001"),TEXT("Actual unarmored SWD startup required")))return;}
        if(!Need(V.RunGuid==Run&&V.OwnerId==OwnerId&&G->GetRunRestartSerial()==RestartSerial&&V.Slots[V.ActiveSlot].InstanceId==SwordId,TEXT("Run/sword identity changed")))return;
        if(Step>=3&&!Need(I->Armor==LightId&&V.Slots[2].Version==LightVersion&&V.NextOperationId==InitialOperation+1&&I->Operations.size()==InitialOperations+1,TEXT("Actual single LGT commit/instance/version changed")))return;
        const auto& Melee=P->GetMeleeCombatState();const auto& A=Melee.Action;
        switch(Step)
        {
        case 0:if(G->bWaitingForStart){if(CanPulse())Pulse(EKeys::Enter);}else Next(1);break;
        case 1:if(IdleSeen[1]>=3&&CanPulse())
            {DungeonEquipmentInventory::FItem Item;Item.ContentId="ARM-LGT-001";const auto R=G->RegisterEquipmentSource(TEXT("qa.walk.native.light.v1"),Item,P->GetGroundPosition()+FVector2D(24.,0.),true);
                if(!Need(R.Ok()&&!R.Replayed,TEXT("Actual public LGT source registration failed")))return;SourceId=R.SourceId;LightId=R.InstanceId;if(!Need(V.SelectedSourceId==SourceId,TEXT("Registered LGT not actual nearest selected source")))return;Pulse(EKeys::E);Next(2);}break;
        case 2:if(!V.Action.Active&&I->Armor==LightId){LightVersion=V.Slots[2].Version;Next(3);}break;
        case 3:if(IdleSeen[3]>=3&&CanPulse()){Key(EKeys::A,true);Next(4);}break;
        case 4:if(Masks[0]==63&&Distances[0]>=Walk::Profile().Gait.CycleDistance){Key(EKeys::A,false);Next(5);}break;
        case 5:if(IdleSeen[5]>=3&&CanPulse()){Pulse(EKeys::J);Next(6);}break;
        case 6:case 11:
        {
            const int32 Side=Step==6?0:1;
            if(A.Active&&A.Stage<2&&A.AttackId!=QueuedAttack&&G->GetSimulationTime()>=A.ActiveEnd&&G->GetSimulationTime()>=A.End-.10&&CanPulse())
                {if(Pulse(EKeys::J))QueuedAttack=A.AttackId;}
            if(!A.Active&&ComboComplete(Side)&&!Melee.PendingPrimary&&G->GetSimulationTime()>=A.End+.46&&CanPulse())
                {Key(Side?EKeys::D:EKeys::A,true);Next(Side?12:7);}break;
        }
        case 7:if(PostWalkSeen[0]>=3&&PostDistances[0]>=20.){Key(EKeys::A,false);Next(8);}break;
        case 8:if(IdleSeen[8]>=3&&CanPulse()){Key(EKeys::D,true);Next(9);}break;
        case 9:if(Masks[1]==63&&Distances[1]>=Walk::Profile().Gait.CycleDistance){Key(EKeys::D,false);Next(10);}break;
        case 10:if(IdleSeen[10]>=3&&CanPulse()){Pulse(EKeys::J);Next(11);}break;
        case 12:if(PostWalkSeen[1]>=3&&PostDistances[1]>=20.){Key(EKeys::D,false);Next(13);}break;
        case 13:if(IdleSeen[13]>=3){TSet<uint64> Unique;for(int32 Side=0;Side<2;++Side)for(int32 S=0;S<3;++S)Unique.Add(AttackIds[Side][S]);if(!Need(Unique.Num()==6,TEXT("Six distinct actual J attacks absent")))return;Complete=true;Next(14);FinishOnFrame=true;}break;
        default:Finish(TEXT("Unknown native Walk proof phase"));break;
        }
    }
};
void FDungeonFairytaleWalkProofDeleter::operator()(FDungeonFairytaleWalkProofState* V)const{delete V;}
ADungeonFairytaleWalkProbe::ADungeonFairytaleWalkProbe(){PrimaryActorTick.bCanEverTick=true;}
ADungeonFairytaleWalkProbe::~ADungeonFairytaleWalkProbe()=default;
void ADungeonFairytaleWalkProbe::BeginPlay()
{
    Super::BeginPlay();Proof.Reset(new FDungeonFairytaleWalkProofState());Proof->Warm=FPlatformTime::Seconds();GIsDumpingMovie=0;
    FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);
    if(Proof->Directory.IsEmpty()||FPaths::IsRelative(Proof->Directory)){Proof->Directory.Reset();Proof->Finish(TEXT("Absolute unused native proof directory required"));return;}
    Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);
    TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("MovieFrame*.png")),true,false);
    if(Prior.Num()||IFileManager::Get().FileExists(*(Proof->Directory/TEXT("runtime-report.json")))||IFileManager::Get().FileExists(*(Proof->Directory/TEXT("prewarm-viewport.png")))){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}
    IFileManager::Get().MakeDirectory(*Proof->Directory,true);Proof->Report->SetObjectField(TEXT("compiled_walk_profile"),ProfileFacts());
    if(!Proof->Need(Walk::Valid(),TEXT("Compiled Walk profile/source closure/measurements/48paths unconfigured or invalid")))return;
    for(const TCHAR* Flag:{TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture")})
        if(!Proof->Need(FParse::Param(FCommandLine::Get(),Flag),FString(TEXT("Required native Walk flag absent: "))+Flag))return;
    if(!Proof->Need(!FApp::UseFixedTimeStep(),TEXT("Actual ordinary pacing required")))return;
    GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;
    FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonFairytaleWalkProbe::ScreenshotProcessed);
}
void ADungeonFairytaleWalkProbe::ScreenshotProcessed(){if(Proof)Proof->Observe();}
void ADungeonFairytaleWalkProbe::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonFairytaleWalkProbe::EndPlay(const EEndPlayReason::Type R)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("Native world ended before Walk proof completion"));GIsDumpingMovie=0;Super::EndPlay(R);}
