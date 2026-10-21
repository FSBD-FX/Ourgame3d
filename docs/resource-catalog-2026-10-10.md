# 《失落城堡》同类游戏：资源、插件与 Skills 清单

> 本文保留 **切换前 Unity 方案的收集快照**。用户随后于同日明确改用 UE5，当前版本、实际接入与素材状态以 [UE5 准备状态](preparation-status-2026-10-10.md) 和根 README 为准；下方 Unity 包推荐不代表已装入当前工程。

核查日期：2026-10-10（Asia/Shanghai）。本清单是制作工具和素材的准备记录；不是已运行的 Unity 工程，也不是全部内容的美术验收。

## 1. 事实、推理与风险

**事实**：用户已选 Unity + C#、Blender，项目根目录为 `E:\codex_game`；首个版本先做单人，之后再考虑合作。参考游戏《失落城堡》在官方页面中属于带 Roguelike 要素的动作 RPG / 清版动作游戏，包含随机地牢和合作玩法。它的玩法参考价值不代表原作角色、场景、音乐或 UI 可以直接复用。[原作官方页面](https://store.steampowered.com/app/434650/Lost_Castle/)

**推理**：本项目应优先验证移动、近战命中、敌人反应、战利品和房间推进。建议先用固定镜头、3D 角色与场景制作一个有纵深移动的战斗房间，保留 2.5D 观感；这是待实玩确认的建议，尚未确定最终美术与视角。输入、角色状态、伤害结算与表现分开，给后续合作留接口；首版暂不引入联网框架。

**风险**：单人之后增加合作仍会涉及状态同步、随机数、掉落归属、存档和复活规则，不能视作只加一个插件。工具源码、已安装程序、已下载素材和实际跑通是不同状态。目前没有 `Game/` Unity 工程，也没有可玩版本。工时和预算尚无可靠估算，不在本清单中编造承诺。

### 状态说明

| 标记 | 含义 |
| --- | --- |
| 本机已核实 | 找到文件或执行了版本命令；具体验证范围单列 |
| 已收录，待接入 | 源码、Skill 或素材在项目中，尚未完成实际使用验证 |
| 官方候选 | 查阅官方说明，尚未下载、安装或导入 |
| 条件候选 | 还依赖账号、付费服务、许可或额外运行环境 |

## 2. 本机环境

| 项目 | 核查结果 | 路径 / 限制 |
| --- | --- | --- |
| Unity 编辑器 | 2021.3.45f1、2022.3.60f1、6000.0.42f1、6000.0.43f1 | `G:\UNITY\<版本>\Editor\Unity.exe`；读取 EXE 产品版本，未验证启动、许可证、编译 |
| 首次接入建议 | 先复用 6000.0.43f1 | 最终版本在工程创建和包兼容检查时固定；不为准备工作盲目升级 |
| Blender | **5.2.2 LTS** | `E:\SteamLibrary\steamapps\common\Blender\blender.exe`；`--version` 已验证，addon 未运行 |
| Python | 系统 3.14.6；Codex 随附 3.12.14 | 系统：`C:\Users\22499\AppData\Local\Programs\Python\Python314\python.exe`；随附：`C:\Users\22499\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` |
| uv / uvx | **0.12.3，已安装** | `C:\Users\22499\AppData\Roaming\Python\Python314\Scripts\uv.exe` 与 `uvx.exe`；不在当前 PATH，接入时用绝对路径 |
| Git | 2.55.0.windows.2 | 命令已核实；三个工具仓库当前工作区均干净 |
| GPU | RTX 3060 Laptop，6144 MiB 显存 | `nvidia-smi` 核实；不能据此推断 UniMate 推理可用 |
| 录屏 / 转码 | 待验证 | 当前 PATH 和有限常见位置未找到 ffmpeg / ffprobe；未做全盘扫描，不能断言未安装 |
| Unity / Blender MCP | **未连接** | 当前会话无对应 MCP 工具；没有把源码收录当作安装完成 |

