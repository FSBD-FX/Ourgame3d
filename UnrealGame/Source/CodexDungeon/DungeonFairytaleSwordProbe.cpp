#include "DungeonFairytaleSwordProbe.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonHUD.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonProofScreenshots.h"
#include "DungeonFairytaleSwordPrimary3V001.inl"
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
#include "HAL/PlatformTime.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
namespace
{
TArray<TSharedPtr<FJsonValue>> SwordXY(FVector2D P)
{return {MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y)};}
}
ADungeonFairytaleSwordProbe::ADungeonFairytaleSwordProbe(){PrimaryActorTick.bCanEverTick=true;}
void ADungeonFairytaleSwordProbe::BeginPlay()
{
    Super::BeginPlay();GIsDumpingMovie=0;WarmStart=FPlatformTime::Seconds();
    if(!FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Directory)||Directory.IsEmpty())
    {Finish(TEXT("missing_directory"));return;}
    Directory=FPaths::ConvertRelativePathToFull(Directory);
    TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Directory/TEXT("MovieFrame*.png")),true,false);
    if(Prior.Num()||IFileManager::Get().FileExists(*(Directory/TEXT("runtime-report.json")))
        ||IFileManager::Get().FileExists(*(Directory/TEXT("prewarm-viewport.png"))))
    {Stopped=true;UE_LOG(LogTemp,Error,TEXT("Sword trial refuses existing evidence"));FPlatformMisc::RequestExit(false);return;}
    IFileManager::Get().MakeDirectory(*Directory,true);
    GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Directory;
    if(auto C=UGameplayStatics::GetPlayerController(this,0))C->AddTickPrerequisiteActor(this);
    FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonFairytaleSwordProbe::ScreenshotProcessed);
}
void ADungeonFairytaleSwordProbe::Key(FKey Code,bool Down)
{
    if(Keys.FindRef(Code)==Down)return;
    if(auto C=UGameplayStatics::GetPlayerController(this,0))
    {
        C->InputKey(FInputKeyParams(Code,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(Code,Down);
        auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("key"),Code.ToString());R->SetBoolField(TEXT("down"),Down);
        R->SetNumberField(TEXT("wall_offset_s"),Started?FPlatformTime::Seconds()-CaptureStart:0.);
        Inputs.Add(MakeShared<FJsonValueObject>(R));
    }
}
void ADungeonFairytaleSwordProbe::ScreenshotProcessed()
{
    if(Stopped)return;
    if(Prewarm&&!Started)
    {
        if(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))<=8){Finish(TEXT("prewarm_file_missing"));return;}
        CaptureStart=FPlatformTime::Seconds();Started=true;GIsDumpingMovie=-1;return;
    }
    if(!Started)return;
    const double At=FPlatformTime::Seconds()-CaptureStart;Offsets.Add(MakeShared<FJsonValueNumber>(At));
    auto R=MakeShared<FJsonObject>();R->SetNumberField(TEXT("wall_offset_s"),At);
    auto C=UGameplayStatics::GetPlayerController(this,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
    auto G=GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto P=G?G->GetPlayerFighter():nullptr;
    R->SetBoolField(TEXT("hud"),H!=nullptr);R->SetBoolField(TEXT("player"),P!=nullptr);
    if(H)
    {
        const auto& D=H->GetFairytaleSwordDraw();R->SetBoolField(TEXT("active"),D.Active);
        R->SetBoolField(TEXT("supported"),D.Supported);R->SetBoolField(TEXT("texture_ready"),D.TextureReady);
        R->SetBoolField(TEXT("armor_preview"),D.ArmorPreview);R->SetBoolField(TEXT("armor_ready"),D.ArmorReady);R->SetBoolField(TEXT("armor_drawn"),D.ArmorDrawn);
        R->SetBoolField(TEXT("equipment_bound_mode"),D.EquipmentBoundMode);
        R->SetBoolField(TEXT("equipment_binding_valid"),D.EquipmentBindingValid);
        R->SetStringField(TEXT("equipment_binding_reason"),D.EquipmentBindingDiagnostic);
        auto BindingRecord=MakeShared<FJsonObject>();
        const auto& Skin=D.EquipmentBinding;
        BindingRecord->SetStringField(TEXT("run_guid"),Skin.RunGuid.ToString(EGuidFormats::Digits).ToLower());
        const auto BoundId=[&](const TCHAR* Field,uint64 Value)
        {BindingRecord->SetStringField(Field,FString::Printf(TEXT("%llu"),(unsigned long long)Value));};
        BoundId(TEXT("run_alias"),Skin.RunAlias);BoundId(TEXT("owner_id"),Skin.OwnerId);BoundId(TEXT("revision"),Skin.Revision);
        BindingRecord->SetNumberField(TEXT("active_slot"),Skin.ActiveSlot);
        BoundId(TEXT("weapon_instance_id"),Skin.WeaponInstanceId);BoundId(TEXT("weapon_version"),Skin.WeaponVersion);
        BoundId(TEXT("armor_instance_id"),Skin.ArmorInstanceId);BoundId(TEXT("armor_version"),Skin.ArmorVersion);
        BindingRecord->SetStringField(TEXT("weapon_content_id"),Skin.WeaponContentId);
        BindingRecord->SetStringField(TEXT("armor_content_id"),Skin.ArmorContentId);
        BindingRecord->SetStringField(TEXT("armor_kind"),D.EquipmentBindingValid
            ?(Skin.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor?TEXT("light_armor"):TEXT("no_armor")):TEXT("invalid"));
        R->SetObjectField(TEXT("equipment_binding"),BindingRecord);
        R->SetStringField(TEXT("draw_id"),FString::Printf(TEXT("%llu"),(unsigned long long)D.DrawId));
        R->SetStringField(TEXT("action_id"),FString::Printf(TEXT("%llu"),(unsigned long long)D.ActionId));
        R->SetStringField(TEXT("instance_id"),FString::Printf(TEXT("%llu"),(unsigned long long)D.InstanceId));
        R->SetNumberField(TEXT("sim"),D.SimulationTime);R->SetNumberField(TEXT("start"),D.ActionStart);
        R->SetNumberField(TEXT("active_at"),D.ActiveAt);R->SetNumberField(TEXT("active_end"),D.ActiveEnd);R->SetNumberField(TEXT("end"),D.ActionEnd);
        R->SetNumberField(TEXT("canvas_size"),D.CanvasSize);R->SetNumberField(TEXT("weapon_angle"),D.WeaponAngle);
        R->SetNumberField(TEXT("weapon_scale"),D.WeaponScale);R->SetNumberField(TEXT("weapon_width"),D.WeaponWidth);
        R->SetNumberField(TEXT("facing"),D.Facing);R->SetNumberField(TEXT("frame"),D.Frame);R->SetNumberField(TEXT("stage"),D.Stage);
        R->SetStringField(TEXT("clip"),D.Clip);R->SetStringField(TEXT("texture"),D.TexturePath);
        R->SetStringField(TEXT("weapon"),D.WeaponPath);R->SetStringField(TEXT("screenshot_request"),D.NativeScreenshotPath);
        R->SetArrayField(TEXT("root"),SwordXY(D.Root));R->SetArrayField(TEXT("grip"),SwordXY(D.Grip));R->SetArrayField(TEXT("grip_screen"),SwordXY(D.GripScreen));
        R->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());R->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());
        TArray<TSharedPtr<FJsonValue>> Stack;for(const auto& S:D.DrawStack)Stack.Add(MakeShared<FJsonValueString>(S));R->SetArrayField(TEXT("draw_stack"),Stack);
    }
    if(G&&P)
    {R->SetBoolField(TEXT("waiting"),G->bWaitingForStart);R->SetArrayField(TEXT("ground"),SwordXY(P->GetGroundPosition()));
        R->SetStringField(TEXT("run"),G->GetEquipmentView().RunGuid.ToString());R->SetStringField(TEXT("animation"),P->AnimationName);
        R->SetNumberField(TEXT("next_crit"),double(G->GetEquipmentView().NextCritDraw));
        R->SetBoolField(TEXT("melee_pending_primary"),P->GetMeleeCombatState().PendingPrimary);}
    Observations.Add(MakeShared<FJsonValueObject>(R));
}
void ADungeonFairytaleSwordProbe::Tick(float Dt)
{
    Super::Tick(Dt);if(Stopped)return;const double Wall=FPlatformTime::Seconds();
    if(!Started)
    {
        if(!Prewarm&&Wall-WarmStart>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}
        else if(Wall-WarmStart>17.)Finish(TEXT("prewarm_timeout"));return;
    }
    const double T=Wall-CaptureStart;
    const bool Third=DungeonFairytaleSwordPrimary3V001::Enabled();
    const bool Second=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2Preview"))
        ||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2ArmorPreview"));
    Key(EKeys::Enter,T<.12);
    if(Third)
    {
        Key(EKeys::J,(T>=1.10&&T<1.18)||(T>=1.60&&T<1.68)||(T>=2.16&&T<2.24)
            ||(T>=4.30&&T<4.38)||(T>=4.80&&T<4.88)||(T>=5.36&&T<5.44));
        Key(EKeys::A,T>=3.40&&T<3.48);
        if(T>=6.60)Finish();
    }
    else if(Second)
    {
        const bool Arc=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2ArcPreview"));
        // Arc trial presses .50s after the first request: safely inside the
        // existing final120ms window, without changing any kernel deadline.
        const double SecondRight=Arc?1.60:1.67,SecondLeft=Arc?4.80:4.87;
        Key(EKeys::J,(T>=1.1&&T<1.18)||(T>=SecondRight&&T<SecondRight+.08)||(T>=4.3&&T<4.38)||(T>=SecondLeft&&T<SecondLeft+.08));
        Key(EKeys::A,T>=3.4&&T<3.48);
        if(T>=6.6)Finish();
    }
    else
    {
        Key(EKeys::J,(T>=1.1&&T<1.18)||(T>=4.0&&T<4.08));
        Key(EKeys::A,T>=3.0&&T<3.08);
        if(T>=5.8)Finish();
    }
}
void ADungeonFairytaleSwordProbe::Finish(const FString& Failure)
{
    if(Stopped)return;Stopped=true;CaptureStop=FPlatformTime::Seconds();GIsDumpingMovie=0;
    Key(EKeys::Enter,false);Key(EKeys::J,false);Key(EKeys::A,false);
    const bool Flushed=FlushFastLosslessProofScreenshots();
    auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("schema"),TEXT("fairytale-sword-normal-input-capture-v1"));
    R->SetBoolField(TEXT("passed"),Failure.IsEmpty()&&Flushed&&Observations.Num()>0);R->SetStringField(TEXT("failure"),Failure);
    R->SetBoolField(TEXT("silent_video"),true);R->SetBoolField(TEXT("audio_recorded"),false);
    R->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);R->SetNumberField(TEXT("formal_complete_units"),0);
    const bool Primary2ArmorTrial=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2ArmorPreview"));
    const bool Second=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2Preview")) || Primary2ArmorTrial;
    const bool Third=DungeonFairytaleSwordPrimary3V001::Enabled();
    const bool ThirdArmor=DungeonFairytaleSwordPrimary3V001::ArmorEnabled();
    R->SetBoolField(TEXT("primary3_fit_trial"),Third);
    R->SetBoolField(TEXT("primary3_armor_trial"),ThirdArmor);
    R->SetBoolField(TEXT("primary2_fit_trial"),Second || Third);
    const bool BoundMode=FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordEquipmentBinding::CommandLineFlag);
    R->SetBoolField(TEXT("equipment_bound_rendering_candidate"),BoundMode);
    if(BoundMode)
        R->SetStringField(TEXT("scope"),TEXT("Same-draw read-only committed equipment resolver controls current sword and matching armor rendering candidates; Bound mode takes priority over art flags. Valid no-armor and actual LGT identity remain distinct; unsupported gear uses an explicit new-bell placeholder without sword or LGT substitution. This does not claim a normal acquisition/swap-flow native proof, automatic full three-stage coverage, visual/grasp/fullmotion/audio acceptance, full units or full Profile persistence; input schedule is unchanged and depends on the existing explicit trial flags"));
    else if(Third)
        R->SetStringField(TEXT("scope"),ThirdArmor
            ?TEXT("Native175 body with opt-in48 Primary3 source/body/armor textures, including integer-registered native176/177/178 armor; real six J requests traverse grounded kernelStages0/1/2, with Stage2 660ms. Existing Ready/Primary1 and native171 V003 Primary2 armor trials retained. No hit target, equipment identity, thumb/grasp, footlock, fullmotion or audio acceptance")
            :TEXT("Native175 six-body independent-sword fit under real six J requests traversing grounded kernelStages0/1/2, with Stage2 660ms. Existing Ready/Primary1 and native171 V003 Primary2 armor trials retained; Primary3 armor absent. No hit target, equipment identity, thumb/grasp, footlock, fullmotion or audio acceptance"));
    else
    R->SetStringField(TEXT("scope"),Primary2ArmorTrial
        ?TEXT("Native171 body with opt-in42 Primary2 body/armor-layer textures (7x6), including integer-registered native172/173/174 armor, and currentV003 independent-sword markers under real paired J/kernelStage1. Existing Ready/Primary1 trial retained. No hit target, complete armor states/equipment identity, three-stage/fullmotion, thumb/footlock or audio acceptance")
        :Second
        ?TEXT("Native169 six-body independent-sword fit under real paired J/kernelStage1. Matching armor only Ready/Primary1; Primary2 armor absent. No hit target, three-stage/fullmotion, thumb/footlock or audio acceptance")
        :TEXT("Selected source-body real Enter/A/J trial; optional matching Ready4 and grounded Primary1-six armor candidates. No hit target, complete armor states, equipment identity, three-stage, thumb, complete motion or audio acceptance"));
    R->SetArrayField(TEXT("observations"),Observations);R->SetArrayField(TEXT("normal_input_requests"),Inputs);
    auto T=MakeShared<FJsonObject>();T->SetNumberField(TEXT("capture_start_monotonic_s"),CaptureStart);
    T->SetNumberField(TEXT("capture_stop_monotonic_s"),CaptureStop);T->SetNumberField(TEXT("requested_video_wall_duration_s"),CaptureStop-CaptureStart);
    T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);R->SetObjectField(TEXT("capture_timing"),T);
    FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(R,Writer);
    if(!Directory.IsEmpty())FFileHelper::SaveStringToFile(Text,*(Directory/TEXT("runtime-report.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    FPlatformMisc::RequestExit(false);
}
void ADungeonFairytaleSwordProbe::EndPlay(const EEndPlayReason::Type Reason)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);GIsDumpingMovie=0;Super::EndPlay(Reason);}
