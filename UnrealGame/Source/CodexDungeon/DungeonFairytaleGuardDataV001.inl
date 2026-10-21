#pragma once
namespace DungeonFairytaleGuard
{
inline const TArray<FRow>& Profile()
{
 static const TArray<FRow> Rows=[]
 {
  TArray<FRow> A;
  {FRow R;
   R.Clip=EClip::Ready;R.NativeSourceId=209;R.SourcePoseApproved=true;
   R.StandingBasisFrame=0;R.StandingCrownY=49;R.StandingSoleY=463;R.StandingExtent=415.;
   R.RegistrationEvidenceSHA256=TEXT("32162f683dcccdd52f90dd94c5be667ca73d2b60be9e486dca4007809b730dfe");
   // Root may approve this exact partial trial with an independent retained registration record.
   R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("source-assets/production/fairytale-guard-v001/root-trial-registration-v001/approval.json");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_00.T_Guard209_Ready_00"),TEXT("54df5fe718a98e1568513193dbde479aff6fd393d623755feb77813cacb4e804"),FVector2D(235.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_01.T_Guard209_Ready_01"),TEXT("3fe3841442c48497d583f4c2622ef9c0bea3c1dc5082cf3b3d373760d547b0e7"),FVector2D(234.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_02.T_Guard209_Ready_02"),TEXT("301878a9ea8523275eb271240e1915620d772a9ec52d73efdc1123e1cd7b682c"),FVector2D(244.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_03.T_Guard209_Ready_03"),TEXT("90c21f1c417102e15f3e601d19351c8a40251e2317fb30b3d004d8d21e35e5b2"),FVector2D(236.,464.)});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::Wake;R.NativeSourceId=210;R.SourcePoseApproved=true;
   R.StandingBasisFrame=5;R.StandingCrownY=66;R.StandingSoleY=463;R.StandingExtent=398.;
   R.RegistrationEvidenceSHA256=TEXT("0493e1bddf65b7e0eb5a07196358426b2469123fb97356a149aa6f70c531beb6");
   // Root may approve this exact partial trial with an independent retained registration record.
   R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("source-assets/production/fairytale-guard-v001/root-trial-registration-v001/approval.json");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_00.T_Guard210_Wake_00"),TEXT("49fa77d9b1f1b3f2de3f69acb0aed401209605f484970954fde1e22ec2746faf"),FVector2D(242.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_01.T_Guard210_Wake_01"),TEXT("3ddc276f3e82e8d27c66f7299fda6faf56e84db204fb414b38a4004f48aa1860"),FVector2D(239.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_02.T_Guard210_Wake_02"),TEXT("d0d6bae6554fdaa7b33656dbdc5d74f7b985be7c3da21db1db5c518491671a03"),FVector2D(233.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_03.T_Guard210_Wake_03"),TEXT("6181bcee3202e5f6782ec5ed06981ad0e1858e1d03e598d2ffc3d5beab08274d"),FVector2D(239.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_04.T_Guard210_Wake_04"),TEXT("d930ff34a7c18cee11853286b374b1e161b54cb2c1ae06b8ac447ec0b00f2429"),FVector2D(237.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_05.T_Guard210_Wake_05"),TEXT("542529833eb98a976d3c146c25fa826020cdb6784a23a13982e82c56b650813d"),FVector2D(242.,464.)});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::AxeWindup;R.NativeSourceId=212;R.SourcePoseApproved=true;
   R.StandingBasisFrame=0;R.StandingCrownY=191;R.StandingSoleY=463;R.StandingExtent=273.;
   R.RegistrationEvidenceSHA256=TEXT("85c493cd3ef7c0abe29046d2b6a8acb185dcee061ed5ac3ceff772bb0ef54e9c");
   // Root may approve this exact partial trial with an independent retained registration record.
   R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("source-assets/production/fairytale-guard-v001/root-trial-registration-v001/approval.json");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_00.T_Guard212_AxeWindup_00"),TEXT("39bd95d59253f8f7a41a4dcc96359b12298af789f0b9a444b694e60c4fd544df"),FVector2D(242.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_01.T_Guard212_AxeWindup_01"),TEXT("ce00612d616abc65b1b27621a708ed27a54708f039c117aaf1bff002512f80a8"),FVector2D(241.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_02.T_Guard212_AxeWindup_02"),TEXT("42ef74e275602583ac3579f8ac3c6318a37d3dd26ecb24359bd55c082a6a9ea5"),FVector2D(253.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_03.T_Guard212_AxeWindup_03"),TEXT("2162193d81f25e6c5de2c332a6738828feb0cc04c8b24f935529dd24e136de42"),FVector2D(268.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_04.T_Guard212_AxeWindup_04"),TEXT("1b57280dd022c5fe4b1d6d7659f181115e9f50c2ae898a6d49e6a30c0026c95a"),FVector2D(273.,464.)});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_05.T_Guard212_AxeWindup_05"),TEXT("18a88f23b28f0e7971d4e897ca28b3c78ed7616ae6215e9319cc75c9c6dcf3b2"),FVector2D(292.,464.)});
   A.Add(MoveTemp(R));}
  {FRow R;R.Clip=EClip::Move;A.Add(MoveTemp(R));} // Explicit gap; never use Ready as a replacement.
  {FRow R;R.Clip=EClip::AxeFollow;A.Add(MoveTemp(R));} // Explicit gap; never use Ready as a replacement.
  {FRow R;R.Clip=EClip::StompWindup;A.Add(MoveTemp(R));} // Explicit gap; never use Ready as a replacement.
  {FRow R;R.Clip=EClip::StompFollow;A.Add(MoveTemp(R));} // Explicit gap; never use Ready as a replacement.
  {FRow R;R.Clip=EClip::Stunned;A.Add(MoveTemp(R));} // Explicit gap; never use Ready as a replacement.
  {FRow R;R.Clip=EClip::Death;A.Add(MoveTemp(R));} // Explicit gap; never use Ready as a replacement.
  {FRow R;R.Clip=EClip::InterruptedRecovery;A.Add(MoveTemp(R));} // Explicit gap; never use Ready as a replacement.
  return A;
 }();
 return Rows;
}
}