旧 Godot / Knight 工程、已有 .NET SDK 不等于本项目 Unity 工具链。Python 环境之间也不共享依赖；尚未验证系统 Python 3.14 对各工具完整依赖的兼容性。

## 3. 已收录的制作工具

| 工具 | 本地位置与固定版本 | 能做什么 | 当前状态与边界 |
| --- | --- | --- | --- |
| [MCP for Unity](https://github.com/CoplayDev/unity-mcp) | `tools/unity-mcp`；main，10.2.0；`30d22075093d1d35dfb0091c1c7550e9ad948577` | 编辑场景、Prefab、C#，读取 Console，控制 Play、截图、测试 | MIT；仅源码已保存，Unity 插件和 Python 服务都未接入；并非游戏模板 |
| [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) | `tools/mcp-for-blender`；2.1.3；`60d2a31b4632a7bc178f3dd636f7e68dfb5c8ae4` | Blender 场景、材质、建模、Python、模型导出 | MIT；仅源码已保存，addon / server 未接入；当前 checkout 的 config 缺失问题需在接入时确认 |
| [UniMate](https://github.com/Friedrich-M/UniMate) | `tools/UniMate`；`2c5b384715aa63d8639b1ed7eb74bfe614570c7a` | 异构骨架的文本动作生成研究 | 代码 MIT，**官方预览权重 CC BY-NC 4.0**；依赖、权重、数据均未下载，Windows / 6 GB 推理未测；暂作研究候选 |

UniMate 的权重许可于本次核查重新读取确认；代码许可不覆盖模型权重和训练数据。自制骨架预处理已有部分实现，但不能据此宣称整条自制角色生成链已经可用。[官方权重 LICENSE](https://huggingface.co/Linzhan/UniMate/blob/main/LICENSE)、[详细核查](unimate-evaluation.md)

两套 MCP 接入优先采用本机连接，固定插件 / 服务版本，按源码关闭遥测。Blender 的安全模式不是完整进程隔离。具体传输、环境变量和源码问题见 [工具链记录](toolchain.md)。以上均是编辑器制作工具，不应成为玩家运行游戏的必需服务。

## 4. Unity 包与插件候选

以下为官方资料核查，**本项目尚未安装这些包**。官方文档展示的已发布包版本不等于当前编辑器可无条件升级到的版本；工程创建时由 Package Manager 解析兼容版本，再固定 `manifest.json` 和锁文件。

| 优先级 | 包 / 插件 | 本项目用途 | 版本与选择边界 |
| --- | --- | --- | --- |
| 基础 | [URP](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/urp-introduction.html) | 3D / 2.5D 的灯光、阴影与材质基础 | 创建匹配编辑器的 URP 工程；根据实际素材选择 Renderer，先验证灯光与材质 |
| 基础 | [Input System](https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.inputsystem.html) | 键盘 / 手柄输入与动作映射 | Unity 6000.0 官方页列出 released 1.20.1；实际兼容性待解析 |
| 验证 | [Unity Test Framework](https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.test-framework.html) | 伤害、掉落等逻辑测试，以及必要的 Play Mode 测试 | 核心包随编辑器匹配；测试不能替代实际操作验收 |
| 按需 | [Cinemachine](https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.cinemachine.html) | 跟随、镜头边界、震屏与镜头切换 | 官方页列出 released 3.1.7；3.x 与旧 2.x 教程存在 API 差异 |
| 按需 | [ProBuilder](https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.probuilder.html) | 房间、墙体与碰撞的灰盒验证 | 官方页列出 released 6.0.9；首个小房间也可直接用基础网格 |
| 交付 | [Unity Recorder](https://docs.unity3d.com/6000.0/Documentation/Manual/com.unity.recorder.html) | 从实际 Play Mode 记录视频、图像和音频 | 官方页列出 released 5.1.7；录制配置与输出格式待实测 |
| 可选 | [PrimeTween](https://github.com/KyryloKuzyk/PrimeTween) | UI、拾取和短时表现动画 | 免费核心和 PRO 内容分开；使用自定义许可，**不是 MIT**，商业游戏使用与源码再分发规则不同 |

PrimeTween 的许可见 [官方 LICENSE](https://github.com/KyryloKuzyk/PrimeTween/blob/main/LICENSE)。暂不引入完整 Roguelike 模板、联网框架、收费控制器或大型行为树；先由一个房间证明确有需求，再决定依赖。

项目素材默认走显式 **FBX** 导入。Unity 支持的导入方式不能证明动画重定向、比例、材质或碰撞已经正确；GLB / glTF 通路要另核对导入包。`.blend` 原文件留在 `source-assets/`。[Unity 模型导入](https://docs.unity3d.com/Manual/ImportingModelFiles.html)、[Avatar 配置](https://docs.unity3d.com/Manual/ConfiguringtheAvatar.html)

## 5. 素材来源

“免费”按列出的具体包或档位判断，不代表整个网站、全部源文件或所有扩展免费。CC0 与账号服务许可分开记录；保留每次实际下载包中的许可。

| 资源 | 适合用途 | 官方许可 / 成本 | 实际状态与检查边界 |
| --- | --- | --- | --- |
| [Kenney Modular Dungeon Kit](https://kenney.nl/assets/modular-dungeon-kit) | 地牢模块与原型房间 | CC0，免费，可选捐赠 | 官方页候选；未下载检查格式、拼接点、碰撞和 URP 材质；不是随机地牢系统 |
| [Quaternius RPG Character Pack](https://quaternius.com/packs/rpgcharacters.html) | 6 个已绑定、带动画的奇幻角色 | CC0，免费 | 官方提供 FBX / OBJ / Blend / glTF；未下载，Humanoid 映射待测；OBJ 不携带骨骼动画 |
| [Quaternius Fantasy Props MegaKit](https://quaternius.itch.io/fantasy-props-megakit) | 武器、宝箱、家具等道具 | CC0；Standard 免费，Pro / Source 付费 | 未下载；不能把 Source 档的 Unity 工程、碰撞等功能视作免费档已包含 |
| [Quaternius Universal Animation Library 2](https://quaternius.itch.io/universal-animation-library-2) | 移动、近战等动作候选 | CC0；Standard 免费，Source 付费 | 未下载；130+ 的完整宣传数量不能直接算作已获得的免费动作；须核对具体下载档位 |
| [Kenney UI Adventure](https://kenney.nl/assets/ui-pack-adventure) | 按钮、面板、血条、背包原型 | CC0，免费 | **已下载并解包**，实际有 PNG / SVG / XML；已检查包内 License.txt，尚未 Unity 导入 / 九宫格配置 |
| [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) / [RPG Audio](https://kenney.nl/assets/rpg-audio) | 命中、拾取与交互音效 | CC0，免费 | **Impact Sounds 已下载，实际为 OGG**；RPG Audio 仅官方候选；未试听挑选或设置混音 |
| [Abstraction Free Music Loop Bundle](https://tallbeard.itch.io/music-loop-bundle) | 原型背景音乐循环 | CC0，免费，可选捐赠 | 未下载；季度分包，曲风、循环衔接和实际格式待检查；其他 Patreon 内容不纳入此许可结论 |
| [Poly Haven](https://polyhaven.com/) | HDRI、PBR 材质、部分道具参考 | [资产 CC0](https://polyhaven.com/license) | 未下载；站点标志、文字和预览等不能一并当作 CC0；真实感资产需评估风格、纹理体积与 LOD |
| [Mixamo](https://www.mixamo.com/) | 人形动作与自动绑定备选 | Adobe 账号；按 Adobe 条款可用于商业游戏，非 CC0 | 条件候选，未登录 / 下载；官方 FAQ 标明 Adobe ID 中国国家码不可用，不假定本账号可访问；主要面向双足人形 |

Mixamo 依据：[Adobe 官方 FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html)。角色动作进入游戏前仍要制作 Animator、武器挂点、命中窗口、受击打断、根运动 / 原地移动规则；动画库不会替我们完成战斗逻辑。

### 本轮已实际收集的素材

位置：`E:\codex_game\source-assets\third-party\kenney\2026-10-10`。

| 包 | ZIP 大小 | 原件与校验 |
| --- | --- | --- |
| UI Adventure | 577,463 字节 | 保留 ZIP、完整解包目录与 License.txt；已记录 SHA256 |
| Impact Sounds | 800,850 字节 | 保留 ZIP、完整解包目录与 License.txt；已记录 SHA256 |

两个 ZIP 合计 1,378,313 字节；下载没有付款。下载清单见 [acquisition-manifest.json](../source-assets/third-party/kenney/2026-10-10/acquisition-manifest.json)。当前状态为 `downloaded_and_license_checked_not_imported`，未生成展示图、未试听，也未认定为最终美术。

### 本机旧资料

发现 `G:\Unity hub\project\kongdong\first\Hollow-Knight`、其副本、相关课程 ZIP / unitypackage 与 `G:\Unity hub\Assests\课程素材`。这些是旧工程 / 课程缓存，**来源许可与复用范围未核实**，不导入本项目，不作为可商用素材。两个已检查的 `Asset Store-5.x` 缓存目录为空，不能据此推断账号从未购买资产。

## 6. Skills 清单

“Skill 可读”表示工作流程文件存在，不能证明其依赖、账号、API 或目标编辑器已经能运行。Skills 是制作说明；MCP 是操作编辑器的通路，两者不能互相替代。

| Skill | 本地位置 | 本项目用途与状态 |
| --- | --- | --- |
| **unity-mcp-orchestrator** | `E:\codex_game\.agents\skills\unity-mcp-orchestrator\SKILL.md` | 已收录 SKILL 与 4 份引用文件，5 文件哈希一致；场景、Prefab、C#、Console、测试工作流；依赖尚未连通的 Unity MCP |
| **asset-gen** | `E:\codex_game\.agents\skills\asset-gen\SKILL.md` | 已收录完整目录，8 文件哈希一致；视觉资产流程入口；生成依赖和密钥未就绪，首次付费前确认花费 |
| **imagegen** | `C:\Users\22499\.codex\skills\.system\imagegen\SKILL.md` | 内置图像生成 / 编辑工具在本会话可调用；适合概念图、UI、贴图，不能直接产出可编辑骨骼模型；仍遵循本项目 asset-gen 与费用规则 |
| generate2dsprite | `C:\Users\22499\.codex\skills\generate2dsprite\SKILL.md` | 2D 动作帧、对齐与抠图备选；含 Godot 流程，Unity 的切片、Pivot、AnimationClip 需另配 |
| generate2dmap | `C:\Users\22499\.codex\skills\generate2dmap\SKILL.md` | 支持 Unity_Tilemap 的 2D 地图与碰撞元数据；不产出可编辑 3D 地牢 |
| sprite-gen | `C:\Users\22499\.codex\skills\sprite-gen\SKILL.md` | 另一个精灵流程；本机环境部分存在，但 Grok CLI / OAuth 未验证，暂不与主流程同时引入 |
| threejs-3d-generator | `C:\Users\22499\.codex\skills\threejs-3d-generator\SKILL.md` | 仅复用生成模型与导出的部分；Three.js 运行代码不用于 Unity；Tripo 密钥未配置 |
| threejs-audio-generator | `C:\Users\22499\.codex\skills\threejs-audio-generator\SKILL.md` | 仅复用音频生成 / 转换部分；WebAudio 代码不用于 Unity；ElevenLabs 密钥未配置 |
| screenshot | `C:\Users\22499\.codex\skills\screenshot\SKILL.md` | 桌面截图备选；Unity MCP 可用后优先采集游戏视图，展示前按归档规则保存 |
| video-edit | `C:\Users\22499\.codex\skills\video-edit\SKILL.md` | 已有录像的剪辑与转码；不是录屏器，ffmpeg 通路待核实 |
| **superpowers:brainstorming** | `C:\Users\22499\.codex\plugins\cache\openai-curated-remote\superpowers\6.4.2\skills\brainstorming\SKILL.md` | 下一阶段收敛战斗、视角和首个房间范围；当前盘点不等于已通过设计验收 |
| **superpowers:systematic-debugging** | `C:\Users\22499\.codex\plugins\cache\openai-curated-remote\superpowers\6.4.2\skills\systematic-debugging\SKILL.md` | 接入、编译或运行失败时基于证据定位 |
| **superpowers:verification-before-completion** | `C:\Users\22499\.codex\plugins\cache\openai-curated-remote\superpowers\6.4.2\skills\verification-before-completion\SKILL.md` | 完成声明前验证；对游戏还要实际操作和审阅运行录像 |
| skill-creator / skill-installer | `C:\Users\22499\.codex\skills\.system\skill-creator\SKILL.md` 与 `C:\Users\22499\.codex\skills\.system\skill-installer\SKILL.md` | 已存在；验证过 Blender→FBX→Unity 后，再沉淀项目专用 Skill，暂不批量安装不相关 Skills |

路径与版本来源见 [项目 Skills 索引](../.agents/skills/README.md)。本轮未安装新的全局 Skill 或修改 Codex MCP 配置；项目内两份 Skill 是完整复制，尚未通过它们执行实际资产生成或编辑器操作。

当前环境的 asset-gen 依赖核查只覆盖系统 Python 3.14：`requests`、`xai_sdk`、`google.genai` 未发现，Pillow 存在；不能推广为所有 Python 环境均缺失。所查环境变量中未配置生成密钥，也未检查所有私有配置。asset-gen 使用 `TRIPO3D_API_KEY`，threejs-3d-generator 使用 `TRIPO_API_KEY`，后续接入要按各自说明配置，不要混用名称或把密钥写入项目。

Three.js 的 game-director / qa-release 面向浏览器游戏，不能当作 Unity 主工程或 Unity 验收；game-design-role-tool 指向另一个职业规划项目，不属于本游戏制作流程。插件目录检索未发现已连接的 Unity / Blender 编辑器插件，这不是对整个插件市场的穷尽结论。Figma 等现有设计能力可选，不是首个战斗房间的前置依赖。

## 7. 建议采用的最小组合与下一步

1. **先建立并启动 Unity 工程**：复用现有 Unity，采用匹配的 URP、Input System；检查 Console / 编译和 Play，再固定实际包版本。
2. **验证制作通路**：连接 Unity MCP 与 Blender MCP，用一个简单 FBX 检查缩放、朝向、材质、骨骼和动画；失败时先缩小问题，不引入更多生成服务。
3. **再下载一个统一风格的角色与地牢包**：优先核查 Quaternius RPG Characters、免费动作档和 Kenney Dungeon；用少量代表性资产验证导入与重定向，再扩大内容量。
4. **做首个单人战斗房间**：建议范围为一个角色、一种武器、一种敌人、一个掉落，覆盖移动→攻击→受击→清房→拾取；摄像机、美术和手感由实际试玩确认。
5. **采集证明与更新资产表**：运行截图 / 短录像先归档到 `E:\OurGame\Knight\过程图稿与视频`，再展示；合适时采用 Recorder。将真正进入工程的资源、许可、修改和实际版本写入 README。

当前已收集的两个素材包免费，无付费生成、模型权重下载或云端推理支出。后续美术统一、绑定重定向、音效选择与许可证核查仍需制作成本；现成资源只能减少起步工作。使用收费素材档位、API 或其他付费生成前，先给出具体内容与费用并遵循首次付费确认约定。UniMate 不作为首版前置依赖。
