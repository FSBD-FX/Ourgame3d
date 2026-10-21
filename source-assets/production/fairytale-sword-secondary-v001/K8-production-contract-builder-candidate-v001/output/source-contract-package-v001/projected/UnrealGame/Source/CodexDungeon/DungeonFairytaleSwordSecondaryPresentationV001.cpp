#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonFairytaleSwordSecondaryPlanV001.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Misc/PackageName.h"
#include "TextureResource.h"
#include "UnrealClient.h"

namespace DungeonFairytaleSwordSecondaryV001
{
const FProfile& Profile()
{
 // Metadata complete; NOT a Content import receipt or runtime admission.
 static const FProfile MetadataComplete=[](){
  FProfile P;P.RuntimeReady=false;
  P.ProfileId="SWD001_K8_SourceTrial_v001";
  P.SourceContractSha256="ef1d2418b7bae89da963fe6d3963c250fa84f89b7108581058dbf06d12be1d4b";
  P.Frames[0].Root={256.0,464.0};
  P.Frames[0].Grip={212.0,313.0};
  P.Frames[0].Axis={0.9400559349922476,-0.3410202913110175};
  P.Frames[0].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_00_v001.T_SWD001_K_BodyRest_00_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/BodyRest/K0.png","5de0611be5ae4eb3d30de857cf59ae666ece4cc81e503efda95b7aaeb971e6e1",68828ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_00_v001.T_SWD001_K_ShoulderFar_00_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K0.png","0f57103907931b760cc03a99ece992f6ed058e81c8a5276ad5a4d699ebb84e0a",2594ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_00_v001.T_SWD001_K_Chest_00_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/Chest/K0.png","f8c9c6081a565ff46bd0e2b0f9a45bcd5de5c753ac36bae288077aed2244340d",16697ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_00_v001.T_SWD001_K_NearArmWithoutHand_00_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearArmWithoutHand/K0.png","04dc67e5616013539a03d0769577f39f15b7f787b371bb5290482938278c6ef8",6297ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_00_v001.T_SWD001_K_ShoulderNear_00_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderNear/K0.png","6a8163a32439cc5a9bf4c60e78ac441a7dea795b225d8220208153f0198093f8",6597ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_00_v001.T_SWD001_K_HelmetForeground_00_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/HelmetForeground/K0.png","98e6c3cd6e7418f4f154efc4ee715816db1f88ad25de697887ba8aef3de225e9",48036ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_00_v001.T_SWD001_K_NearHand_00_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearHand/K0.png","198047dd818eedf00292321959ba4e8c60fa815e3a31de2ab102aa770cf48730",12977ULL}}
  }};
  P.Frames[1].Root={256.0,464.0};
  P.Frames[1].Grip={162.0,180.0};
  P.Frames[1].Axis={-0.3499179538586025,-0.9367803507586017};
  P.Frames[1].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_01_v001.T_SWD001_K_BodyRest_01_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/BodyRest/K1.png","7721cb58c54dd0d14d1395b4d8f88a4ed3fbb2c8f221085f71efec0309f2c78c",73155ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_01_v001.T_SWD001_K_ShoulderFar_01_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K1.png","2e7e46849d93a67778f2eeac5a6df1030ac3605d762956a99a9d94cd0ff83414",3088ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_01_v001.T_SWD001_K_Chest_01_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/Chest/K1.png","ecefdc4f238cd80c9857c96ed3ed928b20265c3f150f6fb36620106a7cab79d5",17889ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_01_v001.T_SWD001_K_NearArmWithoutHand_01_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearArmWithoutHand/K1.png","a0eea3f7941945447a953390b9a73d0234bbe31573575e81628931c8d2bef8e8",9606ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_01_v001.T_SWD001_K_ShoulderNear_01_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderNear/K1.png","20eea2f78f6065ceeb2ac6e5de18e0ef7a1333f74fa1a5929e0691aa90d3b77c",6909ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_01_v001.T_SWD001_K_HelmetForeground_01_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/HelmetForeground/K1.png","f64c6dac5167f01df090d77298d0c8ca072b448cf21531a7a1c235073b63dcb0",47951ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_01_v001.T_SWD001_K_NearHand_01_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearHand/K1.png","ebc15d773ce31d4880aeb51c7f1bb732e6ae19151d0098d44dfd32d99859b476",12306ULL}}
  }};
  P.Frames[2].Root={256.0,464.0};
  P.Frames[2].Grip={163.0,143.0};
  P.Frames[2].Axis={-0.4500114754389374,-0.8930227723710469};
  P.Frames[2].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_02_v001.T_SWD001_K_BodyRest_02_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/BodyRest/K2.png","c0986340890d5697e4bf77fe445afc1d835ab302a007da1e55bbfb4c76753512",74608ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_02_v001.T_SWD001_K_ShoulderFar_02_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K2.png","a9bb2792cd20fa726e65c96d8f8488ec99dd6eaf70b4b1f27f7f83856a807b50",3084ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_02_v001.T_SWD001_K_Chest_02_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/Chest/K2.png","51e39b2eac6dc2805aec659fdcef2bf700f919a8b9eea32567fdb4ac69b57e97",17908ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_02_v001.T_SWD001_K_NearArmWithoutHand_02_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearArmWithoutHand/K2.png","d5575ea974d3c24d51345262a97a73680d6032b837a8f3d08206cf44d8bdba91",11325ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_02_v001.T_SWD001_K_ShoulderNear_02_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderNear/K2.png","7ae78fd79d3984c32fc226162cee4ff510bd14122835d9ed019f6665b81ba815",6926ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_02_v001.T_SWD001_K_HelmetForeground_02_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/HelmetForeground/K2.png","39d31037723d69c3e55293b81bedc428426aa5b94978d4c75098e838f9a97aab",46491ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_02_v001.T_SWD001_K_NearHand_02_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearHand/K2.png","ad4840380f0ea6389f8584d745f3ae6e9fa7173543a6c78daba124a6f0fafe91",11121ULL}}
  }};
  P.Frames[3].Root={256.0,464.0};
  P.Frames[3].Grip={294.0,301.0};
  P.Frames[3].Axis={0.9658855493432025,-0.2589693139543369};
  P.Frames[3].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_03_v001.T_SWD001_K_BodyRest_03_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/BodyRest/K3.png","26bb86bc10808c268ad4ce679b220cb90e84bc9f87ea2fd77286e5b660a84645",74370ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_03_v001.T_SWD001_K_ShoulderFar_03_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K3.png","952856cf1fdafc4ad6bd1c982db0b7b3e55d3cca56b65ec409cbf008217d7101",2999ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_03_v001.T_SWD001_K_Chest_03_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/Chest/K3.png","091855dce02d1ee0ddff61fe87365a377ea9a772a352ee30149a8fcd41b42cf5",17769ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_03_v001.T_SWD001_K_NearArmWithoutHand_03_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearArmWithoutHand/K3.png","dbaddcf89ce966b0aa0025fce6f63d2457d612a84c302059b0aa227bb22742ea",7483ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_03_v001.T_SWD001_K_ShoulderNear_03_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderNear/K3.png","dd8815aa7c2e9cd7b804c3bec394b91daa6f64fbc8cb597869338d089564a330",6551ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_03_v001.T_SWD001_K_HelmetForeground_03_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/HelmetForeground/K3.png","ded9b3e433b45284b824a2da6ef9dadeca3d78b6e6ed6ccff6551da10994f63d",47295ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_03_v001.T_SWD001_K_NearHand_03_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearHand/K3.png","26f27524e42e2628904199d6c0733e552b50be53a72c0254b3c0f83c2ba5c050",12386ULL}}
  }};
  P.Frames[4].Root={256.0,464.0};
  P.Frames[4].Grip={363.0,347.0};
  P.Frames[4].Axis={0.8,0.6};
  P.Frames[4].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_04_v001.T_SWD001_K_BodyRest_04_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/BodyRest/K4.png","7940d50499dac2b7ddf443179b2739b7a4b51412a30187b4b5d1a7701e24b454",73212ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_04_v001.T_SWD001_K_ShoulderFar_04_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K4.png","fff3f6c7d81429c2e1e4dd61e8e1a51f579c7c530ed372e176a73c039eb7562e",2818ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_04_v001.T_SWD001_K_Chest_04_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/Chest/K4.png","ca0a52a88d55fad2d8258eb0bc5165b4ec76b48ee94d8756e5cdc3ee90a8144c",17647ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_04_v001.T_SWD001_K_NearArmWithoutHand_04_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/NearArmWithoutHand/K4.png","1fef9610585b18feec33e8c31e5153f958f861d3edcc523cd32376d8e0806f0b",9666ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_04_v001.T_SWD001_K_ShoulderNear_04_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/ShoulderNear/K4.png","381e6306f5713366d8d8a30641b18473f3c97487c3192d4720b528383c61ea51",6551ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_04_v001.T_SWD001_K_HelmetForeground_04_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/HelmetForeground/K4.png","f03cadff5c9504d03faff5d408f80f5df67fc8f0aa7e555fd27f51e2b58ac9f8",46644ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_04_v001.T_SWD001_K_NearHand_04_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/NearHand/K4.png","d90e5ffa030883511b0833eff17df33af7bacb85255a0a3e7a8370669a91191f",13339ULL}}
  }};
  P.Frames[5].Root={256.0,464.0};
  P.Frames[5].Grip={257.0,322.0};
  P.Frames[5].Axis={0.9400559349922476,0.3410202913110175};
  P.Frames[5].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_05_v001.T_SWD001_K_BodyRest_05_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K5-body-owner-correction-v002/body-layers/BodyRest/K5.png","6da2e66fcdcd1bf0787f7b536dec8740c8c58cb7f04e4bcaea9e067bd359d062",71579ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_05_v001.T_SWD001_K_ShoulderFar_05_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K5.png","8ee6596c8e1a972087752e2195372b1395fc9b60a56cad045f41571b83f8ee12",3000ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_05_v001.T_SWD001_K_Chest_05_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/Chest/K5.png","03220a01a61a73a0a757d8856befb3540ba219e35aae4619a465cb73cb42537e",17757ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_05_v001.T_SWD001_K_NearArmWithoutHand_05_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K5-body-owner-correction-v002/body-layers/NearArmWithoutHand/K5.png","f40d17cffc2141afab0bab61c47a65635fa3f4a52c75aab22587d822054337cf",5803ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_05_v001.T_SWD001_K_ShoulderNear_05_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K5-near-shoulder-integer-fit-v003/near-shoulder-candidates/A/K5.png","c5f42b2ca612e15d151d18fcab94e3fa56df8cdb0bd95d13d611955daf245a52",6569ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_05_v001.T_SWD001_K_HelmetForeground_05_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K5-body-owner-correction-v002/body-layers/HelmetForeground/K5.png","8c21c408ba1741c4252c16492c23ee510e05d835564f82edfe93e07158930dc2",48636ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_05_v001.T_SWD001_K_NearHand_05_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K5-body-owner-correction-v002/body-layers/NearHand/K5.png","8daf3272dac03cddf455579b3310493badfa14ff2ec0ea3be55a5070e915dba6",15191ULL}}
  }};
  P.Frames[6].Root={256.0,464.0};
  P.Frames[6].Grip={212.0,313.0};
  P.Frames[6].Axis={0.9400559349922476,-0.3410202913110175};
  P.Frames[6].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_06_v001.T_SWD001_K_BodyRest_06_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/BodyRest/K0.png","5de0611be5ae4eb3d30de857cf59ae666ece4cc81e503efda95b7aaeb971e6e1",68828ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_06_v001.T_SWD001_K_ShoulderFar_06_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K0.png","0f57103907931b760cc03a99ece992f6ed058e81c8a5276ad5a4d699ebb84e0a",2594ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_06_v001.T_SWD001_K_Chest_06_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/Chest/K0.png","f8c9c6081a565ff46bd0e2b0f9a45bcd5de5c753ac36bae288077aed2244340d",16697ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_06_v001.T_SWD001_K_NearArmWithoutHand_06_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearArmWithoutHand/K0.png","04dc67e5616013539a03d0769577f39f15b7f787b371bb5290482938278c6ef8",6297ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_06_v001.T_SWD001_K_ShoulderNear_06_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/armor-layers/ShoulderNear/K0.png","6a8163a32439cc5a9bf4c60e78ac441a7dea795b225d8220208153f0198093f8",6597ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_06_v001.T_SWD001_K_HelmetForeground_06_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/HelmetForeground/K0.png","98e6c3cd6e7418f4f154efc4ee715816db1f88ad25de697887ba8aef3de225e9",48036ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_06_v001.T_SWD001_K_NearHand_06_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/request260-body-owner-candidate-v001/body-layers/NearHand/K0.png","198047dd818eedf00292321959ba4e8c60fa815e3a31de2ab102aa770cf48730",12977ULL}}
  }};
  P.Frames[7].Root={256.0,464.0};
  P.Frames[7].Grip={212.0,313.0};
  P.Frames[7].Axis={0.9400559349922476,-0.3410202913110175};
  P.Frames[7].Layers={{
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_BodyRest_07_v001.T_SWD001_K_BodyRest_07_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/BodyRest/K7.png","68801987073bddeb6d6a8a46979ba055d56376b4614f86ec7fbec16e23987049",66008ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderFar_07_v001.T_SWD001_K_ShoulderFar_07_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/ShoulderFar/K7.png","869cdbb676af81474372457988d78deebbc28d0ab02507f403251e29410a20f9",2594ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_Chest_07_v001.T_SWD001_K_Chest_07_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/Chest/K7.png","eaa8550fbc3889fe710ced97229578ea62911415fbe92c668d53a090418177dd",16703ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearArmWithoutHand_07_v001.T_SWD001_K_NearArmWithoutHand_07_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/NearArmWithoutHand/K7.png","8f2ea3cee1d7e7ecd1b71c14eb187993c1af5136eab919988c85f79362b48ec7",6410ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_ShoulderNear_07_v001.T_SWD001_K_ShoulderNear_07_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-LGT-fit-candidate-v001/armor-layers/ShoulderNear/K7.png","6a8163a32439cc5a9bf4c60e78ac441a7dea795b225d8220208153f0198093f8",6597ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_HelmetForeground_07_v001.T_SWD001_K_HelmetForeground_07_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/HelmetForeground/K7.png","d36cf02971f76669a8329e29841000800a46bcac867b556a165e7c53cf558b49",47800ULL}},
   FLayer{"/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_NearHand_07_v001.T_SWD001_K_NearHand_07_v001",FSourcePin{"source-assets/production/fairytale-sword-secondary-v001/K4K5K7-body-owner-candidate-v001/body-layers/NearHand/K7.png","cde1e43d76bcd8ac9790c739e6fe9559b8bfa4b4ffd3e258f4197e5f066efa75",10127ULL}}
  }};
  P.Sword=FLayer{"/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002",FSourcePin{"source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png","2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a",31902ULL}};
  return P;
 }();
 return MetadataComplete;
}
}

