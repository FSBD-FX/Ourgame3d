UTexture2D* ADungeonHUD::GetFairytaleSwordArmorPrimary1Texture(const FString& Component,int32 Frame)
{
    if(Frame<0 || Frame>=6)return nullptr;
    // Request258 two-frame trial; actual draw still requires committed LightArmor.
    const bool Bridge258=Frame<2 && bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytalePrimary1Bridge258Preview"));
    const bool LeatherPrimary1=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))
        &&(Component==TEXT("Chest")||Component==TEXT("ShoulderFar")||Component==TEXT("ShoulderNear"));
    const FString Name=Bridge258
        ?FString::Printf(TEXT("T_Fairytale_Bridge258_%s_%03d_v001"),*Component,Frame)
        :LeatherPrimary1
        ?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),*Component,Frame)
        :FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),*Component,Frame);
    if(const auto Found=Frames.Find(Name))return Found->Get();
    const FString Package=FString(Bridge258?TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/")
        :LeatherPrimary1?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/")
        :TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/"))+Name;
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)
        ?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Texture);
    return Texture;
}
