# Primary2软皮六相提取诊断 v001

- Chest standard-baseline: extract exit0; inspect exit0; frames6; inspect warnings=['leather_chest_sword_primary2: motion presence is too low (0.0009 < 0.0100)'].
- Chest shared-HD: extract exit0; inspect exit0; frames6; inspect warnings=['leather_chest_sword_primary2: motion presence is too low (0.0009 < 0.0100)'].
- NearShoulder standard-baseline: extract exit0; inspect exit0; frames6; inspect warnings=['leather_nearshoulder_sword_primary2: motion presence is too low (0.0006 < 0.0100)'].
- NearShoulder shared-HD: extract exit0; inspect exit0; frames6; inspect warnings=['leather_nearshoulder_sword_primary2: motion presence is too low (0.0007 < 0.0100)'].
- FarShoulder standard-baseline: extract exit1; inspect exit1; frames0; inspect warnings=['leather_farshoulder_sword_primary2: motion presence is too low (0.0002 < 0.0100)'].
- FarShoulder shared-HD: extract exit1; inspect exit1; frames0; inspect warnings=['leather_farshoulder_sword_primary2: motion presence is too low (0.0002 < 0.0100)'].

供Root测feature的Source见 `primary2-eighteen-source-index-v001.json` 与各 shared-HD run 的 curated/，显式selected0..5侧车和标准export已执行，逐帧RGBA等于pre-curation frames。A/B/delta仍null；实际Body171是run-primary2-v004，未自动贴合/镜像/动作补帧/导入。Far195原2171×724不改，失败与lowmotion保留。

min512/512/256为本组件配置；低于256未尝试。默认baseline失败及inspect低motion全部保留。bodyfreecount无语义mask无法由通道推断，诚实为null；已给每帧coreRGBA/hash/纯绿/edge及真实共同scale。执行者未查看新输出、未生成/导入/改旧run或tools/Source/UE/ledger/媒体。Root先E留后看。