void ADungeonHUD::ResetFairytaleSwordSecondaryDraw()
{
 const uint64 Previous=FairytaleSwordSecondaryDraw.DrawId;
 FairytaleSwordSecondaryDraw=FDungeonFairytaleSwordSecondaryDrawV001();
 FairytaleSwordSecondaryDraw.DrawId=Previous;
 FairytaleSwordSecondaryDraw.OptIn=bUseFairytaleSwordSecondaryPreview;
}

void ADungeonHUD::PreloadFairytaleSwordSecondary(TArray<UTexture*>& Textures)
{
 using namespace DungeonFairytaleSwordSecondaryV001;
 if(!bUseFairytaleSwordSecondaryPreview||!bUseFairytaleSwordEquipmentBoundPreview)return;
 const auto& P=Profile();if(!ProfileValid(P))return;
 const auto Preload=[&](const FLayer& Layer)
 {
  const FString Path=UTF8_TO_TCHAR(Layer.TexturePath);
  UTexture2D* T=Frames.FindRef(Path);
  if(!Frames.Contains(Path))
  {
   const FString Package=FPackageName::ObjectPathToPackageName(Path);
   T=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*Path):nullptr;
   Frames.Add(Path,T); // Strong UPROPERTY ownership; full object path key.
  }
  if(T)Textures.AddUnique(T);
 };
 for(const auto& F:P.Frames)for(const auto& Layer:F.Layers)Preload(Layer);
 Preload(P.Sword);
 // Caller uses the EXISTING FinishCompilation and startup render flush.
 // Drawing reads this cache only, never loads or waits on the render thread.
}

