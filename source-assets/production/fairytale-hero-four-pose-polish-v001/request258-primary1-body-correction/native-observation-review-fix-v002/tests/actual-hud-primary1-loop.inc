            for(const FString Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
                TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=GetFairytaleSwordArmorPrimary1Texture(Component,I))ReadyArmorTextures.Add(Texture);
