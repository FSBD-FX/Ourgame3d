// Exact frozen artist surface registrations. These are not anatomical bones.
namespace DungeonFairytaleGuardMoveRigV001
{
namespace
{
FProfile MakeMoveProfile()
{
 FProfile P;
 P.ProfileId=TEXT("GuardMoveRig252_250_251_AuthorOwnHipC128_v001");
 P.ProfileSHA256=TEXT("03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51");
 P.SourceSnapshotSHA256=TEXT("a16a6a151ca0f6895c80ce108221bb3bed8f9c267c8016d142c18ed74f84cd94");
 P.RegistrationEvidenceSHA256=TEXT("d78bcbca8cd47caa781ee9a1bdcc1c25c5f9a3036be5d72dc2a2dcceb57feb9e");
 P.TrialApprovalRecord=TEXT("docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001/Root-limited-runtime-trial-approval-v001.json");
 P.SourceClosureVerified=true;P.TrialAllowed=true;P.FinalAccepted=false;
 {FSourcePart S;
  S.Component=EComponent::BodyRest;
  S.TexturePath=TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_BodyRest_v001.T_GuardMoveRig_BodyRest_v001");
  S.SourceSHA256=TEXT("402d6da9d41e88079b82d6fc5978badb8e19f86e1aac3d04d5320800220d4e2c");
  S.SourceRGBASHA256=TEXT("bac74c59c75cab64c8d36744d2e2ad513a270f208fd159dab01d87ff1ce71fb1");
  S.NativeBatchId=252;S.ComponentToRestScale=1.0;
  S.Markers.Add({TEXT("root"),FVector2D(250.,403.),FColor(255,227,144,255)});
  S.Markers.Add({TEXT("crown"),FVector2D(254.,137.),FColor(248,234,166,255)});
  S.Markers.Add({TEXT("near_hip_socket"),FVector2D(224.,404.),FColor(144,134,109,255)});
  S.Markers.Add({TEXT("far_hip_socket"),FVector2D(277.,400.),FColor(227,188,126,255)});
  P.Sources.Add(MoveTemp(S));}
 {FSourcePart S;
  S.Component=EComponent::NearThigh;
  S.TexturePath=TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_NearThigh_v001.T_GuardMoveRig_NearThigh_v001");
  S.SourceSHA256=TEXT("40d167afa7e61a64da7a7dacba3b2110cd28c384d3459ec1e81480cee049b460");
  S.SourceRGBASHA256=TEXT("32b1d0fac2fad4e97cd01289b172e43d183300c5de2124255feb5c6bd460f0c3");
  S.NativeBatchId=250;S.ComponentToRestScale=0.36;
  S.Markers.Add({TEXT("hip"),FVector2D(280.,126.),FColor(253,244,172,255)});
  S.Markers.Add({TEXT("knee"),FVector2D(214.,389.),FColor(158,143,119,255)});
  P.Sources.Add(MoveTemp(S));}
 {FSourcePart S;
  S.Component=EComponent::NearShin;
  S.TexturePath=TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_NearShin_v001.T_GuardMoveRig_NearShin_v001");
  S.SourceSHA256=TEXT("ad4b460374b9ac313f18be190845dab32ad0ece101c88b0b35dab73b050feeff");
  S.SourceRGBASHA256=TEXT("71c60a24f58fa28ec4746edc923163108f7d3346c6af3e3034ae762398b10351");
  S.NativeBatchId=250;S.ComponentToRestScale=0.36;
  S.Markers.Add({TEXT("knee"),FVector2D(268.,184.),FColor(218,189,136,255)});
  S.Markers.Add({TEXT("ankle"),FVector2D(260.,400.),FColor(227,194,132,255)});
  P.Sources.Add(MoveTemp(S));}
 {FSourcePart S;
  S.Component=EComponent::NearFoot;
  S.TexturePath=TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_NearFoot_v001.T_GuardMoveRig_NearFoot_v001");
  S.SourceSHA256=TEXT("bd6e8e5488891d62e7c6756eff9721152c3f99790b131f354496ca81010105a0");
  S.SourceRGBASHA256=TEXT("42cefad645d17f84cd0ef0b1fb1797fe50b9d08a471e3ef5b2dbee5eccb4e370");
  S.NativeBatchId=250;S.ComponentToRestScale=0.36;
  S.Markers.Add({TEXT("ankle"),FVector2D(216.,294.),FColor(254,242,170,255)});
  S.Markers.Add({TEXT("heel"),FVector2D(108.,445.),FColor(1,0,2,255)});
  S.Markers.Add({TEXT("toe"),FVector2D(420.,445.),FColor(1,0,0,255)});
  P.Sources.Add(MoveTemp(S));}
 {FSourcePart S;
  S.Component=EComponent::FarThigh;
  S.TexturePath=TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_FarThigh_v001.T_GuardMoveRig_FarThigh_v001");
  S.SourceSHA256=TEXT("5e2768723ba949b3f04bb07def025e008afe0161a8d149545a705d73c67e3ff4");
  S.SourceRGBASHA256=TEXT("7f71a1afe85db6ca5b6ef9ce9b1b653bc19b6d0ceb3f79c6f21a08198310674a");
  S.NativeBatchId=251;S.ComponentToRestScale=0.36;
  S.Markers.Add({TEXT("hip"),FVector2D(263.,124.),FColor(230,204,144,255)});
  S.Markers.Add({TEXT("knee"),FVector2D(228.,389.),FColor(177,155,119,255)});
  P.Sources.Add(MoveTemp(S));}
 {FSourcePart S;
  S.Component=EComponent::FarShin;
  S.TexturePath=TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_FarShin_v001.T_GuardMoveRig_FarShin_v001");
  S.SourceSHA256=TEXT("1dd04abe980ddc3018c15769105ea5f0513ac6336d61c4045f050f5e8e346dbc");
  S.SourceRGBASHA256=TEXT("b302ef32885c941d760ac10601ca584a91dc4a4f78c72f6b95856392fe687005");
  S.NativeBatchId=251;S.ComponentToRestScale=0.36;
  S.Markers.Add({TEXT("knee"),FVector2D(237.,193.),FColor(162,146,119,255)});
  S.Markers.Add({TEXT("ankle"),FVector2D(267.,407.),FColor(176,156,120,255)});
  P.Sources.Add(MoveTemp(S));}
 {FSourcePart S;
  S.Component=EComponent::FarFoot;
  S.TexturePath=TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_FarFoot_v001.T_GuardMoveRig_FarFoot_v001");
  S.SourceSHA256=TEXT("62eedb18f9de49bfdedf60205644da4e2c0d770a7aa943103315bb39de9ca5a9");
  S.SourceRGBASHA256=TEXT("16eb8d091f9cb0d0100717c4a4f444f05380954b8f8db33d0e3fb63537f2011f");
  S.NativeBatchId=251;S.ComponentToRestScale=0.36;
  S.Markers.Add({TEXT("ankle"),FVector2D(220.,258.),FColor(217,189,133,255)});
  S.Markers.Add({TEXT("heel"),FVector2D(105.,430.),FColor(13,11,18,255)});
  S.Markers.Add({TEXT("toe"),FVector2D(418.,442.),FColor(8,9,11,255)});
  P.Sources.Add(MoveTemp(S));}
 P.LayerOrder={EComponent::FarFoot,EComponent::FarShin,EComponent::FarThigh,EComponent::NearFoot,EComponent::NearShin,EComponent::NearThigh,EComponent::BodyRest};
 return P;
}
}
}