bool ADungeonHUD::DrawFairytaleSwordSecondaryBody(ADungeonFighter* F)
{
 using namespace DungeonFairytaleSwordSecondaryV001;
 namespace BindingNS=DungeonFairytaleSwordEquipmentBinding;
 if(!F||!bUseFairytaleSwordSecondaryPreview||!bUseFairytaleSwordEquipmentBoundPreview)return false;
 const auto& A=F->GetWeaponSkillAction();
 if(!A.Active||A.Type!=DungeonWeaponActions::EAction::Skill)return false;
 const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
 BindingNS::FBinding Binding;FString Why;
 if(!Game||!BindingNS::Resolve(*Game,*F,Binding,Why))return false;
 // Resolve is the one real owner/instance/skin authorizer for this K draw.
 // Unsupported MED/HVY/ROB/other weapon continues the existing closed path.
 const EArmor Armor=Binding.Armor==BindingNS::EArmor::LightArmor?EArmor::Light:EArmor::None;
 const auto& WA=F->GetWeaponActionsState();
 FContext C;C.OptIn=bUseFairytaleSwordSecondaryPreview;C.EquipmentBound=bUseFairytaleSwordEquipmentBoundPreview;
 C.OwnerAuthorized=true;C.BoundWeaponInstanceId=Binding.WeaponInstanceId;C.Armor=Armor;
 C.Grounded=WA.Budget.Grounded&&F->GetMeleeCombatState().Grounded;
 C.Dead=F->bDead||WA.Budget.Dead;C.Hurt=F->AnimationName==TEXT("hurt");
 C.Dodging=F->GetDodgeState().Phase!=DungeonDodge::EPhase::Idle;
 C.Equipping=F->GetArmorChangeRemaining()>0.f||Game->GetEquipmentView().Action.Active;
 C.MeleeActive=F->GetMeleeCombatState().Action.Active;
 C.WeaponTime=F->GetWeaponSkillTime();C.StateTime=WA.Time;C.SimulationTime=Game->GetSimulationTime();
 C.Height=double(F->JumpHeight);C.VerticalVelocity=double(F->GetVerticalVelocity());
 auto& Trace=FairytaleSwordSecondaryDraw;Trace.Sample=Sample(A,C);
 if(Trace.Sample.Decision==EDecision::PassThrough)return false;
 Trace.OwnsBranch=true;Trace.PlayerEntityId=F->GetRuntimeEntityId();Trace.Binding=Binding;
 Trace.ExpectedDrawCount=SelectedSlotCount(Armor);
 const uint64 Previous=FairytaleSwordDraw.DrawId;FairytaleSwordDraw=FDungeonFairytaleSwordDraw();
 auto& Record=FairytaleSwordDraw;Record.Active=true;Record.DrawId=Previous;
 Record.EquipmentBoundMode=true;Record.EquipmentBindingValid=true;Record.EquipmentBinding=Binding;
 Record.Clip=TEXT("sword_secondary");Record.ActionId=A.ActionId;Record.InstanceId=A.InstanceId;
 Record.SimulationTime=C.SimulationTime;Record.ActionStart=A.Start;Record.ActiveAt=A.ActiveAt;
 Record.ActiveEnd=A.ActiveEnd;Record.ActionEnd=A.End; // Stage remains -1; K is NOT a J AttackId.
 Record.NativeScreenshotPath=FScreenshotRequest::IsScreenshotRequested()?FScreenshotRequest::GetFilename():FString();
 bRenderedArmorLayersUsed=false;RenderedArmorLayerPaths.Reset();RenderedPlayerDrawStack.Reset();RenderedPlayerTexturePath.Reset();
 bRenderedWeaponBodyUsed=false;RenderedWeaponBodyFrame=-1;RenderedWeaponBodyFacing=0;RenderedWeaponBodyClip.Reset();
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=0.;RenderedWeaponBodyInstanceId=0;RenderedWeaponStateIndex=-1;
 RenderedWeaponBodyEmitScreen=FVector2D::ZeroVector;
 if(Trace.Sample.Decision!=EDecision::Sampled)
 {
  Trace.MissingReason=FString::Printf(TEXT("Secondary8 actual action/priority/clock rejected (%d); closed draw"),int32(Trace.Sample.Reason));
  Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;
 }
 const auto& P=Profile();Trace.ProfileReady=ProfileValid(P);
 if(!Trace.ProfileReady)
 {
  Trace.MissingReason=TEXT("Secondary8 final measured/pinned profile is not admitted; runtime_not_ready; no partial draw");
  Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;
 }
 Trace.ProfileId=UTF8_TO_TCHAR(P.ProfileId);Trace.SourceContractSha256=UTF8_TO_TCHAR(P.SourceContractSha256);
 const auto GroundPoint=Ground(F->GetGroundPosition());const auto ScreenGround=Screen(float(GroundPoint.X),float(GroundPoint.Y));
 Trace.Context.GroundScreen={double(ScreenGround.X),double(ScreenGround.Y)};Trace.Context.UIScale=double(UIScale);
 const auto& Frame=P.Frames[Trace.Sample.Frame];
 if(!Geometry(Frame,Trace.Sample.Facing,Trace.Context,Trace.Geometry))
 {Trace.MissingReason=TEXT("Secondary8 actual screen context or measured marker is invalid; closed draw");return true;}
 const auto& G=Trace.Geometry;
 Record.Supported=Record.ActionPoseSupported=true;Record.Frame=Trace.Sample.Frame;Record.Facing=Trace.Sample.Facing;
 Record.CanvasSize=CanvasSize;Record.Root={Frame.Root.X,Frame.Root.Y};Record.Grip={Frame.Grip.X,Frame.Grip.Y};
 Record.GripScreen={G.GripScreen.X,G.GripScreen.Y};Record.WeaponAngle=G.Angle;Record.WeaponScale=WeaponScale;Record.WeaponWidth=G.SwordWidth;
 Record.ArmorPreview=Armor==EArmor::Light;RenderedPlayerSpriteSize=float(CanvasSize);RenderedActorSpriteSizes.Add(F,float(CanvasSize));
 const auto CacheReady=[&](const FString& Path)
 {
  const UTexture2D* T=Frames.FindRef(Path);
  return T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512
   &&T->GetResource()&&!T->HasPendingRenderResourceInitialization();
 };
 std::array<bool,ClosureCount> Resident{};int32 ResidentIndex=0;Trace.ResidentTextures.Reserve(ClosureCount);
 const auto CheckResident=[&](const FLayer& Layer)
 {
  const FString Path=UTF8_TO_TCHAR(Layer.TexturePath);const UTexture2D* T=Frames.FindRef(Path);
  FDungeonFairytaleSwordSecondaryResidentV001 R;R.TexturePath=T?T->GetPathName():Path;R.ClassName=T?T->GetClass()->GetName():FString();
  R.Width=T?T->GetSizeX():0;R.Height=T?T->GetSizeY():0;R.Ready=CacheReady(Path);R.PendingInitialization=T&&T->HasPendingRenderResourceInitialization();
  Resident[ResidentIndex++]=R.Ready;Trace.ResidentTextures.Add(MoveTemp(R));
 };
 // Full future closure is required even for None: K0 cannot hide missing K7.
 for(const auto& Future:P.Frames)for(const auto& Layer:Future.Layers)CheckResident(Layer);
 CheckResident(P.Sword);Trace.AtomicPreflightReady=AllResident(Resident);
 UTexture2D* Textures[SlotCount]={};Trace.Slots.Reserve(SlotCount);
 const FLinearColor Tint=F->HitFlash>0.f?FLinearColor(1.7f,.6f,.4f,1.f):FLinearColor::White;
 for(int32 I=0;I<SlotCount;++I)
 {
  const bool Sword=I==6;const FLayer& Layer=Sword?P.Sword:Frame.Layers[I<6?I:6];
  const FString Path=UTF8_TO_TCHAR(Layer.TexturePath);Textures[I]=Frames.FindRef(Path);
  FDungeonFairytaleSwordSecondarySlotV001 Q;Q.SlotIndex=I;Q.Component=static_cast<EComponent>(I);
  Q.TexturePath=Textures[I]?Textures[I]->GetPathName():Path;Q.Selected=SelectedSlot(Armor,I);Q.TextureReady=CacheReady(Path);
  const FPoint Top=Sword?G.SwordTop:G.BodyTop;const double Width=Sword?G.SwordWidth:G.BodyWidth;
  // Store precisely the float parameters actually sent to DrawTexture below.
  Q.Top={float(Top.X),float(Top.Y)};Q.Size={float(Width),float(Width)};Q.UV={float(G.U),0.f};Q.UVSize={float(G.DU),1.f};
  Q.RotationDegrees=Sword?float(G.Angle):0.f;Q.RotationPivot=Sword?FVector2D(float(G.SwordPivot.X),float(G.SwordPivot.Y)):FVector2D::ZeroVector;
  Q.Tint=Tint;Trace.Slots.Add(MoveTemp(Q));
 }
 Record.TextureReady=Record.ArmorReady=Trace.AtomicPreflightReady;
 if(!Trace.AtomicPreflightReady){Trace.MissingReason=TEXT("Secondary8 complete56/sword57 cache is not ready; no partial draw");return true;}
 if(!Canvas){Trace.MissingReason=TEXT("Secondary8 actual Canvas absent; no rendered claim");return true;}
 ++Record.DrawId;Trace.DrawId=Record.DrawId;
 for(int32 I=0;I<SlotCount;++I)
 {
  auto& Q=Trace.Slots[I];if(!Q.Selected)continue;
  DrawTexture(Textures[I],float(Q.Top.X),float(Q.Top.Y),float(Q.Size.X),float(Q.Size.Y),float(Q.UV.X),float(Q.UV.Y),
   float(Q.UVSize.X),float(Q.UVSize.Y),Q.Tint,BLEND_Translucent,Q.DrawScale,Q.ScalePosition,Q.RotationDegrees,Q.RotationPivot);
  Q.Drawn=true;Trace.ActualRenderedStack.Add(Q.TexturePath);Record.DrawStack.Add(Q.TexturePath);RenderedPlayerDrawStack.Add(Q.TexturePath);
  FActorQuad Quad;Quad.Owner=F;Quad.Texture=Textures[I];Quad.Top=Q.Top;Quad.Size=float(Q.Size.X);Quad.Rotation=Q.RotationDegrees;
  Quad.Pivot=Q.RotationPivot;Quad.Tint=Q.Tint;Quad.Weapon=I==6;ActorQuads.Add(Quad);
  if(I==1||I==2||I==4)RenderedArmorLayerPaths.Add(Q.TexturePath);
  if(I==0)Record.TexturePath=RenderedPlayerTexturePath=Q.TexturePath;
  if(I==6)Record.WeaponPath=Q.TexturePath;
 }
 Trace.Drawn=Trace.ActualRenderedStack.Num()==Trace.ExpectedDrawCount;
 if(!Trace.Drawn)Trace.MissingReason=TEXT("Secondary8 actual submission count differs from selected None5/LGT8 slots");
 Record.ArmorDrawn=bRenderedArmorLayersUsed=Trace.Drawn&&Armor==EArmor::Light;bRenderedWeaponBodyUsed=Trace.Drawn;
 RenderedWeaponBodyClip=Record.Clip;RenderedWeaponBodyFrame=Record.Frame;RenderedWeaponBodyFacing=Record.Facing;
 RenderedWeaponBodyActionId=A.ActionId;RenderedWeaponBodySampleTime=C.WeaponTime;RenderedWeaponBodyInstanceId=A.InstanceId;RenderedWeaponStateIndex=Record.Frame;
 return true;
}
