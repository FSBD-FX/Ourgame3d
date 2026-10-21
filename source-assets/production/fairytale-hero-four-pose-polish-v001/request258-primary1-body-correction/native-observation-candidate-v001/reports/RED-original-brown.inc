bool Brown(const FDungeonFairytaleSwordDraw& D,bool Primary)
{
 if(!D.Active||!D.Supported||!D.ActionPoseSupported||!D.TextureReady||!D.ArmorDrawn||!SwordDrawn(D)||D.GearPlaceholder||D.Frame<0||D.Frame>=(Primary?6:4)||D.DrawStack.Num()!=(Primary?8:7))return false;
 if(D.Clip!=(Primary?TEXT("sword_primary_1"):TEXT("sword_ready_idle")))return false;
 const TCHAR* Parts[]={TEXT("ShoulderFar"),TEXT("Chest"),TEXT("ShoulderNear")};const int32 Slots[]={1,2,4};
 for(int32 I=0;I<3;++I){const FString Name=Primary?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Parts[I],D.Frame):FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Parts[I],D.Frame);
  const FString Expected=FString(Primary?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"):TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"))+Name+TEXT(".")+Name;if(D.DrawStack[Slots[I]]!=Expected)return false;}
 return true;
}
