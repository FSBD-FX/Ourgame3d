# 首个单人原型的第三方素材准备

核查日期：2026-10-10，Asia/Shanghai。**当前方向已改为 UE5 / Blender**；本轮获取过程开始于 Unity 方案，保留的 `Unity/` 文件夹是作者原包中的真实名称，不代表仍将 Unity 作为当前目标。范围：首个战斗房间的角色、敌人、武器、地牢、动作、UI、音效和音乐候选。此文记录来源与结构；UE5 实际导入、材质、动画蓝图和玩法验收由工程接入记录单列。

## 事实、推理、风险

**事实**：原有 UI Adventure 与 Impact Sounds 两包保持原位、未改写。本轮从作者官方网站公开链接取得 Kenney 地牢、Mini Dungeon、Animated Characters Protagonists、RPG Audio，以及 Quaternius Universal Animation Library 2 的免费 Standard。Quaternius RPG Character Pack 官方 Drive 文件夹可匿名列出，但 License.txt 与 Warrior.fbx 实际下载均返回 Google Drive “Quota exceeded” HTML；没有把错误页面当作素材，也没有绕过配额或登录。

**推理**：改用 Mini Dungeon 的人类 / 兽人 / 剑 / 宝箱 / 金币和自带动作即可准备第一个战斗房间。该包与地牢均来自 Kenney，许可清楚、下载体积小。Universal Animation Library 2 用于后续较标准人形骨架试验，不是首个 Mini Dungeon 角色运行的前置条件。

**风险**：Mini Dungeon 采用简化骨架，不能把免费 UAL2 的人形动作直接视作可重定向。下载页面的宣传数量不等于实际免费文件：本轮地牢有 39 个 FBX，UAL2 免费 Standard 有 43 个动画栈（包含 A_TPose；对应 42 个非 T Pose 动作，RM 与非 RM 是同一集合的两种导出）。下载与结构读取本身不证明引擎可用；后续 UE 实测已完成代表资产、材质与 idle 站立检查。武器挂点、完整战斗、命中窗口和最终风格仍不在此准备验收范围。

## 保存位置与索引

新增素材根目录：`E:\codex_game\source-assets\third-party\preparation-2026-10-10-v1`。不覆盖已有包，不修改原始 ZIP。

每个已获取包都保存以下内容：

- 原始 ZIP 与完整 `extracted/`。ZIP 中所有文件已安全解包；不是仅解出 License。
- `evidence/official-page.html`：匿名作者官方页面快照。反 CSRF nonce 已去除，未保存账号登录态或临时签名 URL。
- `archive-file-list.json`：**ZIP 内路径**与未压缩字节数。
- `file-checksums-sha256.json`：**相对 `extracted/` 的实际磁盘路径**、字节数与逐文件 SHA256。
- `structure-audit.json`：FBX / GLB 的网格、骨骼和动画元数据；音频的可读取格式信息。它不等于播放验收。

汇总索引：`acquisition-manifest.json`。其中 ZIP 路径、解包根目录、来源页、公开下载端点、档位、字节数和 SHA256 可追溯。itch CDN 的临时签名下载 URL 不作为永久来源；保存公开页面、upload ID 和生成下载 URL 的公开端点。代表文件清单：`representative-files.json`，逐项对照 ZIP 内路径与真实绝对路径。

安全解包拒绝绝对路径、父级跳转、Windows 盘符 / ADS、符号链接和重复目标路径，并限制单文件下载及解压总量。所有本轮包已完整解包成功；提取过程中读取文件并校验 ZIP CRC。没有修改 `Game/`、全局 MCP 配置或旧素材。

## 已获取包

