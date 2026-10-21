# 猎弩装填音效：本地来源与事件接口只读审计 v001

审计日期：2026-10-15。状态：**来源/哈希/许可和代码接口已核，装填音效尚未接线，未试听**。本轮仅写本文件；未改Source、工具或资产，未运行UE/UBT、解码/生成新音频、外部API或付费服务。没有音频试听工具调用，未将听感或整段运行混音认定通过。

## 事实

本地205个OGG当前文件逐一重新算SHA256，205/205与既有audio-preflight库存一致，0缺失/变更。组成是Impact Sounds130个单独音效、RPG Audio51个单独音效+1个合集Preview、Abstraction23个音乐；总203个唯一哈希，181个单独音效只有179个唯一哈希（两对carpet脚步完全重复）。Preview和音乐不作为弩机阶段短声候选。205/205完整解码是原预检的历史结果，本轮只复核实际文件哈希，没有重做解码或试听。

完整逐文件库存：[audio-preflight.json](F:/Ourgame/docs/production/first-batch-v1/audio-preflight.json)，SHA256 `d70898b60a39d7fb8b20a2441b42dfbf2feeb2968934bd08c718cf18bf9b5688`；原预检说明：[audio-preflight.md](F:/Ourgame/docs/production/first-batch-v1/audio-preflight.md)。原库存D12来源 [audio-and-assets.json](F:/Ourgame/docs/design/presentation-v1/audio-and-assets.json)，SHA256 `467f5895c96db5482f7b5c61ea1f6590d85bec2a8a6a7ae8f515c70a2fc82dbc`。

另有17个本地程序合成WAV，48kHz/mono/PCM16，全部当前SHA匹配生成manifest和UE导入receipt。它们不是上述第三方OGG的剪辑或混合；manifest记录标准库生成、0外部调用/0付费API/TTS、未试听、未最终验收。其来源声明是为本项目创建、无第三方采样许可依赖，并**未作CC0奉献或普遍版权资格承诺**。不能把第三方CC0许可证套到这17个原创候选上。

17源manifest：[manifest.json](F:/Ourgame/source-assets/production/audio-v001/manifest.json)，SHA `a2ebc87a2671f58ed12d1bb03616601dc5d8ae26f8d00ae6b2a7e200c1274e62`。实际UE导入receipt：[content-audio-v001-import.json](F:/Ourgame/UnrealGame/Saved/Bootstrap/content-audio-v001-import.json)，SHA `46e9fc39b90926e25583c54e53f37ce437265f9525065548c195823b35e9c64c`；时间2026-10-14T14:13:50.830997+00:00，success=true/actual_count17，receipt仍明确auditioned=false/final_mix_accepted=false。源manifest中engine_imported=false属于较早生成记录，不能据此否定后来的独立实际导入receipt，也不应倒改原来源。

目前已有XBW发射声，但17个候选中没有ReloadStarted、拉弦阶段、插箭阶段、ReloadCompleted、ReloadCancelled、PickupWeapon或PickupArmor专用声。装填图/Actor83通过和四甲录像不补足这个内容缺口。

## 205 OGG原包与许可依据

以下是实际本地许可文件的内容范围，未联网重新核官网。Kenney两份均明确CC0、可个人/商业使用、署名可选。Abstraction仅覆盖本包内音乐；其文末另有不赞同NFT/AI/未修改直接转售的作者表态，原文仍保留。本次不选用任何音乐，不将该包许可外推到作者其他站点或Patreon素材。

