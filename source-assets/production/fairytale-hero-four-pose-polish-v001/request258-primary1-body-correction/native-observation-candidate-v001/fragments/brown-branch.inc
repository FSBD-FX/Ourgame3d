 if(Primary&&D.Frame<2&&Bridge258ObservationEnabled())
 {
  const FString Sword=TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002");
  const FVector2D Grip=D.Frame==0?FVector2D(211.,343.):FVector2D(159.,213.);
  const FVector2D Axis=D.Frame==0?FVector2D(.94,-.341):FVector2D(-.2,-.98);
  const double Angle=FMath::RadiansToDegrees(FMath::Atan2(Axis.Y,Axis.X))*(D.Facing<0?-1.:1.);
  if((D.Facing!=1&&D.Facing!=-1)||D.Root!=FVector2D(256.,464.)||D.Grip!=Grip||D.WeaponPath!=Sword||D.WeaponScale!=.5||D.WeaponAngle!=Angle)return false;
  const TCHAR* Parts[]={TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT(""),TEXT("NearHand")};
  for(int32 I=0;I<8;++I)
  {
   FString Expected=Sword;
   if(I!=6){const FString Name=FString::Printf(TEXT("T_Fairytale_Bridge258_%s_%03d_v001"),Parts[I],D.Frame);Expected=FString(TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/"))+Name+TEXT(".")+Name;}
   if(D.DrawStack[I]!=Expected)return false;
  }
  return true;
 }
