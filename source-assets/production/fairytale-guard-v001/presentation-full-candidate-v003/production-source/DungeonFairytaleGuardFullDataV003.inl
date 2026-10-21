#pragma once
namespace DungeonFairytaleGuardFullV003
{
inline const TArray<FRow>& ProfileFull()
{
 static const TArray<FRow> Rows=[]
 {
  TArray<FRow> A;
  {FRow R;
   R.Clip=EClip::Dormant;R.NativeSourceId=210;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.AliasTarget=EClip::Wake;R.AliasFrame=0; // Explicit logical row, zero extra pixels.
   // Root must explicitly approve this full-mode alias row and the Wake target row.
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::Wake;R.NativeSourceId=210;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=5;R.StandingCrownY=66;R.StandingSoleY=463;R.StandingExtent=398.;
   R.RegistrationEvidenceSHA256=TEXT("0493e1bddf65b7e0eb5a07196358426b2469123fb97356a149aa6f70c531beb6");
   R.SourceIndexSHA256=TEXT("fa593fdcbbd1f3692ee6e2c9bd5b4aeac5b228bdf47f58876b8a7b7bf088ffcb");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_00.T_Guard210_Wake_00"),TEXT("49fa77d9b1f1b3f2de3f69acb0aed401209605f484970954fde1e22ec2746faf"),TEXT("b9e0d20c213f33b088b7cab58e0611d1803f40fc9c47f415439302aeb3ccdb4f"),FVector2D(242.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_01.T_Guard210_Wake_01"),TEXT("3ddc276f3e82e8d27c66f7299fda6faf56e84db204fb414b38a4004f48aa1860"),TEXT("2186bafc76aaeab3726eef067e279e7c163f3fac751b82534ded1f56f59c643d"),FVector2D(239.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_02.T_Guard210_Wake_02"),TEXT("d0d6bae6554fdaa7b33656dbdc5d74f7b985be7c3da21db1db5c518491671a03"),TEXT("65d76cb6c48ff168f7f0e1ed360bc234b986b1a1317d8d14c7f90db178e4dec9"),FVector2D(233.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_03.T_Guard210_Wake_03"),TEXT("6181bcee3202e5f6782ec5ed06981ad0e1858e1d03e598d2ffc3d5beab08274d"),TEXT("d6ffd68591fbd06d2f5ebfa3bee62a366375b843e6f0f136cd1cf42f02247921"),FVector2D(239.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_04.T_Guard210_Wake_04"),TEXT("d930ff34a7c18cee11853286b374b1e161b54cb2c1ae06b8ac447ec0b00f2429"),TEXT("e29cb7bf685b0c39e5406a338aa946172b4d0232dab2eca8fcf97c5f4957e8bc"),FVector2D(237.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Wake/T_Guard210_Wake_05.T_Guard210_Wake_05"),TEXT("542529833eb98a976d3c146c25fa826020cdb6784a23a13982e82c56b650813d"),TEXT("6571450252eb8767f85df60688d6fd523640dfb48f8605f5710dd8183fbb6f5f"),FVector2D(242.0,464.0),EPivotAuthority::VisibleShoeSupport});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::Ready;R.NativeSourceId=209;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=0;R.StandingCrownY=49;R.StandingSoleY=463;R.StandingExtent=415.;
   R.RegistrationEvidenceSHA256=TEXT("32162f683dcccdd52f90dd94c5be667ca73d2b60be9e486dca4007809b730dfe");
   R.SourceIndexSHA256=TEXT("31b213cbb7ff1cc118b290e12e6578d968f74a006b7c1023be7a5be2624884a3");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_00.T_Guard209_Ready_00"),TEXT("54df5fe718a98e1568513193dbde479aff6fd393d623755feb77813cacb4e804"),TEXT("4a919bba4de370c80e885a0f839fbbad7589b1a45de97e3561f41c88187c1e5e"),FVector2D(235.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_01.T_Guard209_Ready_01"),TEXT("3fe3841442c48497d583f4c2622ef9c0bea3c1dc5082cf3b3d373760d547b0e7"),TEXT("e7b34daeca89cebec831667188cfa706597e482dbdd570ca1a777348afe50891"),FVector2D(234.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_02.T_Guard209_Ready_02"),TEXT("301878a9ea8523275eb271240e1915620d772a9ec52d73efdc1123e1cd7b682c"),TEXT("fd2749272eb032b99f7ba997e758a213184002e90267b6b426b6d610d13b18d1"),FVector2D(244.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/Ready/T_Guard209_Ready_03.T_Guard209_Ready_03"),TEXT("90c21f1c417102e15f3e601d19351c8a40251e2317fb30b3d004d8d21e35e5b2"),TEXT("e8d4a0bd0f2648b663278201c96afb2d6145f5f92dc887c569255e2d6bc530ee"),FVector2D(236.0,464.0),EPivotAuthority::VisibleShoeSupport});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::Move;R.NativeSourceId=0;R.SourcePoseApproved=false;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.PendingNativeCandidateId=0;R.GapReason=TEXT("Native221 and223 source rows rejected; no accepted alternating six-phase Move source or floor registration. No bad native pixels imported.");
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::AxeWindup;R.NativeSourceId=212;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=0;R.StandingCrownY=191;R.StandingSoleY=463;R.StandingExtent=273.;
   R.RegistrationEvidenceSHA256=TEXT("85c493cd3ef7c0abe29046d2b6a8acb185dcee061ed5ac3ceff772bb0ef54e9c");
   R.SourceIndexSHA256=TEXT("5f05dc1406bc7fc2013a1772daae191d81dcbd2c27d7c469953fd9f78759157a");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_00.T_Guard212_AxeWindup_00"),TEXT("39bd95d59253f8f7a41a4dcc96359b12298af789f0b9a444b694e60c4fd544df"),TEXT("58a5f01e1fd034a1d553116e00bac5bd20213a567efc2da5bf5e8af6d543672b"),FVector2D(242.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_01.T_Guard212_AxeWindup_01"),TEXT("ce00612d616abc65b1b27621a708ed27a54708f039c117aaf1bff002512f80a8"),TEXT("e1e697613a0d68ff5e1fa72987c4b62fbc76fff75add04d6e53a8109262feb25"),FVector2D(241.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_02.T_Guard212_AxeWindup_02"),TEXT("42ef74e275602583ac3579f8ac3c6318a37d3dd26ecb24359bd55c082a6a9ea5"),TEXT("04e05443640328f375e5f1d2a1751dca45405cbf73c5d38b8c261548f0025819"),FVector2D(253.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_03.T_Guard212_AxeWindup_03"),TEXT("2162193d81f25e6c5de2c332a6738828feb0cc04c8b24f935529dd24e136de42"),TEXT("626aee0f745d7eb4fbb5068cb5f33cab159e57c3f2b6eb7e8d903150bd10ec70"),FVector2D(268.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_04.T_Guard212_AxeWindup_04"),TEXT("1b57280dd022c5fe4b1d6d7659f181115e9f50c2ae898a6d49e6a30c0026c95a"),TEXT("3c793a3b40ceac766f26d4572b61c39163c89a11290c3cd045cb446f8d20c08f"),FVector2D(273.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_v001/AxeWindup/T_Guard212_AxeWindup_05.T_Guard212_AxeWindup_05"),TEXT("18a88f23b28f0e7971d4e897ca28b3c78ed7616ae6215e9319cc75c9c6dcf3b2"),TEXT("186096b776bed7ff712fe18690f10e4073e15df958ea38b3f00ca560eeda78b9"),FVector2D(292.0,464.0),EPivotAuthority::VisibleShoeSupport});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::AxeActive;R.NativeSourceId=215;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=0;R.StandingCrownY=122;R.StandingSoleY=463;R.StandingExtent=342.;
   R.RegistrationEvidenceSHA256=TEXT("33bf98760f857986fd5bc2b8cae9ed28a53f51ab8a8806e62671129dd54cc91e");
   R.SourceIndexSHA256=TEXT("59693db06d95e822333bf249eeca01546b9de169e50cbbc52c3a03ef8ff12a77");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeActive/T_Guard215_AxeActive_00.T_Guard215_AxeActive_00"),TEXT("b97fd6bc5fcf8d203013e71b05b68448295ce5f15f33ad7f59a37654a4f6cd28"),TEXT("d1512bf80fcd2116d2da801c48bdb8b9d90ad36ebf88f00c9bf9474483996e94"),FVector2D(220.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeActive/T_Guard215_AxeActive_01.T_Guard215_AxeActive_01"),TEXT("70623813bdb8b8c9beed9466c7b55aadf8c4da6653c733755242ac6e4bfa09cd"),TEXT("5780726444e4bfe11f77c55d6a77503b238c4839eba08a5ae2506183e20ebe19"),FVector2D(190.0,463.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeActive/T_Guard215_AxeActive_02.T_Guard215_AxeActive_02"),TEXT("e146ddb280384a9b55ed882ef38f7a767d8de0095d8e6b4d5f246f79bdf7491f"),TEXT("c637bd1d8537c7ac44637599116d3cbb8d797a0099edf2bbeeca523c375c1165"),FVector2D(198.0,432.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeActive/T_Guard215_AxeActive_03.T_Guard215_AxeActive_03"),TEXT("ec625087cb3c7ad0e6677d272a6887c5a7c8e1a3ed94c05b86c113fb6fdd3136"),TEXT("c632bb55c9d29805673274dc27871fe072e9042c3fe01b42fea75729fa8698af"),FVector2D(209.0,432.0),EPivotAuthority::VisibleShoeSupport});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::AxeRecovery;R.NativeSourceId=216;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=3;R.StandingCrownY=98;R.StandingSoleY=463;R.StandingExtent=366.;
   R.RegistrationEvidenceSHA256=TEXT("3b8d201227a319cdce293c4ee23dde41259236d1ca9138b0dc4a3393dcd76b05");
   R.SourceIndexSHA256=TEXT("49f059065d4baf3284efc270c60262b9f58fbe7051b26c27d278f51e0b4e6e50");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeRecovery/T_Guard216_AxeRecovery_00.T_Guard216_AxeRecovery_00"),TEXT("997586d88c3cb94dc0733d8f67fb51d622a0e7dfe01b3f1f502b838e4addbd91"),TEXT("49c12c8f593d95f594d0434c2d7458f4d352148532ac4795b8b161fd6e112d64"),FVector2D(209.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeRecovery/T_Guard216_AxeRecovery_01.T_Guard216_AxeRecovery_01"),TEXT("12b21f2ee8bc7ce3b9055c2c29bcc81828b7ada220d869920cf447591597d513"),TEXT("480d13fe961c5b1cf4b14e61205bd91112b6ad2ce52c8dc52221afbceee405f6"),FVector2D(222.0,463.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeRecovery/T_Guard216_AxeRecovery_02.T_Guard216_AxeRecovery_02"),TEXT("e95a4507207dd83a644c4e1a4ee4132e8b65a0eefafa1eb4eabfe544ad3614c3"),TEXT("cfbd877d070880e5c82a56214f01fda2a922e6a7a4f0de6c7e382490042171c4"),FVector2D(249.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/AxeRecovery/T_Guard216_AxeRecovery_03.T_Guard216_AxeRecovery_03"),TEXT("6e83b765ef8a3e384d5425f54cae24f4dae388eb6c65a6e710221ce5c3cc0e36"),TEXT("0445f6deb2ab05c47560883d6cc62e8e85a6e75e15084b783b62915925b43dd1"),FVector2D(239.0,464.0),EPivotAuthority::VisibleShoeSupport});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::StompWindup;R.NativeSourceId=222;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=0;R.StandingCrownY=76;R.StandingSoleY=463;R.StandingExtent=388.;
   R.RegistrationEvidenceSHA256=TEXT("1eeb78d99703b7d27e9ea699ff5b8c90415effa0e30c6df50c2f0c900ecde08d");
   R.SourceIndexSHA256=TEXT("2506cdaeff86129f7bde5c92b83616d810b714fc8389d83e75912cec4dc7381a");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/StompWindup/T_Guard222_StompWindup_00.T_Guard222_StompWindup_00"),TEXT("55964c68e30decbbcc87dee8c2d5da21f2cc3cf6b3a2511456214abaf3257198"),TEXT("d368ea2e0cd59c51e727d884b97d2cf9ca86ec00c80ae05de143458f32284399"),FVector2D(251.0,464.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/StompWindup/T_Guard222_StompWindup_01.T_Guard222_StompWindup_01"),TEXT("417ce45951c7ece7557766cb3f25b8f0b89a7bff93e2ff2d8d7536bf242b66f3"),TEXT("b9694438b1280fc2eb9c248ef7206b60dd53d69412dd7f97fdfd868fdb84859f"),FVector2D(246.0,463.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/StompWindup/T_Guard222_StompWindup_02.T_Guard222_StompWindup_02"),TEXT("8715df198be1a781f545644eace9323c982c64b2c33a9fc214db286629dbd028"),TEXT("fb6f150f319a23641f2602551631ae96af0ad67ddc0c7042d33515a436404a8f"),FVector2D(260.0,463.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/StompWindup/T_Guard222_StompWindup_03.T_Guard222_StompWindup_03"),TEXT("1ad19a548af7b6df42415a5b8d8e0c60ec4ab4f83f67bc96a3e4bbd9e8a6cc7e"),TEXT("c74ee37ee41aed9f0b79b49eecca2f142f5d116f7266332b0c5c850178ec6524"),FVector2D(259.0,463.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/StompWindup/T_Guard222_StompWindup_04.T_Guard222_StompWindup_04"),TEXT("dfe71280f7ff52dab8c5fa1219b4318aa8cd1e7aedea744ca9742bc8d46eef36"),TEXT("ecfc02c1f9663e8466a42081809c7fa5d9679f0c5b0d4c239e12df0ba2948346"),FVector2D(266.0,463.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/StompWindup/T_Guard222_StompWindup_05.T_Guard222_StompWindup_05"),TEXT("563827121d0fda81d4b53d5c1e87fde5061fbd7ab8f59426c5bd8edacca5c047"),TEXT("d42935f30cc3905c2dfaa0701b0728105949080cf81b6e1389b061e1d2220896"),FVector2D(309.0,463.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::StompActive;R.NativeSourceId=0;R.SourcePoseApproved=false;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.PendingNativeCandidateId=224;R.GapReason=TEXT("Native224 source accepted for future samples; body/root registration and WU-to-Active join remain proposal/risk. No runtime trial record or import admitted here.");
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::StompRecovery;R.NativeSourceId=0;R.SourcePoseApproved=false;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.PendingNativeCandidateId=0;R.GapReason=TEXT("No accepted source chain or body-floor registration; v005375ms x4 fixed before future generation.");
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::Stunned;R.NativeSourceId=213;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=3;R.StandingCrownY=54;R.StandingSoleY=463;R.StandingExtent=410.;
   R.RegistrationEvidenceSHA256=TEXT("c746f9c4fd58d8c6893f56f5b512dc98f6721603f5769def43ee4e386b395020");
   R.SourceIndexSHA256=TEXT("8c4fd9408f65f08dd57a0a3884be18f18ddd97da29a6962f15bcbee42d29974c");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Stunned/T_Guard213_Stunned_00.T_Guard213_Stunned_00"),TEXT("61bb84effd274c65394b1d89ce44df6494849cec737fa6fd1988e1ea9365af7c"),TEXT("61834be90a44c7d9f26bf44042fa59750a715852b500b256b322f26b2c056d92"),FVector2D(222.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Stunned/T_Guard213_Stunned_01.T_Guard213_Stunned_01"),TEXT("266f627448a57265f1e40ab0ac5a4436f44d804dca9c73cac09e4940de80ecf4"),TEXT("bba97fe724a19377c21306d08a41c4e9099699ca7fc9e9c9bd0c64bb105264ba"),FVector2D(227.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Stunned/T_Guard213_Stunned_02.T_Guard213_Stunned_02"),TEXT("0242a8d6e177e50ce0e0d47935a69e632a92e7758f58a1e70e12fd088a9fd935"),TEXT("ad02156ad18ce5f8bcf11ed0c309d1b589f329cd02ffac3d653b99467551b4aa"),FVector2D(224.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Stunned/T_Guard213_Stunned_03.T_Guard213_Stunned_03"),TEXT("7a993485d714aa6ef6879ac3540c53cf26f56b350507d6c0c5fc26063bd0da23"),TEXT("9d12727dd79870ac21bd4292d233860fd32e27eedd0fac5d6a665d622c1383e5"),FVector2D(240.0,464.0),EPivotAuthority::VisibleShoeSupport});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::Death;R.NativeSourceId=214;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=0;R.StandingCrownY=98;R.StandingSoleY=462;R.StandingExtent=365.;
   R.RegistrationEvidenceSHA256=TEXT("7d04e86fbd268558bca925f99a1fd6de1c511e6b574933180fc4c5603a38f9e3");
   R.SourceIndexSHA256=TEXT("395ee3c2337f3f837a82ad38bd1799716934df8438a1af03be826780f839f1ff");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Death/T_Guard214_Death_00.T_Guard214_Death_00"),TEXT("9d389f80b06b2143ef3bbc60c6ba2d89b0fa11b93cb59fb8c86584818ba42e63"),TEXT("2bad79e1f8cfbe103717fb8118fc16b9b3cfa17132603966ee11bcfa304079c9"),FVector2D(224.0,463.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Death/T_Guard214_Death_01.T_Guard214_Death_01"),TEXT("bcd56d04ad5f0a294bf94a54a69192730b34b9eaa17976427d941810457792f8"),TEXT("d4380b0a151e6c35b49330a70c3e62db6cad6c9f58bd453768a08cb6d37bb402"),FVector2D(277.0,459.0),EPivotAuthority::ArtistStandingRootPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Death/T_Guard214_Death_02.T_Guard214_Death_02"),TEXT("d5db770fea6a34b52c906e0eec33e7ba8513800091be9368f6f37aba8d6f79c0"),TEXT("6b472366419279f47b1b0b77d9c8a0c9701c9a238ad0429329f9757cc5c2b2d0"),FVector2D(290.0,453.0),EPivotAuthority::ArtistStandingRootPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Death/T_Guard214_Death_03.T_Guard214_Death_03"),TEXT("789ccf682879ff4eec8ce830fe7341b56dc72f8c6ee601efed1577ba64bc835b"),TEXT("731af5c3f4e6aec3501a56e49f375f82af401de84515973b1d7b906cd8e9c324"),FVector2D(282.0,453.0),EPivotAuthority::ArtistStandingRootPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Death/T_Guard214_Death_04.T_Guard214_Death_04"),TEXT("2449157f0c000f39e60377b5345a48d6e5820f31e6994438ec591677c0d21e12"),TEXT("a850a2d550bd10689c4e7423735aeddd3816805d9767aedceb1d4a5e34aabd04"),FVector2D(266.0,453.0),EPivotAuthority::ArtistStandingRootPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/Death/T_Guard214_Death_05.T_Guard214_Death_05"),TEXT("a097242a0cee5a3f579902ac202cb21fbfeb652e64aae3bdca28db21d207d270"),TEXT("f934aa6d5f55cca3c6056a9de9e3a9fed19d7c50bcaad24a0ac059d1217fae7b"),FVector2D(243.0,453.0),EPivotAuthority::ArtistStandingRootPropagation});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::InterruptedRecovery;R.NativeSourceId=217;R.SourcePoseApproved=true;
   R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");
   R.StandingBasisFrame=3;R.StandingCrownY=49;R.StandingSoleY=463;R.StandingExtent=415.;
   R.RegistrationEvidenceSHA256=TEXT("6502aea5e1606147e33dfe2b53d5067278d0ec69d3450f60cbcd2929888afabc");
   R.SourceIndexSHA256=TEXT("6a344dacc8268e2eb7fc4d989e0bad2593f2f1abbb586485eba9bf32e5340174");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/InterruptedRecovery/T_Guard217_InterruptedRecovery_00.T_Guard217_InterruptedRecovery_00"),TEXT("73bfdd41e2215c8e6b1383f0ec374f9cd670fd9f435089e5384da256fec2d2a4"),TEXT("55c1b672bdd68e0ef300bc72a99000e45e5e7d08b842a0ad55ed2b07151b79b8"),FVector2D(241.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/InterruptedRecovery/T_Guard217_InterruptedRecovery_01.T_Guard217_InterruptedRecovery_01"),TEXT("c88ab75a1fe17a14d99de28f72201694f43c0abfaee66ded3e951bd08f06b181"),TEXT("959da8f539360998c5157983b835e15b52dc81ff3d43c09aae6b6fff14087a31"),FVector2D(235.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/InterruptedRecovery/T_Guard217_InterruptedRecovery_02.T_Guard217_InterruptedRecovery_02"),TEXT("f93b36943d471c5e81b831d8318890f5e24639e38c7570031a8ee70c0d27a55f"),TEXT("75d1590e5fdd038ea46c45e8427d228316f582fbe11ecb013da24778ab6cc109"),FVector2D(232.0,464.0),EPivotAuthority::VisibleShoeSupport});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_full_v003/InterruptedRecovery/T_Guard217_InterruptedRecovery_03.T_Guard217_InterruptedRecovery_03"),TEXT("2336a86ebb238b58deac8923ca255a0c0d76b0c713f6405a8e409c253c445caf"),TEXT("8785074d6ee807f1aa3d2e0d5ad13e82112ae4acc29b49fc62347785b784a5f2"),FVector2D(231.0,464.0),EPivotAuthority::VisibleShoeSupport});
   A.Add(MoveTemp(R));}
  return A;
 }();return Rows;
}
}
