#include "DungeonFairytaleSwordDodgeProfile.h"

namespace DungeonFairytaleSwordDodgeV001
{
const FProfile& Profile()
{
 static const FProfile Value=[]
 {
  FProfile P;
  P.ProfileId=TEXT("EV048-v018-HeroLeatherDodge-v001");
  P.SourceClosureSHA256=TEXT("7b62e4e15616c8ada14826ab926361e9a78666f78639eb0e253fbaca50727097");
  P.SourceClosureVerified=true; // Actual retained preparation only, not GPU/native/FinalAccepted.
  P.SwordTexturePath=TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002");
  P.SwordSourceSHA256=TEXT("2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a");
  {
   auto& F=P.Frames[0];F.Frame=0;F.KeyAge=0;
   F.Root={234,464};F.Grip={196,307};F.AxisArtist={0.80000000000000004,0.59999999999999998};
   F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_BodyRest_000_v001.T_Fairytale_Dodge_BodyRest_000_v001"),TEXT("250a2ff18b86a4f2fca92c3a260195f89efe0dc5369a8367584e2d8c0405796f"),TEXT("1ebbf8f74c35520006fcd9c18892fb16551ac08aaca4a861a7de32ba9df16c4f"),33855u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderFar_000_v001.T_Fairytale_Dodge_ShoulderFar_000_v001"),TEXT("13981e9572b82eaf008bd6ab5c8e47a3800f63319432c3b0bc7ae373d55adec2"),TEXT("2f07143ee371b34e4f36584b2534664fb5156273976b437bac463fe4895b2950"),383u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_Chest_000_v001.T_Fairytale_Dodge_Chest_000_v001"),TEXT("050d275f2c254384440210b256b733f1642c89c6a7921b9d0453349a1f37675d"),TEXT("ca2e0cf76ef5b3ad37f6cae21165f6131e1536d057fb11b90b57ef848b98da14"),6568u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearArmWithoutHand_000_v001.T_Fairytale_Dodge_NearArmWithoutHand_000_v001"),TEXT("b9b8c3bd09d937e729f2fc4f8e2d7e829426a3f3a4a575786638381920e17cef"),TEXT("99aac235e0548925ddf10a3f8b55fe2f114395a41de0072c2fc665bd4df5659a"),3637u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderNear_000_v001.T_Fairytale_Dodge_ShoulderNear_000_v001"),TEXT("0ca900fc057fa0d5691c7ffb3211ad13cd5d10227bde6d1436ae13594b51cdf8"),TEXT("c69289c2682761676495d3a35b6955b5b0256c6d0a4fb8682e0d149d4a894dc9"),1583u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_HelmetForeground_000_v001.T_Fairytale_Dodge_HelmetForeground_000_v001"),TEXT("f5f4cc46cfc8cee082a3b1ff2277292f766c7395ce9d577299f59ade18935c64"),TEXT("d07fd4fb20f087ce8b221f59ad666d30a6db7c985343d17b26988df6cdd0c4b3"),24728u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_FarHandForeground_000_v001.T_Fairytale_Dodge_FarHandForeground_000_v001"),TEXT("0919bc0539870f129b5899637089c59b0d9c497a9fb17bfcd1bc1c59d0aeb1c7"),TEXT("e24b8a7f2feb7a14c5a2d8a83dbbfa0de32eae9f121f01408da4ec8d9a8238cc"),3479u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearHand_000_v001.T_Fairytale_Dodge_NearHand_000_v001"),TEXT("829af3ed97cfae0a5c13ee4ad6aee238746942244ab08d455897ebfb5d695186"),TEXT("777c5166ee85461429fe7da87770b7c7827707aa01a4aaf94a5079ade77c294e"),3207u,false};
   F.SlotOrder={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::IndependentSword,EComponent::FarHandForeground,EComponent::NearHand};
  }
  {
   auto& F=P.Frames[1];F.Frame=1;F.KeyAge=0.10000000000000001;
   F.Root={216,464};F.Grip={159,324};F.AxisArtist={0.87998900020624571,0.47499406261132576};
   F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_BodyRest_001_v001.T_Fairytale_Dodge_BodyRest_001_v001"),TEXT("ef1f0ec1a103baf8ce266f2e805acbbb5795e830ffdeea12ab227be8e5301464"),TEXT("973e16e6f073f61eae57ed92615b3eff1753705cad75ecf042d0bc34b91f67cb"),30318u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderFar_001_v001.T_Fairytale_Dodge_ShoulderFar_001_v001"),TEXT("085ea7eec7b06022b1c7ae56e2d2637a08f0839c0332f1180324e6f0c3da820b"),TEXT("cfd697fac5b551c36da593c00250fbe8c7401228d65fba4ea5dca2bc0049261b"),263u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_Chest_001_v001.T_Fairytale_Dodge_Chest_001_v001"),TEXT("f6f2a9de51a51f991e6fea08c38ac4188dd0a15cdd98ceffb040fdab5109aa94"),TEXT("78656792e2e8127b8af254f89580cc8c099818e11793775fc22daaa89cad3f1c"),7005u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearArmWithoutHand_001_v001.T_Fairytale_Dodge_NearArmWithoutHand_001_v001"),TEXT("337c79324fc554467c4eb90e6bd4f7e4d428ba58c79f47702ca44a9e954a6f47"),TEXT("9ba4b61512974a9d21a21b5c1b60d88a79b1b01f4f3869e053aa1e6d47817750"),2511u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderNear_001_v001.T_Fairytale_Dodge_ShoulderNear_001_v001"),TEXT("ab340141e36f67d0785e5f2f4b7a38308525e63628c7802273ffde62f4e5902d"),TEXT("06cc0c5ea29cc71345a00dad1218dbfab26520d126bd79b4e29402fa217aa6b8"),1540u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_HelmetForeground_001_v001.T_Fairytale_Dodge_HelmetForeground_001_v001"),TEXT("4d93a957fdc4387f332ab4b3f1db2646bfc27108da729f32466f1d59d3c60c81"),TEXT("a110bf97386020736d0d08aaba5346c52911850254ef6159b89fb31fe4e65066"),25692u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_FarHandForeground_001_v001.T_Fairytale_Dodge_FarHandForeground_001_v001"),TEXT("9dd047229051068dc5abae53a7adedad7cb1373636b4c1ca7968dbf1880a7a1f"),TEXT("1885ae2eec06204ada35b9a9d9834f63e16f36ba9cb2a276562b8b1ffc031b50"),3595u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearHand_001_v001.T_Fairytale_Dodge_NearHand_001_v001"),TEXT("da0eebe6953786f686bbd8ff70060b91229a8dc6566399bf5da7dbda1e019fdd"),TEXT("f85209b67c77a26b50d081c19963cef7072420c2d8ae485c976ffd42e8243cce"),3493u,false};
   F.SlotOrder={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::IndependentSword,EComponent::FarHandForeground,EComponent::NearHand};
  }
  {
   auto& F=P.Frames[2];F.Frame=2;F.KeyAge=0.20000000000000001;
   F.Root={227,464};F.Grip={158,305};F.AxisArtist={0.94005593499224749,0.34102029131101746};
   F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_BodyRest_002_v001.T_Fairytale_Dodge_BodyRest_002_v001"),TEXT("62c00afd8312c8e8c5e3a8f77cae83c3f41a929835a0fddf577abd0e647d8438"),TEXT("c336c6547ccca0a6a3947bf6763474a035e9fce00fc6c96b5c8080ac747161da"),35213u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderFar_002_v001.T_Fairytale_Dodge_ShoulderFar_002_v001"),TEXT("dcab5eb5848fcb1ff50c1184445d98e5a7c74e40f1110fae80a411d9f4c19ffc"),TEXT("25e4138c8fb06a10f6f4a61b1d7189f99d4643f4c4e9e960dc7e49f6e6a1230d"),399u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_Chest_002_v001.T_Fairytale_Dodge_Chest_002_v001"),TEXT("c89ddc3a2bef82730c56c4746688c348611e84dcfa43dd444c1195d0ad8c074d"),TEXT("025357d4e4df1588ddf2e14ee99d392c917a285c9c2d9dce54609bf283329c79"),6881u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearArmWithoutHand_002_v001.T_Fairytale_Dodge_NearArmWithoutHand_002_v001"),TEXT("7e9bfa1aae1280500b4e043e83c9eca96d2767ec4ded8abad70005a9cbd7d7fa"),TEXT("6c90d767632fbd2c053d0ea701182330a9ba511d435997b0639946a307d5fca0"),2653u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderNear_002_v001.T_Fairytale_Dodge_ShoulderNear_002_v001"),TEXT("24c0e9439f2f3d52744a0fa162b00f7b59d9a8526d199fd1cef19febee64e8e7"),TEXT("f843d28071b8bd363901b1be1b0ad828ff17c8222f6fb16c64e11eee7afd3681"),1643u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_HelmetForeground_002_v001.T_Fairytale_Dodge_HelmetForeground_002_v001"),TEXT("e7ff6d0b449addc8a80ec5dfb159beb73cbeebb2bbfdf6a28bf41edca20b0193"),TEXT("9a2c09663671c2e23c0c206088b465327b6e85895d50f888c1e78267d92ac01c"),23711u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_FarHandForeground_002_v001.T_Fairytale_Dodge_FarHandForeground_002_v001"),TEXT("a7c3a5aa50de53a73f5df9119e073b95de9af5be69cfd353c49e4b2c333cc595"),TEXT("cab34af257f60d066390de60517a914bdab6376d1a2fdd4626b736e81a69f331"),3722u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearHand_002_v001.T_Fairytale_Dodge_NearHand_002_v001"),TEXT("162220e5f5dbd3ac97d13c3a831605ff004f8a022bc223300e4561aabc65fa7b"),TEXT("2dbd7d47c044032d41c3410b56810261afcd83c81d43aa07b9765693895c7050"),3626u,false};
   F.SlotOrder={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::IndependentSword,EComponent::FarHandForeground,EComponent::NearHand};
  }
  {
   auto& F=P.Frames[3];F.Frame=3;F.KeyAge=0.29999999999999999;
   F.Root={247,464};F.Grip={188,293};F.AxisArtist={0.95999999999999996,-0.28000000000000003};
   F.ExpectedNonemptyDrawCount=9;
   F.Layers[0]={EComponent::BodyRest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_BodyRest_003_v001.T_Fairytale_Dodge_BodyRest_003_v001"),TEXT("9edd39a26d52e9a962d0d55970aff824e03c74c19a4c7c901eabed2f4ee65e80"),TEXT("a86ef68aeec8164a0bbbb7a0ed872110de00300b258a5b33a56683c2d517e833"),37331u,false};
   F.Layers[1]={EComponent::ShoulderFar,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderFar_003_v001.T_Fairytale_Dodge_ShoulderFar_003_v001"),TEXT("3e8f73fcade0b5d3e33b83493b43ebb41bb9e56f295f91fa1f194ba9d89403b2"),TEXT("b410de1327ed0d88b1d9bae2c622ed739d819472edbb63a4ece83848cb77ff6b"),397u,false};
   F.Layers[2]={EComponent::Chest,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_Chest_003_v001.T_Fairytale_Dodge_Chest_003_v001"),TEXT("30c6c66756a5d1559e28e5855b226b0297e6b39c82a7287996bf481d30d5f981"),TEXT("6487869e1a6a774d405d56e78c0c8c3141330d76c8343ca4e4d410e47958ea2e"),6556u,false};
   F.Layers[3]={EComponent::NearArmWithoutHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearArmWithoutHand_003_v001.T_Fairytale_Dodge_NearArmWithoutHand_003_v001"),TEXT("2c366bbe43a5bbedfa794cc535f6ecdeb13f7c960d7a8998df4232d1aab7c11f"),TEXT("6a79affdbeee15571f7548138dd6cc02e589a8d13bddfaf65e4f3319c4e1d8a6"),2540u,false};
   F.Layers[4]={EComponent::ShoulderNear,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_ShoulderNear_003_v001.T_Fairytale_Dodge_ShoulderNear_003_v001"),TEXT("8fe637acbd349198ea31861482ba937b2b713125071e44fbce412d8f911f8c11"),TEXT("46c69a2c583509c910f7446e9efa5102fcdff708979681679e70e40292958809"),1714u,false};
   F.Layers[5]={EComponent::HelmetForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_HelmetForeground_003_v001.T_Fairytale_Dodge_HelmetForeground_003_v001"),TEXT("2a1313da5bed96dbab764390009819119057445024d00b5864aad90038f270f7"),TEXT("80489fe01b7d1b903488bb3daaab8a62ff872ef34317fd4d504ad2e654c90aa0"),21456u,false};
   F.Layers[6]={EComponent::FarHandForeground,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_FarHandForeground_003_v001.T_Fairytale_Dodge_FarHandForeground_003_v001"),TEXT("cd2cc037d9c896fe7bc85757fe5092335f4a5692272afc11deab1ba82022be64"),TEXT("3202f9600ee5151e2d0162f58aa78007a3765f953983a41ddbc82fa1a357c851"),3518u,false};
   F.Layers[7]={EComponent::NearHand,TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/T_Fairytale_Dodge_NearHand_003_v001.T_Fairytale_Dodge_NearHand_003_v001"),TEXT("3e2b874fb5f2800197dfda20bdc281da760e8902ffe2351a79b8359c5bae56f1"),TEXT("21dcadc1ae51082310820c020831ae11e81428e819ff764c6edc5709d9c381a4"),3748u,false};
   F.SlotOrder={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::IndependentSword,EComponent::FarHandForeground,EComponent::NearHand};
  }
  return P;
 }();
 return Value;
}
}