| 包 / 实际版本依据 | 原始 ZIP 字节数 | 实际文件 | 许可依据 |
| --- | ---: | --- | --- |
| [Kenney Modular Dungeon Kit](https://kenney.nl/assets/modular-dungeon-kit)，包内 License 标示 2.1 | 6,886,434 | 209 文件；39 FBX、39 GLB、39 OBJ、39 MTL、48 PNG | 包内 `License.txt`，CC0 |
| [Kenney Mini Dungeon](https://kenney.nl/assets/mini-dungeon)，包内 License 标示 2.0 | 1,796,820 | 162 文件；30 FBX、30 GLB、30 OBJ、30 MTL、37 PNG | 包内 `License.txt`，CC0 |
| [Kenney Animated Characters Protagonists](https://kenney.nl/assets/animated-characters-protagonists)，包内 License 标示 1.1 | 581,441 | 16 文件；角色 FBX 1、动画 FBX 3、PNG 5、SVG 4 | 包内 `License.txt`，CC0 |
| [Kenney RPG Audio](https://kenney.nl/assets/rpg-audio) | 964,837 | 55 文件；52 OGG（51 个 `Audio/` 音效和 1 个 Preview） | 包内 `License.txt`，CC0 |
| [Quaternius Universal Animation Library 2](https://quaternius.itch.io/universal-animation-library-2)，免费 Standard，upload ID 17958478 | 18,735,003 | 13 文件；FBX 3、GLB 3、Blend 1、PNG 3、TXT 3 | 包内 `Universal Animation Library 2[Standard]/License.txt`，CC0 1.0 |
| [Abstraction / Tallbeard Music Loop Bundle](https://tallbeard.itch.io/music-loop-bundle)，仅 2026 Q3 分包，upload ID 19538393 | 64,577,448 | 26 文件；23 OGG、1 PNG、2 TXT | 包内 `_LICENSE.txt`，CC0 |

**最终新增 6 包 ZIP 共 93,541,983 字节（约 89.21 MiB）。** 原有两个 Kenney ZIP 合计 1,378,313 字节，保存在 `source-assets/third-party/kenney/2026-10-10/`，有原有独立清单；全部 8 包原 ZIP 合计 **94,920,296 字节（约 90.52 MiB）**。这是素材 ZIP 体量，不含解包副本、网页证据或传输协议开销。全部新增 ZIP 均已完整落盘、解包及核查，不再有 `.partial` 下载文件。本轮未付款、未调用付费生成 API、未登录账号，也没有取得任何付费 Source / Pro 档。

Modular Dungeon ZIP 的文件名仍为 `kenney_modular-dungeon-kit_1.0.zip`，**实际包内 License 标示 2.1**；以包内证据记录版本，不凭 ZIP 名把它认作 1.0。UAL2 官方页面有后续更新日志，但免费文件 upload 时间为 2026-06-16；本轮按 upload ID、文件哈希和实际内容固定，不未经证明标成完整 Source 2.2。

## 可直接读取的代表路径

下表“包目录”均相对新增素材根目录。**磁盘路径 = 新增素材根目录 / 包目录 / `extracted` / ZIP 内路径**。这些路径已逐项确认存在并可读；完整绝对路径和 SHA256 在 `representative-files.json`。

| 用途 | 包目录 | ZIP 内路径 = 解包目录内相对路径 |
| --- | --- | --- |
| 玩家 | `kenney-mini-dungeon` | `Models/FBX format/character-human.fbx` |
| 首个敌人 | `kenney-mini-dungeon` | `Models/FBX format/character-orc.fbx` |
| 武器 | `kenney-mini-dungeon` | `Models/FBX format/weapon-sword.fbx` |
| 掉落 / 宝箱 | `kenney-mini-dungeon` | `Models/FBX format/coin.fbx`、`chest.fbx` |
| 角色与道具颜色纹理 | `kenney-mini-dungeon` | `Models/FBX format/Textures/colormap.png` |
| 地牢小房间 / 地板 | `kenney-modular-dungeon-kit` | `Models/FBX format/room-small.fbx`、`template-floor.fbx` |
| 地牢纹理 | `kenney-modular-dungeon-kit` | `Models/FBX format/Textures/colormap.png` |
| 较完整骨架的备选角色 | `kenney-animated-characters-protagonists` | `Model/characterMedium.fbx`，皮肤示例 `Skins/skaterMaleA.png` |
| 该备选角色基础动作 | `kenney-animated-characters-protagonists` | `Animations/idle.fbx`、`run.fbx`、`jump.fbx` |
| 近战 / 受击动作库 | `quaternius-universal-animation-library-2-standard` | `Universal Animation Library 2[Standard]/Unity/UAL2_Standard.fbx`、`UAL2_Standard_RM.fbx` |
| Blender 原始源文件代表 | `quaternius-universal-animation-library-2-standard` | `Universal Animation Library 2[Standard]/Female Mannequin/Mannequin_F.blend` |
| 抽刀 / 拾取 / 脚步 | `kenney-rpg-audio` | `Audio/drawKnife1.ogg`、`handleCoins.ogg`、`footstep00.ogg` |
| 背景循环候选（未试听选定） | `abstraction-music-loop-bundle-2026-q3` | `Week 27 - Dusty Memories.ogg` |

原有 UI 代表文件实际路径：`E:\codex_game\source-assets\third-party\kenney\2026-10-10\kenney-ui-adventure\PNG\Default\button_brown_close.png`；原有 Impact Sounds 在同日期目录的 `kenney-impact-sounds/Audio/`。原有包未重新下载或改写。

## 骨架、动作与文件结构实查

### Mini Dungeon：首版推荐直接使用包内动作

两个角色 FBX 都实际含 `body-mesh`、`head-mesh`、2 个 Skin Deformer，以及 7 个 FBX Limb / Root 节点：`root`、`leg-left`、`leg-right`、`torso`、`arm-left`、`arm-right`、`head`。Blender 导入把 `root` 表示成 Armature 对象，其下为 6 根骨骼；这是表示层差异，不是丢了动作。没有标准人形的独立前臂、手掌、小腿等骨骼。UE5 初次应先核查同骨架的原包角色与动作导入，再考虑 IK Rig / 重定向；不能默认可直接映射 UE5 人形骨架。历史 Unity 接入参考是先用 Generic Rig，不默认 Humanoid Avatar 会通过。

每个角色 FBX 都实际包含以下 **32 个动画栈**：

`static`, `idle`, `walk`, `sprint`, `jump`, `fall`, `crouch`, `sit`, `drive`, `die`, `pick-up`, `emote-yes`, `emote-no`, `holding-right`, `holding-left`, `holding-both`, `holding-right-shoot`, `holding-left-shoot`, `holding-both-shoot`, `attack-melee-right`, `attack-melee-left`, `attack-kick-right`, `attack-kick-left`, `interact-right`, `interact-left`, `wheelchair-sit`, `wheelchair-look-left`, `wheelchair-look-right`, `wheelchair-move-forward`, `wheelchair-move-back`, `wheelchair-move-left`, `wheelchair-move-right`。

`chest.fbx` 和 `gate.fbx` 各有 `open`、`close`、`open-close` 3 个动画栈；`trap.fbx` 有 `show`、`hide`、`show-hide`。静态剑与金币也已实际解包。FBX 版本为 7700，纹理路径引用 `Textures/colormap.png`。

### UAL2 Standard：免费档内容与边界

Unity 文件有 RM（根运动）与非 RM 两种导出；包内 README 说明这一差异。两者均有 65 个 FBX Limb / Root 节点、`Mannequin` 网格、43 个动画栈。GLB 结构解析也读到对应的 43 个动画。**不按全产品宣传的 130+ 动作记录免费获取数量，也不把两个导出重复相加。**

实际动作名去掉 `Armature|` 前缀后为：

`A_TPose`, `Chest_Open`, `ClimbUp_1m`, `Consume`, `Farm_Harvest`, `Farm_PlantSeed`, `Farm_Watering`, `Hit_Knockback`, `Idle_FoldArms_Loop`, `Idle_Lantern_Loop`, `Idle_No_Loop`, `Idle_Rail_Call`, `Idle_Rail_Loop`, `Idle_Shield_Break`, `Idle_Shield_Loop`, `Idle_TalkingPhone_Loop`, `LayToIdle`, `Melee_Hook`, `Melee_Hook_Rec`, `NinjaJump_Idle_Loop`, `NinjaJump_Land`, `NinjaJump_Start`, `OverhandThrow`, `Shield_Dash`, `Shield_OneShot`, `Slide_Exit`, `Slide_Loop`, `Slide_Start`, `Sword_Block`, `Sword_Dash`, `Sword_Heavy_Combo`, `Sword_Regular_A`, `Sword_Regular_A_Rec`, `Sword_Regular_B`, `Sword_Regular_B_Rec`, `Sword_Regular_C`, `Sword_Regular_Combo`, `TreeChopping_Loop`, `Walk_Carry_Loop`, `Yes`, `Zombie_Idle_Loop`, `Zombie_Scratch`, `Zombie_Walk_Fwd_Loop`。

免费包额外含女木偶 `Mannequin_F.blend`、FBX 和 GLB；README 明确女木偶不包含动画。此 `.blend` 实查有 Rigify 风格的控制骨架 / metarig（382 / 54 骨骼），不是付费 Source 的整套动画源文件。加载时禁用自动脚本，`rig_ui.py` 未执行。女木偶 FBX 为 65 骨骼、0 个动画栈。作者分别提供 `Unity/` FBX 和 `Unreal-Godot/` GLB；当前应由 UE5 实测选择导入通路、比例、骨架映射与重定向，不因目录名称就认定兼容性。

### 其他结构读取

Animated Characters Protagonists 含一个 `characterMedium.fbx` 和四张皮肤 PNG（另四份 SVG 源），独立 `idle/run/jump` FBX 各含目标姿势和一个对应动作。模型与动作 FBX 读取到 58 个 Limb / Root 节点，含 IK / 控制和末端节点；不能把 58 都当作人体变形骨骼。此包留作较完整骨架的备选，不作为奇幻角色美术已选定。

RPG Audio 的 52 个 OGG 均可解析为 Vorbis、48 kHz、双声道，并通过 Ogg 页边界检查。`Audio/` 51 个文件包含抽刀、切割、脚步、金币、门和布料；Preview 另计。文件格式核查不等于已试听挑选、混音或验证响度与循环。

音乐 Q3 分包实际包含 23 个 OGG，均可解析为 Vorbis、44.1 kHz、双声道，时长约 18.31–61.33 秒，全部 Ogg 页边界有效。包内 `_LICENSE.txt` 与官方页均明确 CC0；`_README.txt` 推荐 OGG 循环，并把署名和赞助表述为可选。这里仅获得循环候选，没有试听、检查曲风或实测首尾衔接。Epic 的 [UE5.5 音频导入文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/importing-audio-files?application_version=5.5)明确列 OGG 为受支持来源，代表导入脚本直接提交 OGG；真实引擎随后观察到三份代表音频的 SoundWave。成功导入不等于试听通过。未生成重复 WAV 副本。

## 本机 Blender 读取证明

通过本机 Blender **5.2.2 LTS** 后台进程实际读取：Mini Dungeon 人类、兽人、剑，Modular Dungeon `room-small.fbx`，以及 UAL2 女木偶 `.blend`。均成功；人类 / 兽人各读到 32 个 Blender Action。过程禁用自动脚本，无保存、无渲染、无展示媒体。

结构记录：新增素材根目录的 `blender-structure-inspection.json`。核查脚本：`inspect_blender.py`。读 FBX / GLB / OGG 元数据与校验值的脚本为 `audit.py`，获取和安全解包脚本为 `acquire.py`。

这只证明选定文件能被该 Blender 版本读取，不证明所有包内文件均被编辑器导入，也不替代 UE5 骨架、材质、动画与 Play 验证。素材读取阶段没有建立或修改引擎场景；后续 UE 验收场景由工程代理负责，结果见下文。这里没有作出美术接受或可玩版本完成声明；历史 Unity 导入结果由此前工程接入记录保留。

## 缺口与延后项

| 项目 | 真实状态 | 合理下一步 |
| --- | --- | --- |
| Quaternius RPG Character Pack | 官方 Drive 下载配额超限；无模型或包内许可文件取得 | 首版用已保存 Mini Dungeon；未来官方配额恢复后再补，不用不明镜像 |
| Fantasy Props MegaKit 免费 Standard | 官方页列 143 MB，本轮未下载 | 首版已有剑 / 宝箱 / 金币；需要更多家具与武器时再取免费档 |
| 付费 Source / Pro、账号服务、生成 API | 未使用 / 未取得 | 有明确需求与费用后按项目约定处理 |
| 最终角色美术、动作重定向、武器挂点、碰撞 | 代表角色材质和 idle 已在 UE5 实测；这些玩法与美术决定尚未完成 | 首个战斗房间中继续核查；不默认可重定向 |
| 音效选择、音乐曲风和无缝循环 | 来源与格式已核查；试听、循环和运行验收未做 | 首个房间运行时试听与校准，再决定入选文件 |

不可获取与延后候选另存 `unavailable-and-deferred-candidates.json`，包含官方来源、失败依据与替代方案。错误页面保存在 `not-acquired-quaternius-rpg-characters/evidence/`，不计入资产获取总量。Agent Reach 的 Jina 通用读取请求本轮超时，转用官方页面和公开作者下载端点核对；更新检查受 GitHub API 限流未得到结果，不据此推断有无新版。

没有向用户展示项目草图、图片、动画或音频；如后续展示，仍需先按项目约定归档到 `E:\OurGame\Knight\过程图稿与视频`。

## UE5.5 代表资产导入脚本

脚本：`E:\codex_game\tools\scripts\ue-import-prepared-assets.py`。普通 Python `--preflight` 已确认：**14 个代表源文件均存在、可读，且 SHA256 均匹配保存的来源清单 / Blender probe 记录**。普通预检明确输出 `engine_executed=false`。工程代理随后在真实 UE5.5.4 Editor 执行脚本；首轮真实结果和修复过程见下节，不能将普通预检当作导入证明。

引擎内执行需要 Python Editor Script Plugin：

```text
py "E:/codex_game/tools/scripts/ue-import-prepared-assets.py"
```

也可在启动 UE 编辑器时传入：

```text
-ExecutePythonScript="E:/codex_game/tools/scripts/ue-import-prepared-assets.py"
```

14 个来源任务包括：房间、地板、剑、金币、宝箱、人类、兽人、两个 colormap、一个 UI PNG、Impact / RPG 音效各一个、一个背景循环、Blender 1×1×2 m probe。目标均在 `/Game/ThirdParty/...` 的各自专用目录，源文件保持不变。

静态 FBX 使用 StaticMesh 配置并组合网格；人类 / 兽人分别创建骨架，启用原文件动画导入。暂不做重定向、角色蓝图或材料接线，也不自动生成房间凸包碰撞来冒充可走的地牢。宝箱此处按静态任务导入，开关盖动作仍需另行接入。单位配置让 FBX 导入器转换为 UE 厘米；probe 的报告同时记录**实际 XYZ 尺寸、最长轴、100×100×200 cm 原顺序匹配与容许换轴匹配**，不凭配置就宣称单位 / 朝向正确。

每个任务读取 `get_objects()`、`imported_object_paths`，再检查该专用目录中的真实对象，记录实际 `StaticMesh` / `SkeletalMesh` / `Skeleton` / `AnimSequence` / `Texture2D` / `SoundWave` 等类型、保存 API 返回值和失败原因。角色报告分别列出**实际观察到的 AnimSequence 数量与名称**；原 FBX 的 32 动画栈只作为来源元数据另列，不当作 UE 导入数量。脚本现增加每角色六个 idle / 左右近战姿态的根骨与头部数据门槛；该数值核查不代替 PIE 画面、音频试听、材质与玩法验收。

引擎运行后写入**当前项目**的 `Saved/Bootstrap/asset-import-report.json`，每项完成即更新，并保留带 UTC 时间的运行副本；运行前的旧报告也另存。默认遇到已有专用目录时只检查已有对象，避免重跑覆盖；需要重导时，在启动编辑器的环境中设置 `CODEX_ASSET_IMPORT_REPLACE=1`，报告会标明替换模式。可用 `CODEX_ASSET_IMPORT_ONLY=human,orc` 限定最小修复范围；限定运行的报告只覆盖所选任务，不代表重新执行完整 14 项。脚本不执行网络请求或付费生成。

所用参数已查阅 Epic **application_version=5.5** 的官方资料：[AssetImportTask](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetImportTask?application_version=5.5)、[FbxImportUI](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxImportUI?application_version=5.5)、[静态网格导入数据](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxStaticMeshImportData?application_version=5.5)、[骨骼网格导入数据](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxSkeletalMeshImportData?application_version=5.5)、[动画导入数据](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxAnimSequenceImportData?application_version=5.5)、[导入类型枚举](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FBXImportType?application_version=5.5)、[StaticMesh bounds](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/StaticMesh?application_version=5.5)、[EditorAssetLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorAssetLibrary?application_version=5.5)。源码可解析与官方参数核查不替代本机 UE 执行。

## UE5.5.4 真实导入核查

首轮由工程代理在单一 UE **5.5.4-40574608+++UE5+Release-5.5** GUI Editor 执行，报告：`E:\codex_game\UnrealGame\Saved\Bootstrap\asset-import-report-20261010T015423_395596Z.json`；原生日志：`E:\codex_game\UnrealGame\Saved\Bootstrap\editor-verification-20261010-095359.log`。14 个来源任务实际观察到 **76 个对象**：6 StaticMesh、2 SkeletalMesh、2 Skeleton、60 AnimSequence、3 Texture2D、3 SoundWave。所有保存 API 返回 true，并逐路径确认对应 76 个 `.uasset` 非空存在。

Blender probe 的真实 UE StaticMesh 局部包围尺寸 **X=100、Y=100、Z=200 cm**，包围盒原点为 `(0,0,100) cm`，最长轴 Z，原 XYZ 顺序匹配通过。该结果是这一个诊断 FBX 的测量，不推广为所有作者模型的比例都合适。原始人类 / 兽人的 UE 包围高度分别约 75.53 / 78.03 cm；游戏角色最终缩放仍需玩法场景决定。

首轮人类 / 兽人各只有 **30 个 AnimSequence**。原生日志实际有 **4 条 FBXImport Error**：各角色左右 `attack-melee` 片段约 0.416667 秒，默认强制 30 fps 后末端在半帧边界，被 UE 拒绝；原始 FBX 二进制 `LocalTime` / `LocalStop` 也确认这两段约 0.416667 秒。因此首轮报告的 `failed_task_ids=[]` 只证明期待的对象类被观察到，不证明全部源动作导入，也不证明原生日志无错误。

据此修正脚本为 `use_default_sample_rate=False`、`custom_sample_rate=60`、`snap_to_closest_frame_boundary=False`，来源范围对应 25 个 60 fps 间隔。**实际 UE AnimSequence 的左右近战时长都是 0.400000006 秒，约 0.4 秒，不能宣称完整保留了来源的 0.416667 秒。** 后续命中窗口须按实际 UE 片段制定。新增从已保存源结构审计读取动作名并逐项对照实际 AnimSequence；缺少任何源 take 将明确标记任务失败。最小修复只选择人类 / 兽人，其他资产不重导。后续真实修复结果如下。

首轮原生日志另有 **14 条 FBXImport Warning**：选定 FBX 缺少平滑组，以及房间、金币、宝箱的退化切线 / 近零副法线。首轮静态与骨骼对象保存后，最终代表材质已在运行画面检查；未重写作者原始 FBX 的平滑组 / 切线数据，不把这些源文件警告视作已修复。宝箱此任务按静态网格导入，因此原有开合动画仍未接入。材质、碰撞、动画播放、音频试听、最终玩法和风格验收继续由工程与运行记录分别核查。

## 正式动作集与轴修复结论

第二轮设置 60 fps 后，已有 SkeletalMesh 进入网格重导分支，仍未补入近战片段。第三轮显式使用旧 FBX 导入器、`FBXIT_ANIMATION`、`import_mesh=False`，绑定各角色已有 Skeleton，并使用 `SK_Human_Anim` / `SK_Orc_Anim` 前缀，才实际得到各 32 个 AnimSequence。对应 `asset-import-report-20261010T020355_102224Z.json`。源动作名与本节上方的 32 名逐项相符；这 32 名包含 `static`，两角色是同一动作集合，不宣称 64 种独特动作。

但 32 个文件存在仍不足以证明角色可用：PIE 中角色仰躺。独立全新网格 + 新骨架 + 32 动作的一次 legacy FBX 对照也复现，因此不能只归因于此前 Interchange 与 legacy 混用。来源 Blender 实查外层 Empty 有 +90° X 旋转，root Armature 局部为单位旋转，保留父级后的来源站立正确。UE 中参考根骨四元数 XYZW 为约 `(-0.70710672,0,0,0.70710684)`，未修复动画根骨却为单位旋转；动画头部主要沿负 Y，而非向上。证据在 `blender-source-axis-inspection.json` 与 `character-axis-diagnostic-report-20261010T021017_081764Z.json`。

独立脚本 `E:\codex_game\tools\scripts\ue-diagnose-character-axis.py` 先在隔离目录导入，再通过严格门槛后修复正式动画。首次 `roll=-90` 试验实际得到相反根骨旋转，与参考差约 180°，因此门槛拒绝且正式资产未修改。**真实通过的 Unreal 动画导入选项是 `import_rotation=Rotator(pitch=0,yaw=0,roll=90)`。** 这是这两份 Mini Dungeon FBX 的动画数据修正；mesh 导入旋转保持零，Actor / Component 不加 pitch 或 roll 补偿，不推广为所有 FBX 的通用参数。

最终修复记录：

- `E:\codex_game\UnrealGame\Saved\Bootstrap\character-axis-repair-report-20261010T021821_783052Z.json`：`isolated_alignment_passed=true`、`canonical_alignment_passed=true`、`canonical_assets_modified=true`，状态 `canonical_root_alignment_passed_pose_samples`。
- 每角色 32 个实际 AnimSequence，全部保存成功且绑定该角色原 Skeleton；32 份既有 `FbxAnimSequenceImportData` 也同步为 60 fps / +90 roll，防止后续合法 Reimport 回退。
- 每角色采样 `idle`、`attack-melee-right`、`attack-melee-left` 各自 0 秒 / 中点，共六姿态；有效 AnimPose，根骨与参考夹角须 ≤0.1°，head 的 component Z 须 >10 cm。实际两角色十二姿态根骨夹角均为 0°，head Z 约 34.325–34.532 cm。
- 正式修复前备份：`E:\codex_game\UnrealGame\Saved\Bootstrap\asset-backups\20261010-before-animation-axis-normalization`，68 个 `.uasset` 与 SHA 清单。该备份是修轴前的 32 动作版本；没有宣称另存了初轮 30 动作的完整二进制快照。

唯一正式角色路径：

| 对象 | 人类 | 兽人 |
| --- | --- | --- |
| SkeletalMesh | `/Game/ThirdParty/Kenney/MiniDungeon/Human/SK_Human` | `/Game/ThirdParty/Kenney/MiniDungeon/Orc/SK_Orc` |
| Skeleton | `/Game/ThirdParty/Kenney/MiniDungeon/Human/SK_Human_Skeleton` | `/Game/ThirdParty/Kenney/MiniDungeon/Orc/SK_Orc_Skeleton` |
| 32 动作的名称模式 | 同目录 `SK_Human_Anim_<源 take 名>` | 同目录 `SK_Orc_Anim_<源 take 名>` |
| 右手近战代表 | `SK_Human_Anim_attack-melee-right` | `SK_Orc_Anim_attack-melee-right` |

最终代表集合为 **80 个正式对象**：6 StaticMesh、2 SkeletalMesh、2 Skeleton、64 AnimSequence、3 Texture2D、3 SoundWave。14 项对象索引在 `asset-import-report-20261010T021821_408549Z.json`，它写于轴修复之前，必须结合最终轴报告判定。`/Game/Tests/Preparation/AxisDiagnostic/` 下的 Fresh、Aligned、AlignedV2 是保留的成功 / 失败实验，不计入正式对象或可用动作数量。

最终真实 PIE 报告：`E:\codex_game\UnrealGame\Saved\Bootstrap\pie-report-20261010T021821Z.json`。运行 8.016 秒，真实开始 / 停止、idle 进度变化及六帧采样均有时间记录；角色 Actor 与 Component 的 pitch / roll 为零，yaw=180°。工程代理和主代理分别审阅归档首 / 中 / 尾，确认两角色站立、代表颜色材质和道具可见。原生日志 `editor-verification-20261010-101801.log` 本轮未见 Error 或 FBXImport Warning；本轮以检查既有静态对象及重导动画为主，不意味着重新修好了原始静态 FBX 警告。

媒体归档索引：`E:\OurGame\Knight\过程图稿与视频\2026-10-10_UE55角色轴修复与运行采样_v004\index.json`。视频是六个实际 PIE 画面按约 1 fps 取样后保持帧编码成 6 秒 MP4，**不是连续实时录屏**。本报告不展示媒体；证据仅覆盖素材 / 材质 / idle 准备，不代表战斗或玩家输入已实现。组件 bounds 可能回退为参考包围盒，未把它当作逐顶点 posed bounds。

## 清空工程后的复现入口

必须把主导入器与 `ue-diagnose-character-axis.py` 放在同一 `tools/scripts/` 目录，并保留完整来源目录与 source audit。最终主导入器已将两角色动画默认改为 **60 fps、+90 roll**，mesh 旋转显式为零；重导已有角色时走动画专用任务并同步既有动画 import data。它现在也检查实际每角色恰为 32 个动画、同 Skeleton 与六姿态门槛，数量正确而轴错误将标记失败。

**验证边界**：上述 +90 的 animation-only 隔离导入、正式覆盖、十二姿态与 PIE 已真实通过。最后更新的主导入器 schema 3 只做了 AST 语法检查和 14 来源 / SHA 预检；没有为再次运行它而关闭已释放的 Editor。尤其“干净目录内 mesh + animation 同一次导入并带 +90”尚未单独重测，不能直接宣称成功；应按下列门槛验收，失败时使用已验证的 animation-only 规范化流程。

1. 单一 UE5.5 Editor、启用 Python Editor Script Plugin，在全新项目内执行主脚本。已有 Editor 可在 Python 控制台执行以下命令；启动方式可用 `-ExecutePythonScript`。默认已有目录只检查，不覆盖。

   ```text
   py "E:/codex_game/tools/scripts/ue-import-prepared-assets.py"
   ```

2. 检查当前项目 `Saved/Bootstrap/asset-import-report.json`：每角色 32 名、同 Skeleton、保存成功、`selected_pose_alignment_gate.passed=true`。不能仅用 `source_tasks=14` 或对象总数作为通过条件。若缺片段或轴门槛失败，保留报告。缺近战时，先在启动 Editor 的环境中设置 `CODEX_ASSET_IMPORT_REPLACE=1`、`CODEX_ASSET_IMPORT_ONLY=human,orc`，运行主脚本；已有 mesh 会触发 animation-only 补齐。待两角色均已有 32 动作与四个近战文件，再备份各正式角色目录到一个**全新绝对路径**（如 `Saved/Bootstrap/asset-backups/<时间>/Human` 与 `Orc`），连同 SHA 清单保存；不要覆盖旧备份。补齐步骤只覆盖角色动画，不改骨架网格 / 关卡。

3. 需要独立的严格修轴记录时，关闭该 Editor 后，在启动新唯一 Editor 的 PowerShell 中设置以下环境并执行诊断脚本。此流程先检查隔离 32 动作，再要求存在包含两角色 mesh 和四个近战片段的备份，才允许正式动画覆盖。这里的 `BACKUP` 必须替换为本次实际创建的绝对备份目录，不能用尚不存在的示例。

   ```powershell
   $env:CODEX_CHARACTER_AXIS_REPAIR = '1'
   $env:CODEX_CHARACTER_AXIS_APPLY_CANONICAL = '1'
   $env:CODEX_CHARACTER_AXIS_BACKUP = 'E:\codex_game\UnrealGame\Saved\Bootstrap\asset-backups\20261010-before-animation-axis-normalization'
   & 'G:\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe' 'E:\codex_game\UnrealGame\CodexDungeon.uproject' '-ExecutePythonScript=E:\codex_game\tools\scripts\ue-diagnose-character-axis.py'
   ```

   上面路径是本轮已存在的工程与备份，复现到新工程时须换为该工程和新备份。不运行并行 Editor 写同一项目。`CODEX_CHARACTER_AXIS_APPLY_CANONICAL` 不为 1 时只隔离检查；任何隔离门槛失败都不覆盖正式动画。报告须为 `canonical_alignment_passed=true`；原生日志仍需另查。

4. 可选干净导入对照：不设置 `CODEX_CHARACTER_AXIS_REPAIR`，设置 `CODEX_CHARACTER_AXIS_FRESH_SUFFIX=FreshV2` 后运行诊断脚本，会使用主导入 helper 创建新的 HumanFreshV2 / OrcFreshV2，保留初次 Fresh 错轴证据。此入口本轮未执行；报告须观察 32 动作及 `fresh_pose_alignment_passed=true`，不可把预期当结果。

5. 数值通过后仍在素材验收地图中实际播放 idle 并审阅归档画面，核查站立、方向与材质；近战命中窗口使用实际片段长度约 0.4 秒。32 动作名对应不等于 32 动作都逐帧审阅，音效 / 音乐试听、无缝循环、碰撞、挂点、伤害和战斗流程继续分别验收。完成后清除上述环境变量，避免下一次普通 Editor 启动误用修复模式。

脚本 API 依据包括 Epic 5.5 的 [AnimPoseExtensions](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimPoseExtensions?application_version=5.5)、[AnimPoseEvaluationOptions](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimPoseEvaluationOptions?application_version=5.5)；骨骼取样明确关闭重定向和根运动提取。本轮没有把标准人形重定向作为角色可用的前提。

最终只读复核的机器清单：`E:\codex_game\docs\asset-engine-verification-2026-10-10.json`，包括正式对象类别 / 真实文件检查、角色 32 名与姿态门槛、证据报告 SHA256、最新脚本未再次 UE 执行的明确标记。
