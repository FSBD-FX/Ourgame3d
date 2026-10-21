#pragma once
namespace DungeonFairytaleGuardStompV004
{
inline const TArray<DungeonFairytaleGuardFullV003::FRow>& ProfileStompV004()
{
 using namespace DungeonFairytaleGuardFullV003;
 static const TArray<FRow> Rows=[]
 {
  TArray<FRow> A;
  {FRow R;
   R.Clip=EClip::StompActive;R.NativeSourceId=245;R.SourcePoseApproved=true;
   R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("Root.GuardStomp50.v139.20261018.ScopedTrial.StompActive");
   R.StandingBasisFrame=0;R.StandingCrownY=48;R.StandingSoleY=463;R.StandingExtent=416.0;
   R.RegistrationEvidenceSHA256=TEXT("02455880bc7c6ec370a59b2d4f4b4569efe23152822b3da052cfebd846d25f97");
   R.SourceIndexSHA256=TEXT("9491cc7eb01ca7638447c4805ad4d6ee893bdcc8cc222c2da31278e35d79b5f9");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_stomp_v004/T_Guard245_StompActive_00.T_Guard245_StompActive_00"),TEXT("87913631392ed84f58357fefb29d00b956ca32417f9b7db5b581af3091e3132f"),TEXT("51edde7964693e8c1f28fe38f184e8364809b9cb521345d4a1a38bc05be0d97c"),FVector2D(290.0,464.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_stomp_v004/T_Guard245_StompActive_01.T_Guard245_StompActive_01"),TEXT("e74a17645e2e469bfd994a1225bcd623a0f5fb2ac0c9fc10905fcc7ccc66eda4"),TEXT("b3bda0ad8eb71f0258a6a11bc05f633e6d476f488ac25c7426f316f75f0e0e56"),FVector2D(290.0,464.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   A.Add(MoveTemp(R));}
  {FRow R;
   R.Clip=EClip::StompRecovery;R.NativeSourceId=248;R.SourcePoseApproved=true;
   R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("Root.GuardStomp50.v139.20261018.ScopedTrial.StompRecovery");
   R.StandingBasisFrame=2;R.StandingCrownY=48;R.StandingSoleY=463;R.StandingExtent=416.0;
   R.RegistrationEvidenceSHA256=TEXT("9d5de0328171e1e1a82be92407f9a6eacaeeba3e5aabad93028d7780ed6c3fc1");
   R.SourceIndexSHA256=TEXT("9ed6ae0e04acaf696d8a39795d1bf72c29f7eab984e92434f2c5de7952f64fc5");
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_stomp_v004/T_Guard248_StompRecovery_00.T_Guard248_StompRecovery_00"),TEXT("6e6da7a700da81942b3bcf812349871fef93b8eded0fc053d8e38b7fde5cce0c"),TEXT("d020f1a6b980d27856d28f892bbc9bc80d9340cf57592c93a531eb44fb34b4fb"),FVector2D(275.0,463.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_stomp_v004/T_Guard248_StompRecovery_01.T_Guard248_StompRecovery_01"),TEXT("951057b91b27e32c4e1a211437875b8846c117b3ac5454799da69e01f2c66488"),TEXT("5091a395859858a1b7e74de17e4086685c6d5315b24dd405c1a8f44d3ba89a12"),FVector2D(282.0,464.0),EPivotAuthority::ArtistNearSupportDeltaPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_stomp_v004/T_Guard248_StompRecovery_02.T_Guard248_StompRecovery_02"),TEXT("97cea78c71398eb8353d57d8861f6d9410223a3872a5f6dd6fd974a2253bcea9"),TEXT("def4c291b4cad90c8ed599e3fe8df5dd8e33b3ea951e5da17d07b8b65ad88751"),FVector2D(260.0,464.0),EPivotAuthority::ArtistStandingRootPropagation});
   R.Frames.Add({TEXT("/Game/Production/FirstBatch/GuardWhole_stomp_v004/T_Guard248_StompRecovery_03.T_Guard248_StompRecovery_03"),TEXT("549d595d52d55c45545d1daf730f1bf35543ac5fe45eb7cc7bba015fc5bda244"),TEXT("756757a2ef4d3cd3865bcc609d715fdba9cb3515dfbbc7ab39c281b6ea468334"),FVector2D(256.0,464.0),EPivotAuthority::ArtistStandingRootPropagation});
   A.Add(MoveTemp(R));}
  TArray<FRow> Result=ProfileFull();
  for(auto& Override:A){FRow* Target=Result.FindByPredicate([&](const FRow& Q){return Q.Clip==Override.Clip;});check(Target);*Target=MoveTemp(Override);}
  return Result;
 }();
 return Rows;
}
}
