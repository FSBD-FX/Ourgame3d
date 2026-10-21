  // The new renderer selects Bridge258 J0/J1, so explicitly retain the old
  // fourteen layers still required by the unchanged old115 readback contract.
  TArray<TStrongObjectPtr<UTexture2D>> Bridge258LegacyReadbackRefs;
  if(Bridge258ObservationEnabled()&&Action==TEXT("J"))
  {
   for(int32 Frame=0;Frame<2;++Frame)for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
   {
    const bool Armor=FString(Component)==TEXT("ShoulderFar")||FString(Component)==TEXT("Chest")||FString(Component)==TEXT("ShoulderNear");
    const FString Name=Armor?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),Component,Frame);
    const FString Path=FString(Armor?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"):TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/"))+Name+TEXT(".")+Name;
    Bridge258LegacyReadbackRefs.Emplace(LoadObject<UTexture2D>(nullptr,*Path));
   }
   FlushRenderingCommands(); // Before the original strict FindObject/RHI/pending checks, before audio/input.
  }
