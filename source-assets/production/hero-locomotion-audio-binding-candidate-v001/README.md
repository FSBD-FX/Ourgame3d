# 玩家移动音频绑定候选 v001

状态：**实现候选，尚未集成、导入、UE 编译或试听**。只写本目录；实际 Source、Content、工具、E 盘媒体、运行中的 UE 与账本均未改动。六条 WAV 来自已冻结的本地 CC0 来源候选，未重新生成或加工。

已实现：可移植具名事件 producer/一次性消费 cursor；按真实地面距离交替脚步；成功起跳；真实 H>0→0 自然落地并按真实落速/本 epoch 下落距离选轻/重；实际 Dodge Started 去重；owner/run/room/restart/epoch 静默接入；暂停与终点死亡抑制；三份新 UE C++ 文件及三份现有文件的精确接点补丁；六条禁止覆盖的 SoundWave 导入提案。

主机验证：初始 RED 为 59 checks / 13 expected failures；GREEN 为 59 / 0。仅 MSVC C++17 主机逻辑测试，包含真实 DungeonDodge 内核。`tests/run-host.ps1 -Phase GREEN` 另编译纯头文件的无异常版本；`python verify-handoff.py` 校验当前源码 SHA、精确接点、Python 语法及六份冻结 WAV。UE 导入脚本只执行过 `--validate-only`。

| 具名 cue | 冻结 WAV（兄弟候选目录的 wav/） | 提案 SoundWave 名称 |
|---|---|---|
| HERO_STEP_LIGHT_01 | AUD-HERO-STEP-LIGHT-01__v001.wav | SW_AUD_HERO_STEP_LIGHT_01_v001 |
| HERO_STEP_LIGHT_02 | AUD-HERO-STEP-LIGHT-02__v001.wav | SW_AUD_HERO_STEP_LIGHT_02_v001 |
| HERO_TAKEOFF_LIGHT_01 | AUD-HERO-TAKEOFF-LIGHT-01__v001.wav | SW_AUD_HERO_TAKEOFF_LIGHT_01_v001 |
| HERO_LAND_LIGHT_01 | AUD-HERO-LAND-LIGHT-01__v001.wav | SW_AUD_HERO_LAND_LIGHT_01_v001 |
| HERO_LAND_FIRM_01 | AUD-HERO-LAND-FIRM-01__v001.wav | SW_AUD_HERO_LAND_FIRM_01_v001 |
| HERO_DODGE_SHORT_01 | AUD-HERO-DODGE-SHORT-01__v001.wav | SW_AUD_HERO_DODGE_SHORT_01_v001 |

全部新对象位于 `/Game/Production/HeroLocomotion/v001/Audio/`；详见 `import/import-manifest.json` 的精确绝对源路径、SHA、对象路径。源 PCM 合计 168960 字节；全部单声道 48k PCM16。导入提案使用 ADPCM、ForceInline、非循环、asset volume/pitch=1；step priority=40、其他=50。新 native prototype sink 统一声音组上限 6、StopQuietest、25ms stealing release；调用增益 step=.25、其他=.32，未调整既有声音。

仍待 Root：按 `handoff.md` 新运行空闲窗口顺序审查、集成、UE 编译及项目原有检查、六条独立导入、真实事件/播放请求/主混音关联、耳机与外放试听、材质与混音认可、性能检查、媒体保留与最终验收。现有 native 2D 原型播放架构保持一致；正式 middleware、3D/遮挡/混响均未在本候选实现或验收。受伤、死亡、Guard 接触归属、音频 audition 和最终完整单元维持 OPEN。

刻意边界：Schema1 与既有 continuation 不改。磁盘恢复/新房间/新 run/新 epoch 的脚步剩余距离与左右奇偶从零开始；不声称精确恢复保存前音频节拍。真实当前 H/V 可武装未来自然落地，保存前起跳和 Dodge 历史不会补播。
