#include "DungeonFairytaleSwordHurtProfile.h"

// Frozen author/source metadata only. No production selector/renderer is implemented by Stage0.
namespace DungeonFairytaleSwordHurtV001
{
const FProfile& Profile()
{
 static const FProfile Value=[]()
 {
  FProfile P;
  P.ProfileId=TEXT("EV048-v017-HeroLeatherHurt-v001");
  P.SourceClosureSHA256=TEXT("38e3a3c90eeda66842a2f2d5c53260832c226d18ca58640ee0720dc9271a1f28");
  P.SourceClosureVerified=true;
  P.SwordTexturePath=TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002");
  P.Frames[0].Frame=0;
  P.Frames[0].Root=FVector2D(259.9182682987829,463);
  P.Frames[0].Grip=FVector2D(236,303);
  P.Frames[0].AxisArtist=FVector2D(0.7,0.714142842854285);
  P.Frames[0].ExpectedNonemptyDrawCount=9;
  P.Frames[0].Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_BodyRest_000_v001.T_Fairytale_Hurt_BodyRest_000_v001"),TEXT("3bc5ab6aba5e6d7c52158f727e56ee6093921badd7f0822352fba8e8055390e8"),TEXT("55f90baa0d5ab145ea4bb2bcbc2b8db53faabfe55d6bab275e3a1387c24f4a43"),25599u,false};
  P.Frames[0].Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderFar_000_v001.T_Fairytale_Hurt_ShoulderFar_000_v001"),TEXT("6bd809fc6c790e69a01a1fa0e94a18411021a664c44bb69f3aebf7c43034accc"),TEXT("9316a89090294b68c6330658055f730a7fdaf6810d608261e81e7f602e50eb2a"),333u,false};
  P.Frames[0].Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_Chest_000_v001.T_Fairytale_Hurt_Chest_000_v001"),TEXT("ef34155b19f273ee8a86602f4ff9f566d2092c9c6264a0325aaf35ac9d5bd346"),TEXT("cd3ef78645f7797b2719656742c95a6ecb3478426129116e84a7928198318a76"),5768u,false};
  P.Frames[0].Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearArmWithoutHand_000_v001.T_Fairytale_Hurt_NearArmWithoutHand_000_v001"),TEXT("753eacc1a1970d7b31d372acc7485724d798c1dffa1b0105c4a8f0587e40a42b"),TEXT("1436bbdc3489e53a83bb178dee744d03deb401800ae496152f9aa01b6b4f69f3"),4327u,false};
  P.Frames[0].Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderNear_000_v001.T_Fairytale_Hurt_ShoulderNear_000_v001"),TEXT("4041224c3893203158e7636625e90e95307b636f5a2c7f220abd795a4b34758d"),TEXT("d5403f284ea759276eb34bfe76ba11d14ab85e82e1e8e56c663557de2febb5e6"),1680u,false};
  P.Frames[0].Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_HelmetForeground_000_v001.T_Fairytale_Hurt_HelmetForeground_000_v001"),TEXT("f9fcccc43aa00a96a83f832720a9b14299e5264a4bcf09f9d943f978680a3c26"),TEXT("6756c30119e4ac476766fbbf498953026acd160ae3a6ad776a5bf17e3be17168"),19853u,false};
  P.Frames[0].Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_FarHandForeground_000_v001.T_Fairytale_Hurt_FarHandForeground_000_v001"),TEXT("79c0ec92f8774904027633d70aee3ca4efd6ea805b72d1c22b83a416c47b100d"),TEXT("fca76738d9cdef18f18ccadef7b15b0059732739a00bea3b067efec58dd7d990"),1759u,false};
  P.Frames[0].Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearHand_000_v001.T_Fairytale_Hurt_NearHand_000_v001"),TEXT("27dd72f81f74d52a7470907996237b36044aaa142113432d4f76a912b3aea2c8"),TEXT("fd0498cf0197fb2fa54846217a2e0a9792140ee3a24f0a156f9107bf19398935"),2536u,false};
  P.Frames[1].Frame=1;
  P.Frames[1].Root=FVector2D(283.3389315213614,464);
  P.Frames[1].Grip=FVector2D(194,289);
  P.Frames[1].AxisArtist=FVector2D(0.8,0.6);
  P.Frames[1].ExpectedNonemptyDrawCount=8;
  P.Frames[1].Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_BodyRest_001_v001.T_Fairytale_Hurt_BodyRest_001_v001"),TEXT("1fb4f59715d6073359b2926d56ab285a36e068e455a3f7b76ce874d140474687"),TEXT("7e5dc4aefe49a4e146ab4468c81ca4324c051e87b81fe953255c56e755d7d5fe"),43796u,false};
  P.Frames[1].Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderFar_001_v001.T_Fairytale_Hurt_ShoulderFar_001_v001"),TEXT("040fcf0010d7cfd029769112448ea253d384edcd7a5035e9f1e73e8e6dfc620b"),TEXT("cb1251dee3177ce693c928f840aebc80c0c10159200634f7c4d618f484ccb147"),356u,false};
  P.Frames[1].Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_Chest_001_v001.T_Fairytale_Hurt_Chest_001_v001"),TEXT("22f478541997a36fe3d261de930c5a56c6282077b25daf98795e0c53a8cb8046"),TEXT("ab37a7754762d1ada300153ad2b75c091d2eed9c0c7f3be113a5c2a82d8b78f3"),6980u,false};
  P.Frames[1].Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearArmWithoutHand_001_v001.T_Fairytale_Hurt_NearArmWithoutHand_001_v001"),TEXT("ee613be1d4872aa5236049452e9965187974ee59c21ac1f3d84db490604181f7"),TEXT("5d78ef2dbf04ac868a5664c0395b051cbf5b17f291178d18c113dec3269c3e7f"),2471u,false};
  P.Frames[1].Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderNear_001_v001.T_Fairytale_Hurt_ShoulderNear_001_v001"),TEXT("7d726a7fcdf1e96ce933dd57fb715d29b02e44b157885219b5f128766b305e61"),TEXT("66fd9b7cd76771ffc115c7edab00f647f07036a66c284126047ee038b05f1620"),1515u,false};
  P.Frames[1].Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_HelmetForeground_001_v001.T_Fairytale_Hurt_HelmetForeground_001_v001"),TEXT("cf23448723916446f8ccd8cc1ddd06e5daa53be2082a98f0bd399b4e491ec05a"),TEXT("0934b9944becd7bca132c6a1c0e7e516a104a1d2748045ac034de910ef554c82"),18010u,false};
  P.Frames[1].Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_FarHandForeground_001_v001.T_Fairytale_Hurt_FarHandForeground_001_v001"),TEXT("b262bd68d44f93637b9949caf7ff7ce0b6b6ed839c3a2468681952b215ec4d95"),TEXT("30e14955ebf1352266dc2ff8067e68104607e750abb9d3b36582b8af909fcb58"),0u,true};
  P.Frames[1].Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearHand_001_v001.T_Fairytale_Hurt_NearHand_001_v001"),TEXT("51f359f1bcfe662ac5faa84dbf2a35b94d0d6673b643caca40753f590890b18b"),TEXT("8aa763df24c6f0966c25820db57a302ec8025e07ede7a1395ab2f3d1f0006008"),2892u,false};
  P.Frames[2].Frame=2;
  P.Frames[2].Root=FVector2D(247.06828334586936,464);
  P.Frames[2].Grip=FVector2D(205,289);
  P.Frames[2].AxisArtist=FVector2D(0.96,0.28);
  P.Frames[2].ExpectedNonemptyDrawCount=8;
  P.Frames[2].Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_BodyRest_002_v001.T_Fairytale_Hurt_BodyRest_002_v001"),TEXT("8f99443929bd0984f0e5cdaf315cee8069eba1ba68096cd5d6bad33476b4690e"),TEXT("b236adff8abc3582dded0f9f09428a5e6e0434ad4760b10bfe01dc46ac74e136"),33606u,false};
  P.Frames[2].Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderFar_002_v001.T_Fairytale_Hurt_ShoulderFar_002_v001"),TEXT("8ce7e527081984c39ac49e607f1498d817309cf45ef97cdee16fcc5cb2695d08"),TEXT("aa777dfcd4bea80982dd85cf8214b07ac5a87b8294540545d16b5f8f982408e5"),359u,false};
  P.Frames[2].Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_Chest_002_v001.T_Fairytale_Hurt_Chest_002_v001"),TEXT("127bd4db3736950349947f9865b7063ded24b7883578e831b685d99857ea5693"),TEXT("bf7eb8cec12c65f9346af3652f6551fa5d7252ddd3f2f4651c337f409a01e1c4"),6294u,false};
  P.Frames[2].Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearArmWithoutHand_002_v001.T_Fairytale_Hurt_NearArmWithoutHand_002_v001"),TEXT("022703331024b472ef466f71f6ebbb89f2663df6e9b07750b828fd5c55babd94"),TEXT("6073e0efff658c53ce029848ce9bf4174d49648161c0a9cffb1ffb9511cfe52d"),3175u,false};
  P.Frames[2].Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderNear_002_v001.T_Fairytale_Hurt_ShoulderNear_002_v001"),TEXT("094310835f9e49eb2cfb645c2bb988ac763dcc9c91d3aaa5d9eebe80b31d926a"),TEXT("fa4ef3fcbae985b8054573f57d6507a25cb35ccafcc6b480b259fd99528c0586"),1717u,false};
  P.Frames[2].Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_HelmetForeground_002_v001.T_Fairytale_Hurt_HelmetForeground_002_v001"),TEXT("49d925efe0a808c4914437be52b7d15599e4d3f5c040105420dc4f254b6490a3"),TEXT("8b2a4c9e3ee1660f4cd77e6db80392ea1887bbab93d872a63d089771b5f8b021"),20925u,false};
  P.Frames[2].Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_FarHandForeground_002_v001.T_Fairytale_Hurt_FarHandForeground_002_v001"),TEXT("b262bd68d44f93637b9949caf7ff7ce0b6b6ed839c3a2468681952b215ec4d95"),TEXT("30e14955ebf1352266dc2ff8067e68104607e750abb9d3b36582b8af909fcb58"),0u,true};
  P.Frames[2].Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearHand_002_v001.T_Fairytale_Hurt_NearHand_002_v001"),TEXT("afd007b84a4602e60c0d79654ec0d07633502069dda6957e822a11100c9afc0a"),TEXT("e83955067a383e6b1967d4eca380c2eabaeb5cf2831819a03fe25252127fcf79"),3084u,false};
  P.Frames[3].Frame=3;
  P.Frames[3].Root=FVector2D(252.4471254026009,464);
  P.Frames[3].Grip=FVector2D(218,303);
  P.Frames[3].AxisArtist=FVector2D(0.94,-0.341);
  P.Frames[3].ExpectedNonemptyDrawCount=8;
  P.Frames[3].Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_BodyRest_003_v001.T_Fairytale_Hurt_BodyRest_003_v001"),TEXT("dfe2858525cdce9d4ebf8f69e34b5699dd7212e1c13af8f95d26da7c35bb75e7"),TEXT("0db8b27bef95a61e67668c3af4385c41bf5ad8d00d305bdc6eb545c9e32afcb1"),34488u,false};
  P.Frames[3].Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderFar_003_v001.T_Fairytale_Hurt_ShoulderFar_003_v001"),TEXT("3c7e2d9afed494b4ccff3ef7375bc9a5406f9b921ba13e7f519233dfca80fc8f"),TEXT("0a5d4d5f58709823acb649923fe5fe7ac975c73a992dba3c9eb9ec931371c548"),370u,false};
  P.Frames[3].Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_Chest_003_v001.T_Fairytale_Hurt_Chest_003_v001"),TEXT("641aaca5b423fed9afe90d1645e34b727fbd45d4786f41aa0f1b82a28dfeb277"),TEXT("48e0e612010058fe8a4fd9a4fbfcffaa7d33c8170e670c26ba52bc5f94efa695"),6874u,false};
  P.Frames[3].Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearArmWithoutHand_003_v001.T_Fairytale_Hurt_NearArmWithoutHand_003_v001"),TEXT("fd0a647900cac5e4cb07ff0dea5447de9f44b7f4703724490e8221f2e9270f8b"),TEXT("ce40d9a34de0b764a7b13056b00dac6750d254d89fbadf52b7d6e3ee856a043d"),3316u,false};
  P.Frames[3].Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_ShoulderNear_003_v001.T_Fairytale_Hurt_ShoulderNear_003_v001"),TEXT("5fde262bbfa32a9d98a2474ee2834fceb4f640af1cf9939c448dc4d79e06d8d2"),TEXT("442765da4101bdf1f397cc0eff8aceebacc6645a1aff7deec715a861323054fc"),1667u,false};
  P.Frames[3].Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_HelmetForeground_003_v001.T_Fairytale_Hurt_HelmetForeground_003_v001"),TEXT("61484c4aed6d7129fc2f90a035c05e4ba94746865ef9ff4d3b2ac6369c2e6c41"),TEXT("b565fbcc45b596850ba1e9b5a249cdfb3d2bd8f0f73815a04405c446f48c5113"),19085u,false};
  P.Frames[3].Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_FarHandForeground_003_v001.T_Fairytale_Hurt_FarHandForeground_003_v001"),TEXT("b262bd68d44f93637b9949caf7ff7ce0b6b6ed839c3a2468681952b215ec4d95"),TEXT("30e14955ebf1352266dc2ff8067e68104607e750abb9d3b36582b8af909fcb58"),0u,true};
  P.Frames[3].Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/T_Fairytale_Hurt_NearHand_003_v001.T_Fairytale_Hurt_NearHand_003_v001"),TEXT("4341af407c770581d5a220300565a0dbec406cc896473f08025b17d86a77bb4f"),TEXT("7ca260c24de1adc656cf5a22fabaf4d7bc7bb02b57caa4def491c28ba315d7a5"),2642u,false};
  return P;
 }();
 return Value;
}
}
