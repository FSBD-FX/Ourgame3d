#include "DungeonFairytaleSwordDeathProfile.h"

namespace DungeonFairytaleSwordDeathV001
{
const FProfile& Profile()
{
 static const FProfile Value=[]
 {
  FProfile P;
  P.ProfileId=TEXT("fairytale-SWD001-LGT001-Death220-LGT237-239-author-v002");
  P.SourceClosureSHA256=TEXT("5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c");
  P.SourceClosureVerified=true; // Exact E505 source closure, not import/native/final acceptance.
  P.SwordTexturePath=TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002");
  P.SwordSourceSHA256=TEXT("2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a");
  {
   auto& F=P.Frames[0];F.Frame=0;F.KeyAge=0;
   F.Root={242,464};F.SwordAnchor={183.0,311.0};F.AxisArtist={0.93969262078590843,-0.34202014332566871};
   F.VisualSwordReleased=false;F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_BodyRest_000_v001.T_Fairytale_Death_BodyRest_000_v001"),TEXT("d74e7fad4c2432cc873ffefc37f69dfb809ed49e2982aa2a78f2aa658f9c8b7a"),TEXT("9f72e758f78372ae9798b6e89822ca825a23894d4cd3904819a5707d815a787a"),30593u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderFar_000_v001.T_Fairytale_Death_ShoulderFar_000_v001"),TEXT("ea0de1561352734edb2b27671295c765194df21003ec8171b9d9ad8e069ec84f"),TEXT("944733d50d66005d50c383a2f853ae9266cfb70253d05a450a8b952b87d546ed"),573u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_Chest_000_v001.T_Fairytale_Death_Chest_000_v001"),TEXT("8d5ec4c22254581eceae408012c59c0a43784fef161d441bc9fcfd9a461cc09e"),TEXT("34135d520466bed07b9d64f2b5afe03182b132cf64517bf6190214f7aec1f704"),5926u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearArmWithoutHand_000_v001.T_Fairytale_Death_NearArmWithoutHand_000_v001"),TEXT("821da45e5e6dd83526bb954b9a5b9248d25ec164bdba505af2961a4f535f9876"),TEXT("540511bedecb692954e2fef170693fc00cf5d3bc035a798b777feb9fad88d958"),2866u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderNear_000_v001.T_Fairytale_Death_ShoulderNear_000_v001"),TEXT("9b0e6e46e1223f91639d6a26b29b44393445961394f84165894288bc3fb1cbcf"),TEXT("988a3cd64322836b77800aa74c4997648cd28135e0a7a6937fcd5aa73ffd3a9a"),2196u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_HelmetForeground_000_v001.T_Fairytale_Death_HelmetForeground_000_v001"),TEXT("7d71875531402268f8669f7d6018381a39b50c0639634b88ed6a3e76334eb29e"),TEXT("b43a709f943ad2bc14cb136a539f6132c3c56ff9ca80028bac644b0c9dca7764"),20484u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_FarHandForeground_000_v001.T_Fairytale_Death_FarHandForeground_000_v001"),TEXT("1c48b63178ea43e2eab725493307f09233e4d4608d5f3a6b73052c94a1a5cd36"),TEXT("f1dcb28ef9aa289740d2196f24c3fb8a3329932bc17830091d0a5b835025cdea"),2675u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearHand_000_v001.T_Fairytale_Death_NearHand_000_v001"),TEXT("2c518111523077ed0d09fce1529ff91e5f0af0e6062efee50362ae0177c28db9"),TEXT("4995979393826fa61c98997204d526b9e1b97bffb3c95d166edcac2ca581f6c1"),4118u,false};
   F.SlotOrder={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::IndependentSword,EComponent::NearHand};
  }
  {
   auto& F=P.Frames[1];F.Frame=1;F.KeyAge=0.20000000000000001;
   F.Root={242,464};F.SwordAnchor={296.0,430.0};F.AxisArtist={1,0};
   F.VisualSwordReleased=true;F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_BodyRest_001_v001.T_Fairytale_Death_BodyRest_001_v001"),TEXT("5bc6d34e64de4a2dcf9d2e0c8270a47d4a5d3a05d76bc5c72ceec0a46b71e824"),TEXT("79d48f60ae124cd9a821a9532e13430dd1d912a803846bd1dc8c64f24d786732"),28419u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderFar_001_v001.T_Fairytale_Death_ShoulderFar_001_v001"),TEXT("effe947a699734539452ff37fea747754ac41f9d12a21c03e30db63609f9d9c0"),TEXT("17b6463afe3380b47a7c65c25123d81b9ee7a95af0358796b18d23d80f643118"),571u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_Chest_001_v001.T_Fairytale_Death_Chest_001_v001"),TEXT("0fe0efcec01a08985ed9cf26b8f2b0714fbbd93512bc3aa4b7eb0662a8396afa"),TEXT("1db378bb69eae7c70b0bdc47f359327e37e8638c01a7620223e183e52c943fb4"),5926u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearArmWithoutHand_001_v001.T_Fairytale_Death_NearArmWithoutHand_001_v001"),TEXT("bd5288f0f028f9b4f5523203292b65684568138b8deb418e85c769fca60fe16d"),TEXT("c34d5ac2391bdcae38abb98c0c21c6677b44107918c312a7700bc8490a20bdf8"),3429u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderNear_001_v001.T_Fairytale_Death_ShoulderNear_001_v001"),TEXT("ec68bc10693d50ba3d4e9ec737dea5cf0b6ef93b0ac72d3f5aff5686e10ec7c3"),TEXT("31fd78b3e031cd0a5e3fd04ec8447c26e6b50677dc92b184377c750a9bcd1bad"),2049u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_HelmetForeground_001_v001.T_Fairytale_Death_HelmetForeground_001_v001"),TEXT("4afccbd3e05656e53042b0cce8a7b0eadb87ede219a9d249f0b1927834e57dbc"),TEXT("198ca3f27671b7013a8373b9d44ac2b04264aad359be93c7c1c690d54877bc56"),19937u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_FarHandForeground_001_v001.T_Fairytale_Death_FarHandForeground_001_v001"),TEXT("0f20af90e43c55ea6292d7c37eb04a30a8912b9b72e63ee93415c44c3bda36d2"),TEXT("55a0bffecbbb3dac61d854a83c227faca6204e3b477362b46f37cb0fd9f16780"),2926u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearHand_001_v001.T_Fairytale_Death_NearHand_001_v001"),TEXT("d224104ae90c09b275300ea21e704c698581035291be09b79c15d420efb2c1a3"),TEXT("597c6e36d2b835007df198bf8a26ad674f632d08e12f4f516d0cd908a6d7c3f8"),4146u,false};
   F.SlotOrder={EComponent::IndependentSword,EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::NearHand};
  }
  {
   auto& F=P.Frames[2];F.Frame=2;F.KeyAge=0.40000000000000002;
   F.Root={242,464};F.SwordAnchor={480.0,442.0};F.AxisArtist={1,0};
   F.VisualSwordReleased=true;F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_BodyRest_002_v001.T_Fairytale_Death_BodyRest_002_v001"),TEXT("6ec0e5456dfe32d088444136f630d15a18bfee9957bb43bf0a6baec1de7176e5"),TEXT("927032bd2b23ef4b9d5c08367ce2a8f28b300a501520ff68245111a74a82497d"),23117u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderFar_002_v001.T_Fairytale_Death_ShoulderFar_002_v001"),TEXT("a20a38491e76188e22b4350a44dd55bf1cb5d1c6127a920e10a79eebc31b97a6"),TEXT("59e25b77b20be0d5dfb3c8edb12c0404b153ad4d6bc9e6d21db432af9da9c9b6"),582u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_Chest_002_v001.T_Fairytale_Death_Chest_002_v001"),TEXT("643daec1834f2c1869c863d8250d03817400c02ff04bb40af0e2c3bf97bd5010"),TEXT("df665b4df724c8e02d21d0f172aad23edefadb8b5fa47f4b58defaf6f79e5b5b"),5353u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearArmWithoutHand_002_v001.T_Fairytale_Death_NearArmWithoutHand_002_v001"),TEXT("c203c6beaa11975f26bb6558d02b82e8687bd6b72f5befaacbda12c1b83aa6f7"),TEXT("869eed30db633e87e5ca0d9a18f2d9b7a62d06a2a2b547d8f6bcdf2b889635db"),2608u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderNear_002_v001.T_Fairytale_Death_ShoulderNear_002_v001"),TEXT("0cacb1a553f772adec5878db5b86b0c91755ef0431824583375b0c68ec883401"),TEXT("3d6627b9e2f8b74a4cdc1280f88ddda81d0c01e386e5455643d32260c41913cb"),1934u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_HelmetForeground_002_v001.T_Fairytale_Death_HelmetForeground_002_v001"),TEXT("a2d44d3c84f90f5360914507785878b803e0f350e129089237f4db2b2d09d567"),TEXT("a6080a430d5617e050c3f47e110f9c67a3faf0b8e2c68697b7e11e07d0db0aa1"),20761u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_FarHandForeground_002_v001.T_Fairytale_Death_FarHandForeground_002_v001"),TEXT("b8eb048cd2d6d9347cd47e8fe868bf46bd7bf78d815419c7d2d3bc09a7fa4892"),TEXT("ecd1d62b55d642c86e948f5f373577f7409f99c72e69a687c2ed7874770cdb31"),2927u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearHand_002_v001.T_Fairytale_Death_NearHand_002_v001"),TEXT("a9679776466e7aa17e0a5c6e4e5a38c497e645f39726ae914e2e5a82335a5ed3"),TEXT("800a25d9c6eb2a7dbec9172e9de88adea1fbbd6f9ffabde81028fd1dd9424099"),3763u,false};
   F.SlotOrder={EComponent::IndependentSword,EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::NearHand};
  }
  {
   auto& F=P.Frames[3];F.Frame=3;F.KeyAge=0.59999999999999998;
   F.Root={242,464};F.SwordAnchor={480.0,442.0};F.AxisArtist={1,0};
   F.VisualSwordReleased=true;F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_BodyRest_003_v001.T_Fairytale_Death_BodyRest_003_v001"),TEXT("013a0a4e8f45adbde8542984a9abb6460d02df8f4a23ce8085d47eab770aaff2"),TEXT("3f6c9d7cad80b5de2ad519138fa4a6cf9acf381a26d100b9d456e23f456ff85a"),16142u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderFar_003_v001.T_Fairytale_Death_ShoulderFar_003_v001"),TEXT("259cd45d21b0932c964b85828babad6bb8ca4f7788e1e7632da23251576eacca"),TEXT("af63b990fd0d61fdcf945b93dbc5467d646c80cbdd9bb2944e15c0d93bfcd46b"),498u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_Chest_003_v001.T_Fairytale_Death_Chest_003_v001"),TEXT("1da038ed312be4d4e0850147faefc76de0c594d67316cfcfbae6247d90ad2cc2"),TEXT("99629116bd25cda750ef40bac9f58cfc768800030d21269d74603c547ead93e1"),4676u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearArmWithoutHand_003_v001.T_Fairytale_Death_NearArmWithoutHand_003_v001"),TEXT("b09b80a2970e3483f7990fb2b2079111eb21a50fb0672db2f52cc35368b12252"),TEXT("5cc60635b24a5edb6fd9cedab8bf5ae3f0b8f668f0904337a140037c452647ec"),3029u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderNear_003_v001.T_Fairytale_Death_ShoulderNear_003_v001"),TEXT("769b49a4429528889c9fd092e8e21a6533bc09802b08f7a2b53da8b70251f702"),TEXT("98e287d3a5cb219cb75ff283f07a49f631ecb9daf579e0bd2ff2ac64cbdc8972"),1765u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_HelmetForeground_003_v001.T_Fairytale_Death_HelmetForeground_003_v001"),TEXT("8583b91731d2b06076ee09ef037897b0109fc78cf016fe96b7705529e3b5f3a7"),TEXT("80ee6337775c8433a1957c396431130688ab985f1c0b108ca887c7c363b4c724"),19446u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_FarHandForeground_003_v001.T_Fairytale_Death_FarHandForeground_003_v001"),TEXT("9c2867f30fb25e30c8013befc6f32c02882afc54ebbcef2ad3ffc576bca272a0"),TEXT("f60f66f162da0190564ba8e4bf5d5590826169eef5ddf325c6b8c0fd5154ee22"),1499u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearHand_003_v001.T_Fairytale_Death_NearHand_003_v001"),TEXT("cf186c03faec51369aa8772d116d7a1147985828f01a18d8aa0d8946588dbb74"),TEXT("bfe69c06f07b216e943e0e499ee79d8d23760c94eaea557ca2d7f0df02794dfc"),3855u,false};
   F.SlotOrder={EComponent::IndependentSword,EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::NearHand};
  }
  {
   auto& F=P.Frames[4];F.Frame=4;F.KeyAge=0.80000000000000004;
   F.Root={242,464};F.SwordAnchor={480.0,442.0};F.AxisArtist={1,0};
   F.VisualSwordReleased=true;F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_BodyRest_004_v001.T_Fairytale_Death_BodyRest_004_v001"),TEXT("d1b82a5a7c2278d68db644bcd966ff8260f530191d435206592f81ee960258c8"),TEXT("311afa2ce5d20b92ceda49af7dc3650578453465911bb5965822a4788bf5cb6e"),14013u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderFar_004_v001.T_Fairytale_Death_ShoulderFar_004_v001"),TEXT("7ddf4db5790e33ce40682c69b7909d2b48d042d0a118f843f0cbeb2e08e116fe"),TEXT("f90355dbb648ca0c32533b87e070e755527158c947f6bb0394d5a183199b9bce"),381u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_Chest_004_v001.T_Fairytale_Death_Chest_004_v001"),TEXT("04699cf0b29bb5bd460eb130e9acd6298eadc6b7ab2030a9efe46dfb415680f4"),TEXT("61cdee3039f1f953b97809b6265f9ab1f0739643a20a222e01bb9da48d6797ca"),4469u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearArmWithoutHand_004_v001.T_Fairytale_Death_NearArmWithoutHand_004_v001"),TEXT("06bc51a43a305ae929ce227b90501119fdcaa7556d9d0fa6cd5a237edcad080c"),TEXT("a5a12869b9a5a3fc4cdde1831700c8403238c0677d7702e669234fffa2757895"),2771u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_ShoulderNear_004_v001.T_Fairytale_Death_ShoulderNear_004_v001"),TEXT("fccf163a5b5f03794e1fb479ea3a9ff6582099b949af69f9f13aece638be8850"),TEXT("a871f2e062a62dc357551feea993778978ca3dc0c265228dff6b4a44f1491c28"),1819u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_HelmetForeground_004_v001.T_Fairytale_Death_HelmetForeground_004_v001"),TEXT("e279d4fb49cd6bcd60ec374ce06715b1ae41561506b48f990bb58b90d09668f7"),TEXT("822e7a54e187ff628f4b41610f8f70d812802e94909ba8bce7737c6a78901a81"),16469u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_FarHandForeground_004_v001.T_Fairytale_Death_FarHandForeground_004_v001"),TEXT("cf7f26ef2b9b839aac11b3c63e20af0807d94814b597e9aeb136f2eae6ac469b"),TEXT("7fd70105728568f9477619b06c73d947ee39d7e225ca056522276ba52ad632b6"),1402u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/T_Fairytale_Death_NearHand_004_v001.T_Fairytale_Death_NearHand_004_v001"),TEXT("9b4ee26fd9679f273a7e0451513e72d9f45265cec6eb07f1044f50c4e97e2bc4"),TEXT("7d1baf1be06497d1311f728ff89e6f52eac09bd522b1dd32c8722d32728d5f06"),3787u,false};
   F.SlotOrder={EComponent::IndependentSword,EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::NearHand};
  }
  return P;
 }();
 return Value;
}
}
