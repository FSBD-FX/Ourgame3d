#pragma once
// Frozen source manifest SHA256 3a35ea2aacde0115947daf4b51ff023ca36d50b42e343b0b048c07c8e72d1905
// Frozen base manifest SHA256 cd35fa43412f8fcf6fcd074e9f4f8ff85c20615e2d99863f15c6f5504e0a7c7d
// Candidate measured metadata only; old states remain where not replaced.
namespace DungeonCandidateAssemblyV007 {
struct FMarker { const TCHAR* Clip; int32 Index; FVector2D Grip; FVector2D Root; float Angle; TArray<FVector2D> HandPolygon; bool WeaponVisible; };
inline const FMarker* Find(const FString& Clip,int32 Index) {
    static const FMarker Markers[] = {
    {TEXT("idle"),0,FVector2D(185,335),FVector2D(256,472),35.0f,{FVector2D(167,317),FVector2D(203,317),FVector2D(203,353),FVector2D(167,353)},true}, // cca03d3302bf5f5377e0bdc80b99704a2466348f717cd9a0c0fee314ee0eefcd
    {TEXT("idle"),1,FVector2D(184,334),FVector2D(256,472),35.0f,{FVector2D(166,316),FVector2D(202,316),FVector2D(202,352),FVector2D(166,352)},true}, // 5c64af4d729137017eda6778597c20f016c31e52ba99dd635b3226b15e7fc11f
    {TEXT("idle"),2,FVector2D(184,335),FVector2D(256,472),35.0f,{FVector2D(166,317),FVector2D(202,317),FVector2D(202,353),FVector2D(166,353)},true}, // dec80eb04a074e28cade8db7f4f526e7201feb40ce879319f4da031b910fe037
    {TEXT("idle"),3,FVector2D(184,336),FVector2D(256,472),35.0f,{FVector2D(166,318),FVector2D(202,318),FVector2D(202,354),FVector2D(166,354)},true}, // 613a0803ec2cdb0a4ca19016acc315eaf0eca9d3f4f0714fe6f576d603d9b71a
    {TEXT("idle"),4,FVector2D(185,336),FVector2D(256,472),35.0f,{FVector2D(167,318),FVector2D(203,318),FVector2D(203,354),FVector2D(167,354)},true}, // d8a7acb407d89dec13c36bc35dcf50b967916d0758b3c0d09f42718d082fdbbc
    {TEXT("idle"),5,FVector2D(186,336),FVector2D(256,472),35.0f,{FVector2D(168,318),FVector2D(204,318),FVector2D(204,354),FVector2D(168,354)},true}, // 52b259c3de25467787042f16309e064b1dcde68aaa177be0c572c6731ba586ea
    {TEXT("walk"),0,FVector2D(192,353),FVector2D(268,470),30.0f,{FVector2D(166,327),FVector2D(218,327),FVector2D(218,379),FVector2D(166,379)},true}, // a2eb8338bb6c03b2e7f5f55a7bce9a06635a74f5b3c5d9f6647cdfe2588d7123
    {TEXT("walk"),1,FVector2D(287,353),FVector2D(335,482),30.0f,{FVector2D(261,327),FVector2D(313,327),FVector2D(313,379),FVector2D(261,379)},true}, // 26bf4d1fd2fbca25ab3a9c19169b5148a94dd6c0a049938a77c709a8b1fa25d8
    {TEXT("walk"),2,FVector2D(211,352),FVector2D(292,470),30.0f,{FVector2D(185,326),FVector2D(237,326),FVector2D(237,378),FVector2D(185,378)},true}, // 486f1427bc2891da1162d385982ba76660dcdd54e2e85613ef536c450117bd93
    {TEXT("walk"),3,FVector2D(172,351),FVector2D(261,474),30.0f,{FVector2D(146,325),FVector2D(198,325),FVector2D(198,377),FVector2D(146,377)},true}, // 65a0e2bfd4741967f73cdbfa683f41bcbf3077c0614f1623399f88c20e781c0e
    {TEXT("walk"),4,FVector2D(98,367),FVector2D(229,489),30.0f,{FVector2D(72,341),FVector2D(124,341),FVector2D(124,393),FVector2D(72,393)},true}, // 2ddbba0939def55296e49ea2d8b1d0ae01bd8438b69f19cc9cc53a2860db530d
    {TEXT("walk"),5,FVector2D(181,349),FVector2D(265,470),30.0f,{FVector2D(155,323),FVector2D(207,323),FVector2D(207,375),FVector2D(155,375)},true}, // c6e76d2119468461b0ded71e8e520cf8ef7fcc1880607c577731f7560055c95d
    {TEXT("primary_1"),0,FVector2D(131,193),FVector2D(256,472),-125.0f,{FVector2D(105,167),FVector2D(157,167),FVector2D(157,219),FVector2D(105,219)},true}, // 33f746a0d27c81b89b1f0b7086e6f213890aadf6ba212defd9bdd4e93f572cab
    {TEXT("primary_1"),1,FVector2D(169,137),FVector2D(256,472),-55.0f,{FVector2D(143,111),FVector2D(195,111),FVector2D(195,163),FVector2D(143,163)},true}, // bdb63470527a2d7f3738f4a165e9aa0daf7f383891c6d65b20444c36708fc947
    {TEXT("primary_1"),2,FVector2D(284,295),FVector2D(256,472),20.0f,{FVector2D(258,269),FVector2D(310,269),FVector2D(310,321),FVector2D(258,321)},true}, // b47f3331d3a1efcfab791ea6c115483d1daee9d77506477cd25294349d327e93
    {TEXT("primary_1"),3,FVector2D(286,372),FVector2D(256,472),35.0f,{FVector2D(260,346),FVector2D(312,346),FVector2D(312,398),FVector2D(260,398)},true}, // f65a7d38112390a828e6adabe749102f4a98b7d0e9a07987b5c073409c81cefb
    {TEXT("primary_1"),4,FVector2D(200,364),FVector2D(256,472),25.0f,{FVector2D(174,338),FVector2D(226,338),FVector2D(226,390),FVector2D(174,390)},true}, // 849d979bb8576a1eaeb351677ba4b2a8397e020e3bf0bef7b515b07b441178fc
    {TEXT("primary_1"),5,FVector2D(202,359),FVector2D(256,472),-35.0f,{FVector2D(176,333),FVector2D(228,333),FVector2D(228,385),FVector2D(176,385)},true}, // 8b35ea89d2fd4feeaddeb889ed7dbba5bb6adbc85f6c9cceecc5af3ca567e35f
    {TEXT("primary_2"),0,FVector2D(227,368),FVector2D(256,472),30.0f,{FVector2D(201,342),FVector2D(253,342),FVector2D(253,394),FVector2D(201,394)},true}, // e1b3355fbe81918eec6c37f7deb96c93d1bba3ad90432bf2580a5395cbeea138
    {TEXT("primary_2"),1,FVector2D(134,343),FVector2D(256,472),50.0f,{FVector2D(108,317),FVector2D(160,317),FVector2D(160,369),FVector2D(108,369)},true}, // b8302a0f98dd16c62f5f9a9d576ef5dfb2ab53d3f56cfb6f01a43dbab357ea1d
    {TEXT("primary_2"),2,FVector2D(315,239),FVector2D(256,472),-35.0f,{FVector2D(289,213),FVector2D(341,213),FVector2D(341,265),FVector2D(289,265)},true}, // 50d28c6ee7240240f83d0d3aafa7b3457dd21a30ecf86f38bfed83f4584bbad7
    {TEXT("primary_2"),3,FVector2D(192,114),FVector2D(256,472),-35.0f,{FVector2D(166,88),FVector2D(218,88),FVector2D(218,140),FVector2D(166,140)},true}, // 23107803c09beddc5941cefaba9d761ada2c3b036ac27048b4e315b884f95caf
    {TEXT("primary_2"),4,FVector2D(163,168),FVector2D(256,472),-75.0f,{FVector2D(137,142),FVector2D(189,142),FVector2D(189,194),FVector2D(137,194)},true}, // 99c9fe073dc2f281b27c691b008db737a5ace7bfc03ac34a114a9800af8d78fa
    {TEXT("primary_2"),5,FVector2D(176,227),FVector2D(256,472),-80.0f,{FVector2D(150,201),FVector2D(202,201),FVector2D(202,253),FVector2D(150,253)},true}, // a54a82cc1b9028c7bfa50e03230632c39caddf086eb47b60eada5ab716440c31
    {TEXT("primary_3"),0,FVector2D(183,189),FVector2D(256,472),-70.0f,{FVector2D(157,163),FVector2D(209,163),FVector2D(209,215),FVector2D(157,215)},true}, // 4c42ea1b381ae5863899232ce359ee393420a4256e00b03620a47de7d0e42f20
    {TEXT("primary_3"),1,FVector2D(181,143),FVector2D(256,472),-55.0f,{FVector2D(155,117),FVector2D(207,117),FVector2D(207,169),FVector2D(155,169)},true}, // c08851f94bcda3093a556357fcec3a73eef9eea4505c8e2c439deca20d296b09
    {TEXT("primary_3"),2,FVector2D(253,398),FVector2D(256,472),25.0f,{FVector2D(227,372),FVector2D(279,372),FVector2D(279,424),FVector2D(227,424)},true}, // 34227aa7d7f95217ed7ca3f1fbbdf54883e359c56eeebe267a14b652ff6a26cb
    {TEXT("primary_3"),3,FVector2D(300,401),FVector2D(256,472),15.0f,{FVector2D(274,375),FVector2D(326,375),FVector2D(326,427),FVector2D(274,427)},true}, // 984907904acae53370c1f9268edab537c01b93180af2d9039ba7be456da796e9
    {TEXT("primary_3"),4,FVector2D(164,316),FVector2D(256,472),-20.0f,{FVector2D(138,290),FVector2D(190,290),FVector2D(190,342),FVector2D(138,342)},true}, // 8151d8eb8008db6edfdd3712728395b977d1c1e5d6b33622078ca3e1163428fe
    {TEXT("primary_3"),5,FVector2D(173,350),FVector2D(256,472),35.0f,{FVector2D(147,324),FVector2D(199,324),FVector2D(199,376),FVector2D(147,376)},true}, // a1d6bc39bd6c029d71fc954d570f8a36c3c7f5cb3298538712aed258745bcb94
    {TEXT("jump"),0,FVector2D(198,303),FVector2D(256,394),30.0f,{FVector2D(172,277),FVector2D(224,277),FVector2D(224,329),FVector2D(172,329)},true}, // 6fce3c884a32dac3e4aee21a11c427325a45f09535e718674db9268d28ba4d4c
    {TEXT("jump"),1,FVector2D(204,301),FVector2D(256,384),30.0f,{FVector2D(178,275),FVector2D(230,275),FVector2D(230,327),FVector2D(178,327)},true}, // 118c0a5a66245c9fc3d23dd8ab30b8de855322b2dd287ebd3e526f8483b7c9e7
    {TEXT("jump"),2,FVector2D(206,270),FVector2D(267,414),30.0f,{FVector2D(180,244),FVector2D(232,244),FVector2D(232,296),FVector2D(180,296)},true}, // 88233cda7bcced1b549d9d5580bea982f53d06776af4d4a05c5aa0d985f9c39a
    {TEXT("jump"),3,FVector2D(146,274),FVector2D(252,426),30.0f,{FVector2D(120,248),FVector2D(172,248),FVector2D(172,300),FVector2D(120,300)},true}, // e50263969c7071a7ac2b4d13a27193b22d245f7ff41e66a8ed15b2e1afd62519
    {TEXT("fall"),0,FVector2D(166,266),FVector2D(256,411),30.0f,{FVector2D(140,240),FVector2D(192,240),FVector2D(192,292),FVector2D(140,292)},true}, // f164dc1a93bfb389ac557c597812f20d78764f70e46e0b613dfd918fa0abcfc1
    {TEXT("fall"),1,FVector2D(192,279),FVector2D(260,412),30.0f,{FVector2D(166,253),FVector2D(218,253),FVector2D(218,305),FVector2D(166,305)},true}, // c713c6d9524545718fa4651ed672b24b078047caf80e4a26b67e0345f82a2eb6
    {TEXT("land"),0,FVector2D(173,276),FVector2D(256,391),30.0f,{FVector2D(147,250),FVector2D(199,250),FVector2D(199,302),FVector2D(147,302)},true}, // 34e8fe52a4e3d330d5223bfe6def7595b1f329f35f7abc7d87282bce100c7a38
    {TEXT("land"),1,FVector2D(193,299),FVector2D(256,413),30.0f,{FVector2D(167,273),FVector2D(219,273),FVector2D(219,325),FVector2D(167,325)},true}, // fc5928cf44b8ded3d23153de747a2d0b8044646bf5c288a3aa1c3a8b9636b1f1
    {TEXT("dodge"),0,FVector2D(184,363),FVector2D(256,472),20.0f,{FVector2D(158,337),FVector2D(210,337),FVector2D(210,389),FVector2D(158,389)},true}, // bb648572af9071de7c5eef0763632dedb81e00df0a3ab3fa3b71de2fdd78dee5
    {TEXT("dodge"),1,FVector2D(179,366),FVector2D(256,472),20.0f,{FVector2D(153,340),FVector2D(205,340),FVector2D(205,392),FVector2D(153,392)},true}, // 39ba1cdad34c86e078b1bc772dc4edb49ac33a203e91aef9496ecb55b96d94a9
    {TEXT("dodge"),2,FVector2D(179,380),FVector2D(256,472),10.0f,{FVector2D(153,354),FVector2D(205,354),FVector2D(205,406),FVector2D(153,406)},true}, // 8af9c3866e4432a7112b5e3e55c2b332edad9970ca4cba632fc7bbbb3243f389
    {TEXT("dodge"),3,FVector2D(146,336),FVector2D(256,472),0.0f,{FVector2D(120,310),FVector2D(172,310),FVector2D(172,362),FVector2D(120,362)},true}, // a95005c63884cee9405ac97c66d9bb23988993130c66a0c2df488576bd21468d
    {TEXT("dodge"),4,FVector2D(188,342),FVector2D(256,472),20.0f,{FVector2D(162,316),FVector2D(214,316),FVector2D(214,368),FVector2D(162,368)},true}, // 0e06e826664a21f30f6b4ec0eaef94400f31dbd7286bc625aa18c7934acd6f53
    {TEXT("dodge"),5,FVector2D(182,358),FVector2D(256,472),20.0f,{FVector2D(156,332),FVector2D(208,332),FVector2D(208,384),FVector2D(156,384)},true}, // fbf3e675bf9ba12608a0af6186665c65495b1f52715816c19043c4d29cb66359
    {TEXT("hurt"),0,FVector2D(176,345),FVector2D(256,472),35.0f,{FVector2D(150,319),FVector2D(202,319),FVector2D(202,371),FVector2D(150,371)},true}, // 12371221b0cba8f2961ced2272d2869d5179fd63d8cbe0c7b2b133ab5aae6561
    {TEXT("hurt"),1,FVector2D(183,345),FVector2D(256,472),35.0f,{FVector2D(157,319),FVector2D(209,319),FVector2D(209,371),FVector2D(157,371)},true}, // b3dd64253d43c2d236394a5c23c4d8e3ae102b97f1c32e0fb953985bdca13f57
    {TEXT("hurt"),2,FVector2D(171,357),FVector2D(256,472),35.0f,{FVector2D(145,331),FVector2D(197,331),FVector2D(197,383),FVector2D(145,383)},true}, // 5b7c6f52da21e557bf06eeb325ba93554a1150adce078eaa65353ddc5e2fda2b
    {TEXT("hurt"),3,FVector2D(184,340),FVector2D(256,472),35.0f,{FVector2D(158,314),FVector2D(210,314),FVector2D(210,366),FVector2D(158,366)},true}, // 927db39985c748c961b95217e73e3e161284ef046a92075161230afec3f2df33
    {TEXT("hurt"),4,FVector2D(180,343),FVector2D(256,472),35.0f,{FVector2D(154,317),FVector2D(206,317),FVector2D(206,369),FVector2D(154,369)},true}, // afa35b55254af3501896658f689df6ab6bda7e7f203bf816a744d55566c00b76
    {TEXT("hurt"),5,FVector2D(177,340),FVector2D(256,472),35.0f,{FVector2D(151,314),FVector2D(203,314),FVector2D(203,366),FVector2D(151,366)},true}, // 39076fcd1fd33cfd9342c4852ae92b45973164ae66e8565a07e3e44f65bbafbe
    {TEXT("death"),0,FVector2D(0,0),FVector2D(256,472),0.0f,{},false}, // 3e7178dae801d8a3570d48ebc0a2f21923d014e620d7ae0da9c43defb4249cdc
    {TEXT("death"),1,FVector2D(0,0),FVector2D(256,472),0.0f,{},false}, // 30521dac571031655c1b71f8df2942a5ba5b1a1c7f8d0b9c782f7f1bd9bad02a
    {TEXT("death"),2,FVector2D(0,0),FVector2D(256,472),0.0f,{},false}, // 14ec800e98518b2c390aea4be39afece5027785f5b2767a404fee30de1ab415b
    {TEXT("death"),3,FVector2D(0,0),FVector2D(256,472),0.0f,{},false}, // 6bf023260da750cb78dcbe57f1d9e59a1b10fa6fec022ee7afef5cb8a2faec30
    {TEXT("death"),4,FVector2D(0,0),FVector2D(256,472),0.0f,{},false}, // e101d5efbd428d60caf3f7e1ccbd06e1f8a5b33ee46b6cd6668957d4e649e229
    {TEXT("death"),5,FVector2D(0,0),FVector2D(256,472),0.0f,{},false}, // 7144cd2c50f174acf0ff14daa316691993851236e1c28997187893a6e1b1eafc
    {TEXT("secondary"),0,FVector2D(149,232),FVector2D(256,472),-130.0f,{FVector2D(123,206),FVector2D(175,206),FVector2D(175,258),FVector2D(123,258)},true}, // 62310a76a149543945027a1d0659a4adf711e44d79f7b96cf9f22fc5413c5798
    {TEXT("secondary"),1,FVector2D(141,187),FVector2D(256,472),-60.0f,{FVector2D(115,161),FVector2D(167,161),FVector2D(167,213),FVector2D(115,213)},true}, // a511888379a32c3aa06fbe66869ab06fcb9413935acd3f38068c92bd5c1928ae
    {TEXT("secondary"),2,FVector2D(270,353),FVector2D(256,472),25.0f,{FVector2D(244,327),FVector2D(296,327),FVector2D(296,379),FVector2D(244,379)},true}, // 9c074c85fc39420ec72f08aae2df109c5aa06ed70e58ad51a1870b22627be66a
    {TEXT("secondary"),3,FVector2D(333,386),FVector2D(256,472),25.0f,{FVector2D(307,360),FVector2D(359,360),FVector2D(359,412),FVector2D(307,412)},true}, // 53f6a33b21a3940da15762da571dbc279bd660f34ddcb3238f71297fc407d317
    {TEXT("secondary"),4,FVector2D(129,231),FVector2D(256,472),-110.0f,{FVector2D(103,205),FVector2D(155,205),FVector2D(155,257),FVector2D(103,257)},true}, // 47751099997f07ef8cf5b3eda7c5933724887ccd70685bb8be959626c4367aab
    {TEXT("secondary"),5,FVector2D(162,270),FVector2D(256,472),-70.0f,{FVector2D(136,244),FVector2D(188,244),FVector2D(188,296),FVector2D(136,296)},true}, // 6a2a77ffec757630a8859410e735818dde51bd96a82084ca7547663d060d63cc
    {TEXT("air_primary_1"),0,FVector2D(174,155),FVector2D(257,438),-125.0f,{FVector2D(148,129),FVector2D(200,129),FVector2D(200,181),FVector2D(148,181)},true}, // b1d0ecd945662cca4542d5fb87a11a4ceebeefc345ad9cd612bdf9e867619841
    {TEXT("air_primary_1"),1,FVector2D(205,108),FVector2D(255,443),-25.0f,{FVector2D(179,82),FVector2D(231,82),FVector2D(231,134),FVector2D(179,134)},true}, // 7ce1acbc50b53ce684110b578f3eb8f0ecde9cb8e62724c5eedc4ec7ae5ee7af
    {TEXT("air_primary_1"),2,FVector2D(329,251),FVector2D(267,439),20.0f,{FVector2D(303,225),FVector2D(355,225),FVector2D(355,277),FVector2D(303,277)},true}, // 9dbd9bf1777f5b2ac74dcff5b959338987d089fc6b6da439a3fdcdf62cef18ad
    {TEXT("air_primary_1"),3,FVector2D(332,336),FVector2D(248,437),25.0f,{FVector2D(306,310),FVector2D(358,310),FVector2D(358,362),FVector2D(306,362)},true}, // efee98019452c5ba2f961f5c1de3b1b4044974ba1e1895dd76f0c698b563a219
    {TEXT("air_primary_1"),4,FVector2D(246,337),FVector2D(265,441),25.0f,{FVector2D(220,311),FVector2D(272,311),FVector2D(272,363),FVector2D(220,363)},true}, // cef54fac27bc66be8af0d6c094456c8525715b697d37175665b07448888166d1
    {TEXT("air_primary_1"),5,FVector2D(237,323),FVector2D(252,436),-35.0f,{FVector2D(211,297),FVector2D(263,297),FVector2D(263,349),FVector2D(211,349)},true}, // a1e48e78d7e8c0d9ca2d5ff0198585b00f402ebc6a5f5fa6746f6305484ae393
    {TEXT("equip_weapon"),0,FVector2D(186,344),FVector2D(256,472),35.0f,{FVector2D(160,318),FVector2D(212,318),FVector2D(212,370),FVector2D(160,370)},true}, // bb69543cd6b9c6479e8ac68b5e2f4cc52fe3925a529b5de5332698893420b649
    {TEXT("equip_weapon"),1,FVector2D(181,344),FVector2D(256,472),35.0f,{FVector2D(155,318),FVector2D(207,318),FVector2D(207,370),FVector2D(155,370)},true}, // d6597a78a33c322adf1d42d632e5453ca3e3c5abc897b5db50e033290cb728d6
    {TEXT("equip_weapon"),2,FVector2D(182,344),FVector2D(256,472),35.0f,{FVector2D(156,318),FVector2D(208,318),FVector2D(208,370),FVector2D(156,370)},true}, // 185390e59ae2eb9473a33f3c6891fcd0f57c93722dc00d2b136d48eafdd7dc30
    {TEXT("equip_weapon"),3,FVector2D(186,343),FVector2D(256,472),35.0f,{FVector2D(160,317),FVector2D(212,317),FVector2D(212,369),FVector2D(160,369)},true}, // 97c9259829c55fcff5276c3084d910264f5b35aa935dde1ca22effddb485c1ec
    {TEXT("equip_weapon"),4,FVector2D(181,341),FVector2D(256,472),35.0f,{FVector2D(155,315),FVector2D(207,315),FVector2D(207,367),FVector2D(155,367)},true}, // 84754dcdf51d07ac393c2cd29f78a6f8302ba15ac80fcabb6031ddaa8be768a9
    {TEXT("equip_weapon"),5,FVector2D(184,344),FVector2D(256,472),35.0f,{FVector2D(158,318),FVector2D(210,318),FVector2D(210,370),FVector2D(158,370)},true}, // ff26d6e08ba4a7f18b6f5240f88f24587047eb064ea6ebbf49eaf180b6b85a00
    {TEXT("equip_armor"),0,FVector2D(186,344),FVector2D(256,472),35.0f,{FVector2D(160,318),FVector2D(212,318),FVector2D(212,370),FVector2D(160,370)},true}, // bb69543cd6b9c6479e8ac68b5e2f4cc52fe3925a529b5de5332698893420b649
    {TEXT("equip_armor"),1,FVector2D(181,344),FVector2D(256,472),35.0f,{FVector2D(155,318),FVector2D(207,318),FVector2D(207,370),FVector2D(155,370)},true}, // d6597a78a33c322adf1d42d632e5453ca3e3c5abc897b5db50e033290cb728d6
    {TEXT("equip_armor"),2,FVector2D(182,344),FVector2D(256,472),35.0f,{FVector2D(156,318),FVector2D(208,318),FVector2D(208,370),FVector2D(156,370)},true}, // 185390e59ae2eb9473a33f3c6891fcd0f57c93722dc00d2b136d48eafdd7dc30
    {TEXT("equip_armor"),3,FVector2D(186,343),FVector2D(256,472),35.0f,{FVector2D(160,317),FVector2D(212,317),FVector2D(212,369),FVector2D(160,369)},true}, // 97c9259829c55fcff5276c3084d910264f5b35aa935dde1ca22effddb485c1ec
    {TEXT("equip_armor"),4,FVector2D(181,341),FVector2D(256,472),35.0f,{FVector2D(155,315),FVector2D(207,315),FVector2D(207,367),FVector2D(155,367)},true}, // 84754dcdf51d07ac393c2cd29f78a6f8302ba15ac80fcabb6031ddaa8be768a9
    {TEXT("equip_armor"),5,FVector2D(184,344),FVector2D(256,472),35.0f,{FVector2D(158,318),FVector2D(210,318),FVector2D(210,370),FVector2D(158,370)},true}, // ff26d6e08ba4a7f18b6f5240f88f24587047eb064ea6ebbf49eaf180b6b85a00
    };
    for(const auto& M:Markers) if(Clip==M.Clip && Index==M.Index) return &M;
    return nullptr;
}
inline int32 Count(const FString& Clip) {int32 N=0;while(Find(Clip,N)) ++N;return N;}
inline constexpr float WeaponScale=.4f;
inline const FVector2D WeaponGrip(99,256);
}