| 原包 | 本地许可文件及SHA256 | 原档案/来源记录 |
| --- | --- | --- |
| Kenney Impact Sounds (1.0) | [License.txt](F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/License.txt)<br>`b49aa9c56b04528b95913de13e506a0f7c5e807b9925db9bfef86af1f91120db` | [kenney_impact-sounds.zip](F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney_impact-sounds.zip)<br>`029d734af1582474edf3a694d1b0cebc97c1c152f2f39fa34d4c2bafc5de77f8`<br>[原记录官网页](https://kenney.nl/assets/impact-sounds) |
| Kenney RPG Audio | [License.txt](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/License.txt)<br>`5735dfd72cb64cbbceda4ebc00c380c41ca680edb82ff153aa7c9ab97614c539` | [kenney_rpg-audio.zip](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/kenney_rpg-audio.zip)<br>`6dbeaf8544da958d8f2adcb4a4a4b76c1ade34a05f8ab9edccd327da7375f38b`<br>[原记录官网页](https://kenney.nl/assets/rpg-audio) |
| Abstraction Music Loop Bundle | [_LICENSE.txt](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/abstraction-music-loop-bundle-2026-q3/extracted/_LICENSE.txt)<br>`d02e059adb401d50167b2e04d12ef9236fbcef0b4e3b7157bd5ebfab8a82b8f4` | [music-loop-bundle-2026-q3.zip](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/abstraction-music-loop-bundle-2026-q3/music-loop-bundle-2026-q3.zip)<br>`2ee1222f54446b61b9e51e211cea29ef6147491562c682edaf6056f38fe4c93b`<br>[原记录官网页](https://tallbeard.itch.io/music-loop-bundle) |

下载记录：[acquisition-manifest.json](F:/Ourgame/source-assets/third-party/kenney/2026-10-10/acquisition-manifest.json) SHA `60a07578fa624007876d01ce73315d35f2807e31bab9e935ad643f36db2c15aa`；[acquisition-manifest.json](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/acquisition-manifest.json) SHA `5e809f6c827a26b2d31f34165d3e2115d5baa37d8ac620528ff3b11d1bea5704`。记录中的旧E:/codex_game地址是当时下载根；本表链接为当前实读F:/Ourgame镜像。当前原ZIP及205 OGG哈希均已实核，未伪称本轮重新下载。

## 可供剪辑/试听的材料候选

“建议用途”仅依据文件身份、既有选材预检和数值长度作推理，不代表已听到相应机械音色。没有可信真实弩弦或插箭成品；creak/点击/木碰材料不能改称已解决。时长/采样峰值来自哈希一致的历史完整解码，峰值是decoded sample peak dBFS，既不是dBTP也不是LUFS。RPG候选均48kHz双声道，Impact候选均44.1kHz双声道。

| 用途假设 | 实际文件 | SHA256 | 长度s / 峰值dBFS | 限制 |
| --- | --- | --- | --- | --- |
| 起始握持/拉弦材料 | [creak3.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak3.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak3.ogg` | `f9638787f95004b9d2d06f8eff8e99d4e594c21b51947daf562856fbcec905d1` | 0.338208 / -7.413 | 0.338s适合短机械材料；仍需听后定点，不代表真实弩弦 |
| 较长拉弦材料备选 | [creak1.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak1.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak1.ogg` | `8a346186fd297254248cab8e8117060a52a5cf2a84f603153a762108550ea95e` | 0.661042 / -6.694 | 0.661s不能硬塞进.20→.60的.40s段，须剪辑后试听 |
| 较长拉弦材料备选 | [creak2.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak2.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/creak2.ogg` | `8a990afdc03aebb91d528f5385e2f95582dbfa8e2c12c71098ab01be9142294a` | 0.830146 / -7.040 | 0.830s需剪辑；不能拉长装填时轴来适配素材 |
| 起始握持/拾武器 | [handleSmallLeather.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleSmallLeather.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleSmallLeather.ogg` | `ae3cbf695aa0a8b98b5a80a835be5a3ccbd5446a24db2235cd4c3cd6fc92ed96` | 0.338208 / -11.620 | 皮革/握持材料；不是弩矢装入或完成事实 |
| 起始握持/拾武器备选 | [handleSmallLeather2.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleSmallLeather2.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/handleSmallLeather2.ogg` | `a66f6db5918ad016c28a9f2768f127a7f39b5fa04481e5a3b4e78ebe2a1c282d` | 0.307479 / -16.472 | 短握持材料；与完成声分开 |
| 插箭/轻机括材料 | [metalClick.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalClick.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalClick.ogg` | `9851a69d0c613e13bceef08060ecc4148f098ef487927cbebe270d642398a3b3` | 0.445833 / -6.929 | 0.446s偏长；起始样本非零，需剪短/渐入后试听 |
| 补弹提交卡扣材料 | [metalLatch.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalLatch.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/metalLatch.ogg` | `ba9ba60b172b3ebc131a940f25793cd2e207aca7af73dc80d637277f060f1708` | 0.261333 / +1.615 | +1.615dBFS解码过冲、14样本abs>=1；先浮点留余量再量化，非原始录音削波证据 |
| 插箭木托接触备选 | [impactWood_heavy_000.ogg](F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactWood_heavy_000.ogg)<br>`F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactWood_heavy_000.ogg` | `15ff82332f342c30e469215539e1cc57e11b221aa2cf7e11e811d313a9927f3d` | 0.313039 / -0.940 | 木碰材料可能过重；不可按文件名承诺箭轨声音 |
| 取消可选轻点备选 | [impactMetal_light_000.ogg](F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_light_000.ogg)<br>`F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactMetal_light_000.ogg` | `33b5e6e37c6e9d54e07bf5a89b12c76e879f40c1ea83cdd82714df1d6f9fec6d` | 0.351474 / -0.962 | 不是专用取消声，可能误像命中；默认取消静音更清楚 |
| 拾武器/换武器备选 | [drawKnife1.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/drawKnife1.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/drawKnife1.ogg` | `276403e72c3b71c47bc24db3083970c23f8e5551ffa78f436f83483c56f3f0bb` | 0.399708 / -24.284 | 刀具抽取素材不是弩具；-24.284dBFS采样峰较低，不可未试听就盲增益 |
| 换甲握带 | [beltHandle1.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/beltHandle1.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/beltHandle1.ogg` | `2ef665bd8b65dbe669f4560be38a6d8f04a162e618b15a49e3e71b58e558aab0` | 0.276708 / -3.289 | 只作衣带处理候选 |
| 换甲握带备选 | [beltHandle2.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/beltHandle2.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/beltHandle2.ogg` | `f3b692d5c83263c25bce779805b212dbab515d18a603c695fc6a1e8650cf5366` | 0.476562 / -4.172 | 只作衣带处理候选 |
| 换甲布料 | [cloth2.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth2.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth2.ogg` | `8a7451193c38bc05483aec25dd193e163a15d44cf7fff04ac7912573231b0201` | 0.415063 / -7.938 | 0.415s可作.50s事务的视觉反馈材料，仍未试听 |
| 换甲布料备选 | [cloth1.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth1.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/cloth1.ogg` | `ddb93a3671233f95da0e0b10367f082f7eb42fa6caaddcf776410aa8833c747d` | 0.661042 / -3.490 | 0.661s长于基础.50；不要为声音更改事务deadline |
| 换甲布带备选 | [clothBelt.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/clothBelt.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/clothBelt.ogg` | `f29560a2aea95bbfeb643e1e8f56ec2b6f7e32f32ce4e140645a36db81de3253` | 0.722521 / -4.305 | 0.723s，须剪辑/试听后才接 |
| 换甲布带备选 | [clothBelt2.ogg](F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/clothBelt2.ogg)<br>`F:/Ourgame/source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio/clothBelt2.ogg` | `d545b1d9f20e6188140aaf551a96f1e82fe0d15f7ca066fac8b065e1231e0038` | 0.753292 / -6.688 | 0.753s，须剪辑/试听后才接 |
| 重甲卡扣/硬片备选 | [impactPlate_heavy_000.ogg](F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactPlate_heavy_000.ogg)<br>`F:/Ourgame/source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio/impactPlate_heavy_000.ogg` | `112d4f93ddcc370b410630f971c0f5d991856102da9c76bc5c5540d388e75aaa` | 0.488662 / -0.972 | 起始样本约.2546，存在突入风险；应去掉硬切并试听，不能当完整穿甲成品 |

上述RPG文件适用RPG Audio许可；三个Impact文件适用Impact Sounds许可。未导入的候选不能因本地有OGG就假称UE SoundWave已就绪。`metalLatch`不能原增益直接混入；以-6dBFS样本峰为示例目标，至少需约7.615dB衰减（例如8dB浮点预衰减），这只是数值留余量，仍不是听感/混音验收。任何后续剪辑应输出新版本派生WAV、保原OGG、记录原hash/截取点/淡入淡出/增益/派生hash，不能覆盖原件。本轮未做这些处理。

## 已导入17候选与现Cue映射

下表源WAV和当前uasset均实读存在并重新哈希；uasset类型/时长是上述实际UE导入receipt当时的验证，不是本轮启动Editor重验。全部位于`/Game/Production/FirstBatch/v001/Audio`。

| 候选 | 实际WAV / SHA256 | 实际uasset / SHA256 | 当前静态映射 |
| --- | --- | --- | --- |
| AUD-SWD-WHOOSH-01 | [AUD-SWD-WHOOSH-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-SWD-WHOOSH-01__v001.wav)<br>`6b02b1e1c2e34684151202bef53f092ba9b2350ff578ba3dbb8096fbb17f8a09` | [SW_AUD_SWD_WHOOSH_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_SWD_WHOOSH_01_v001.uasset)<br>`50ff2abbe1a8ffe7b4bb70297c99ec9b65b77d778d16bcaffde8823035d5f4a0` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-GSW-WHOOSH-01 | [AUD-GSW-WHOOSH-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-GSW-WHOOSH-01__v001.wav)<br>`b89901ea83c8f2f28a5a4ba9dfa2c280ffa5e4da715f50f8155bf09dfd1b194a` | [SW_AUD_GSW_WHOOSH_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_GSW_WHOOSH_01_v001.uasset)<br>`af1346d5d00f25ba28c7eb3098bfa73ab0f07fa6f25f4dc9ebcf5a17fe38723e` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-SPR-THRUST-01 | [AUD-SPR-THRUST-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-SPR-THRUST-01__v001.wav)<br>`aaca86e4a4635670f80b5d7fbc439d9554848d83e4f8e6640dbdc3a6fe4bc110` | [SW_AUD_SPR_THRUST_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_SPR_THRUST_01_v001.uasset)<br>`2b8950d7d524097686eb1ee25bd71c62aa36523be466325403bd303f98d6a03e` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-SWD-WHOOSH-02 | [AUD-SWD-WHOOSH-02__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-SWD-WHOOSH-02__v001.wav)<br>`c9becad05f048714bd5d3a02aeec3ba2758976bbb232431478b0001ce09453f9` | [SW_AUD_SWD_WHOOSH_02_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_SWD_WHOOSH_02_v001.uasset)<br>`f085386c76cb026ff03c1f6157a4bf33a859d38d1404bbb4788e362d856c8ed8` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-GSW-WHOOSH-02 | [AUD-GSW-WHOOSH-02__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-GSW-WHOOSH-02__v001.wav)<br>`452afcaf972f94df9e4e9268ba07618325bb104891cac441c0067e8fa6cde98f` | [SW_AUD_GSW_WHOOSH_02_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_GSW_WHOOSH_02_v001.uasset)<br>`c10f91da63f6398b771a64c8a0ef521ef58fa1a38c4eb9893cac9912ac9fef52` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-SPR-THRUST-02 | [AUD-SPR-THRUST-02__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-SPR-THRUST-02__v001.wav)<br>`5b260c8b000366d7daf4c76d72d4d474dcd71d278dd9d60a09f66860976312ae` | [SW_AUD_SPR_THRUST_02_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_SPR_THRUST_02_v001.uasset)<br>`e248867867f80503823b2007da93635281423573fc03eb31a3eb1d407b5772f1` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-SWD-WHOOSH-03 | [AUD-SWD-WHOOSH-03__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-SWD-WHOOSH-03__v001.wav)<br>`4b61b6c26505d5a0db6396dce7b1792f428ccb4a89de8a847abb00d6a57a6304` | [SW_AUD_SWD_WHOOSH_03_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_SWD_WHOOSH_03_v001.uasset)<br>`cbd3428f4e431f8b762dbdf7e0de5af6645c3e4c6f1b4e385d04aad51e748d9f` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-GSW-WHOOSH-03 | [AUD-GSW-WHOOSH-03__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-GSW-WHOOSH-03__v001.wav)<br>`59d8b53e2ec61bc4ba05a599c3cd3519c3184ced4aa7e6af6c0b1f6ae534cf52` | [SW_AUD_GSW_WHOOSH_03_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_GSW_WHOOSH_03_v001.uasset)<br>`a6b365f20e1b07efc9b40cda3271486f6c4166467fba4eba988bc8a97e96bd4b` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-SPR-THRUST-03 | [AUD-SPR-THRUST-03__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-SPR-THRUST-03__v001.wav)<br>`6be2d5e77b0b4874b20a28f635e09449dab82473d42e822e1ddaf8417bfe7e41` | [SW_AUD_SPR_THRUST_03_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_SPR_THRUST_03_v001.uasset)<br>`b1576a5c2987ad6230327ec18e4e72517e833bb85208117de06a764c6d6cffd8` | Fighter真实近战ActiveWindow对应stage1..3；GameMode/World技能窗采用stage3 |
| AUD-XBW-RELEASE-01 | [AUD-XBW-RELEASE-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-XBW-RELEASE-01__v001.wav)<br>`58c4533ea780873e0b088e630e160504137fa0b24b94f31c1f5e94cad6ac1543` | [SW_AUD_XBW_RELEASE_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_XBW_RELEASE_01_v001.uasset)<br>`761117490bdf050f5fd5083397621706e2d97ca55d5ef71e90723e4c1c11e42c` | HUD消费实际World ProjectileEmitted非Magic→XBW_RELEASE_01 |
| AUD-FIRE-LAUNCH-01 | [AUD-FIRE-LAUNCH-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-FIRE-LAUNCH-01__v001.wav)<br>`3ea568f3a53d7c214db83890760802d63815bd226b7a1069b86a80d656c4c8fd` | [SW_AUD_FIRE_LAUNCH_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_FIRE_LAUNCH_01_v001.uasset)<br>`fa59c6d648258faa349d1639eb661e297ee03ff3b9a7f3aa39b9c969c8972d50` | HUD实际Magic ProjectileEmitted或Magic WindowCreated |
| AUD-FIRE-BURN-SHORT-01 | [AUD-FIRE-BURN-SHORT-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-FIRE-BURN-SHORT-01__v001.wav)<br>`54a9b50193a1e3e9fb837988a20ff5f2760678bc4937f403361aab874effec78` | [SW_AUD_FIRE_BURN_SHORT_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_FIRE_BURN_SHORT_01_v001.uasset)<br>`65787c13e01e458b1b0d3b2579cd45719606c26e51f46b486d88605837d69810` | HUD实际BurnTickCommitted且ActualHPLoss>0 |
| AUD-STONE-AWAKE-01 | [AUD-STONE-AWAKE-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-STONE-AWAKE-01__v001.wav)<br>`b91f927fc4efc585907c45be369113fc907eea2ae8e6197d3ba8a8fb525611f1` | [SW_AUD_STONE_AWAKE_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_STONE_AWAKE_01_v001.uasset)<br>`0c089495bda15534d2ce23aaae3937cfd2c284e229f98bda4d9b41da60f7ce25` | StoneKnight WakeStarted |
| AUD-STONE-WING-01 | [AUD-STONE-WING-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-STONE-WING-01__v001.wav)<br>`91f020a1b95a6f1d5aaef7e9ec2ddeee4b2dff676eaab9305693e3920332858d` | [SW_AUD_STONE_WING_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_STONE_WING_01_v001.uasset)<br>`8c26011cbc64fc71c80f1502c5c813ca7ad5f6862f09be36ba36a40fb08acd4a` | 已导入；本轮检索未找到当前preload/播放映射，不能称已接蝠翼 |
| AUD-STONE-ARMOR-SCRAPE-01 | [AUD-STONE-ARMOR-SCRAPE-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-STONE-ARMOR-SCRAPE-01__v001.wav)<br>`8af7b393a18e4753b2f7eeefafde9cb27c3a9b5558ee03a18426f45b1025846e` | [SW_AUD_STONE_ARMOR_SCRAPE_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_STONE_ARMOR_SCRAPE_01_v001.uasset)<br>`a1907e2fe7afdfa73d553500eca4821c4ff1b0be24dd6d6256618c090d6458d8` | StoneKnight ChargeStarted/ActiveWindow |
| AUD-STONE-CHARGE-BRAKE-01 | [AUD-STONE-CHARGE-BRAKE-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-STONE-CHARGE-BRAKE-01__v001.wav)<br>`667c5da9523e0c274bc1526767f22803bf7d6613d47ae69b0f4ae5a46be8c04a` | [SW_AUD_STONE_CHARGE_BRAKE_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_STONE_CHARGE_BRAKE_01_v001.uasset)<br>`7f1e12c9009fbd0dffd359c953dedd18cd23c3a3284d1952a2abc4036db7324a` | StoneKnight ChargeStopped |
| AUD-STONE-FRACTURE-01 | [AUD-STONE-FRACTURE-01__v001.wav](F:/Ourgame/source-assets/production/audio-v001/AUD-STONE-FRACTURE-01__v001.wav)<br>`9524cd2ce97251324e0df852bcaafe8167966201e80d3f3f059920575b64e107` | [SW_AUD_STONE_FRACTURE_01_v001.uasset](F:/Ourgame/UnrealGame/Content/Production/FirstBatch/v001/Audio/SW_AUD_STONE_FRACTURE_01_v001.uasset)<br>`0754957109967975bfbb6b211a966a681ff493bff07b29e35f181a417c99d48f` | StoneKnight PoiseBroken/Died |

额外旧第三方包有`/Game/ThirdParty/Kenney/RPGAudio/DrawKnife/SW_DrawKnife`和ImpactLight。前者只找到导入包、未找到当前播放调用；后者Fighter受伤和StoneKnight HUD反馈会用作实际impact。它们没有提供装填事件映射，也不应把命中声直接复用为补弹完成身份。

## 现运行接口与建议绑定

现WA已经具有实际`ReloadStarted`、`ReloadCompleted`、`ReloadCancelled`事件，含EventId/ActionId/InstanceId/AtTime/Action snapshot。`Issued`长期只保存实际ProjectileEmitted/ActiveWindow；`WeaponRuntimeHistory`保存Emission/ReloadCompleted资源receipt，不保存Started/Cancelled；PendingEvents会被Drain。Fighter AdvanceWeaponSkillTo把全部实际Events交中央消费，World当前只为ForwardStep/ProjectileEmitted/ActiveWindow处理，其他事件虽推进LastSkillEventId，却没有reload专用World journal或SFX映射。只观察当前Action或图frame不能恢复被错过的取消事实。

最小后续方案是在中央已接受事件流旁增加只读presentation journal，完整保存本Run/Room/Owner/EventId/ActionId/InstanceId/Kind/AtTime，播放器按cursor去重。不能由HUD反写kernel或库存。当前World/HUD `.25s`迟到跳过策略可作实时声音上限参考；新HUD/换房/重开应重置本地cursor，跳过历史积压，不回放整段装填。该方案本轮没有实现。

终止交接还需覆盖死亡：中央当前即便死亡仍会AdvanceWeaponSkillTo并Drain出事件，但随后`!bGameOver&&!PlayerFighter->bDead`守门会跳过ConsumeWeaponSkillEvents。因此只在现ConsumeBoundWeaponEvents分支加音频journal仍可能丢失死亡取消事实。未来应在真实事件Drain后的纯呈现交接保留终止事件，或由明确的死亡终止记录作废该Action声音；不能为此放开死亡后的发射/命中消费，更不能等旧End到了再推断“完成”。这是新增音频接线的接口边界，当前未实现取消SFX，不能把它倒称为现有声音的实际复现故障。

| 绑定点 | 真实依据 | 建议材料/行为 | 资源与取消规则 |
| --- | --- | --- | --- |
| ReloadStarted | WA实际EEvent、AtTime==A.Start，接纳成功才有 | 握持短声handleSmallLeather2；或先保持静音待真实拉弦剪辑 | 每真实Action一次；拒绝T/无资源/不合法请求无声；不补弹 |
| 视觉阶段0→1：拉弦 | 仍Active的该Reload时钟跨越Start+(End−Start)×.20/1.10 | creak3剪辑候选 | 同Action/阶段一次；不是新动作、不是资源提交；不能按GPU frame1每帧播放 |
| 视觉阶段1→2：置箭 | 仍Active的该Reload跨越×.60/1.10 | metalClick或木托接触派生短声，均须试听 | Ammo仍0；不因图上出现箭或声音响起提交资源 |
| 视觉阶段2→3：回握 | 仍Active的该Reload跨越×.85/1.10 | 可以静音或轻握持材料 | Ammo仍0；与完成卡扣声区分，不能让stage3抢播完成 |
| ReloadCompleted | 实际EEvent Terminal + 同Action/Instance ReloadCompleted receipt，AtTime==A.End、0→1 | 处理过过冲的metalLatch候选 | 只真正补弹提交响一次；不是预约到End就响 |
| ReloadCancelled | 实际EEvent/Terminal、LastReloadCancelTime；新T、换武器、受伤/死亡等真实取消 | 默认可静音；若以后加止机短点必须区别完成音 | 取消后作废该Action所有未来阶段/完成预约；旧deadline不得响完成，新Action另分ID；长拉弦如需截断应管理音频组件淡停 |
| PickupWeapon开始/提交 | GameMode真实StartEquipmentPickup(PickupWeapon)，以及最终CommitEquipmentAction成功安装inventory候选 | 现无专用Cue；handleSmallLeather或drawKnife只是试听备选 | 开始与提交必须区分；.35不能改；被取消/失败不得播“取得成功” |
| PickupArmor开始/提交 | 真PickupArmor事务Slot2/.50，且最终CommitEquipmentAction成功 | cloth2/beltHandle1或轻硬片材料，按实际甲材质选 | 旧甲在deadline前仍held；E打开选择层不是换装声，独立Enter接纳才有开始；失败/取消无完成声 |

阶段以真实最终`End−Start`归一化，适用未来合法ReloadSpeed而不是硬编码墙钟1.10。当前四甲零加速fixture基础1.10只用于证明；音效长度不得改Actor时轴。阶段采样只作呈现，可在大帧跨越后按迟到门跳过，而非一次爆响补放所有阶段。

装备Action view有ActionId/OperationId/Kind/SourceId/InstanceId/Slot/Start/Deadline，但没有现成音频journal。`V.Action.Active=false`也发生于取消/拒绝，单凭它或ArmorId变化不足以声明成功。建议在真实成功安装inventory候选后输出只读提交事件；若利用公开inventory Operations，必须关联原OperationId且Result.AcquiredId/Slot确证成功，不能从“现在没有action”推断。保持中央dueDamage先于同点新完成的现有权限；不增加资源退款或新的动作门。

## 建议最小下一步与验收边界

先将“装填开始/真实完成/取消阻断旧完成”做成三个实际事件门，再审是否需要拉弦与置箭两个纯呈现阶段声。先对creak3、handleSmallLeather2、metalClick、metalLatch和cloth2作少量保全试听/派生版本，保本地原许可。新资源放全新包目录，receipt记录原source、派生处理和SoundWave导入；不覆盖现17候选或旧运行证据。

真实验证至少包含一次完整1.10装填（开始一次/完成一次/唯一0→1），一次置箭图阶段后取消（无补弹、过旧deadline无完成声），同点伤害在完成前取消、正常重新T创建新Action、Q切走/死亡/换房不带旧预约，以及PickupArmor只开E层无开始声、freshEnter真接纳、被取消无成功声。HUD播放请求计数只是请求，不能当设备播放完成、可听品质或PCM正确性的替代；最终仍需真实主submix录制、F/E保全/哈希和试听。

## 本轮代码来源冻结

| 文件 | 本轮实读SHA256 |
| --- | --- |
| [DungeonWeaponActions.h](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWeaponActions.h) | `e8d6d2366c26b87eecc14b660b8020b31a4e7c674c7256479a536ba8d2b91586` |
| [DungeonFighter.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFighter.cpp) | `e36cc2915b1367057f32e25054eb6356c37e4569cddc3d619738afaa52df9a60` |
| [DungeonGameMode.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp) | `930d3ae95684e8f8893b507e394f65daf00beef4fa740c7d2fff1285651bd3e6` |
| [DungeonWorldProjectiles.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWorldProjectiles.cpp) | `0bc43aaf55c8576b93f8fde87cd8db92f04153d682ba332aa2620ac547687fb9` |
| [DungeonWeaponPresentation.inl](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonWeaponPresentation.inl) | `501e67665e1efabeb6ad209b98f7cec60e43626133bc52041b0c0156bd009b02` |
| [DungeonHUD.cpp](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonHUD.cpp) | `a81276255f8ed08351f9794598a02e8a983f6cf7cb5d3fa6cf65cc9ea9d44a94` |
| [DungeonXBWBodyPose.h](F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonXBWBodyPose.h) | `ab20ab9de111f97fb4d5b217c43d6923e4ece65249240682a5ea6ed1bb8c8b8e` |
| [ue-import-content-audio.py](F:/Ourgame/tools/scripts/ue-import-content-audio.py) | `431e33d221cf8d09c464f72c8016edcb78ca3b76685c53e7720cf532325a7dd5` |

结论限制：本文件完成本地来源和接口审计，不代表已剪辑、导入新装填声、完成接线、试听或正式音效/全内容/D13验收。
