# 首个完整单元：视觉生产只读预检

日期：2026-10-14，Asia/Shanghai。范围为 WPN-SWD-001 尺衡军剑、ARM-LGT-001 行路短衣、ENM-STN-001 沉石骑士。读取 asset-gen 技能、CLI、锁定依赖、现有来源与最新三段连招规格；本轮生成调用与费用均为零。报告不代表正式素材或运行验收完成。

## 工具与配置事实

- 正式入口 `F:/Ourgame/tools/scripts/Invoke-AssetGen.ps1 --help` 实际退出 0。它使用项目隔离 Python 3.12.14，并设置 UTF-8；SDK、requests、Pillow、numpy、rembg、pymatting、onnxruntime 均存在。锁文件为同目录 `asset-gen-requirements.lock.txt`。系统 Python 缺依赖和直接运行时的 GBK 帮助输出错误，不能代表正式入口不可用。
- GEMINI_API_KEY、GOOGLE_API_KEY、XAI_API_KEY、TRIPO3D_API_KEY 在 Process / User / Machine 均未发现。仅检查存在布尔值，未输出密钥。项目 `.env` / `.gateway.env` 和用户 `~/.gateway.env` 不存在。CLI 没有读取 dotenv 的实现；仅把密钥写进未加载的文件不会让它可用。
- Garden 模式检查退出 0：开关未启用、OPENAI_API_KEY 不存在，结果为 B-or-C。当前会话确实提供 `image_gen.imagegen`，因此可选 Host-Native 后端，无需新增外部 API key；没有调用来验证生成、额度或计费，不能称为免费。
- asset-gen 原文提供 Gemini/Grok/Tripo CLI 与参考→动作→抠图→清单流程，没有 Host-Native 条款，也没有 only-CLI 禁令。以它指导生产、明确替换图片后端是实施解释，不是原文已集成。另一个 gpt-image-2 技能的 Mode B 明确支持宿主工具。必须记录实际后端，不能用 CLI 的 7¢ 估算宿主费用。
- CLI 硬编码 `gemini-3.1-flash-image-preview`；官方[停用表](https://ai.google.dev/gemini-api/docs/deprecations)列其关闭日为 2026-06-25。即使补 key 也不能宣称该分支已可生成。后续须改为有效且账户可访问的模型；本轮未改脚本。
- 默认 BiRefNet 模型未缓存；ffmpeg / magick 不在 PATH。未安装或下载。静态样张不需要视频工具；后续视频抽帧须另核实绝对 ffmpeg 路径，不能凭技能中的命令就宣称可用。

## 可重用来源与真实缺口

`source-assets/prototype/first-room-v1/manifest.json` 明确标为 Blender 离线 CC0 转绘的历史原型：人类、兽人各 idle8 / walk8 / attack6 / hurt2 / death8，共64帧，另5图标；hurt 是 idle 倾斜的替代，不是原始受击动作。可复用技术导入、脚底锚点与读取方式，不将这些帧改标正式军剑三段、轻甲换装或沉石骑士。

Kenney Mini Dungeon 包内 CC0 许可和实际 `character-human.fbx`、`weapon-sword.fbx`、`shield-round.fbx` 可作比例/握持/转绘对照；历史剑与盾图标仍是占位图。没有现成行路短衣可编辑分层、沉石骑士厚盾/石腿形象，或这两个角色的完整正式动作集。现有原包许可不自动成为新生成图片的许可；新素材需保留实际生成后端、prompt、原始输出与采用的授权依据。

## 最小风格样张批次：3张，额外纠错最多1张

| 次序 | 内容 | 本次评审目标 |
| --- | --- | --- |
| P01 | 原创成人冒险者穿行路短衣：腰长褐软皮衣、软肩、外露膝、小布包；右向完整站姿，双手可辨，1K | 人物比例、轮廓、皮革笔触、后续拆层基准；武器独立 |
| P02 | 尺衡军剑单体：单手直剑、短护手、清楚握柄与刃尖，1K；沿已接受P01的风格 | 轮廓和手部尺度；之后独立武器层与图标复用 |
| P03 | 沉石骑士：短颈、石腿、厚盾前压，右向完整站姿，1K；沿同一风格基准 | 石材/盾沿辨识、身体与盾的近远关系 |

先审P01，失败仅允许一次有明确原因的修订；仍失败则停止，不继续浪费P02/P03。三张是在游戏尺寸下审查的静态参考，不能冒充完整角色帧、可编辑分层或动作。保持一个朝向，另一朝向在后续明确镜像合同中处理，不另付费生成镜像。Gemini/Grok按技能用纯实色背景再抠图；Host-Native 若通过专用参数提供真实alpha，必须实读像素和叠底QA，不把棋盘格画面算透明。

## 费用、停止条件与重试

外部CLI备选建议使用官方有效的 `gemini-nano-banana-2.1`。官方[价格页](https://ai.google.dev/gemini-api/docs/pricing)列1K输出1120图像tokens、$30/百万图像tokens，即 **$0.0336/张**；输入$1.50/百万tokens，文本/思考输出$7.50/百万。3张输出基价$0.1008，连同最多1张纠错的输出基价$0.1344，另计输入及思考。

**可向主线程建议的授权数额：税前生成用量最高 US$0.30、最多4个实际请求。** 需后续先实现并确认每请求总输入≤4096、总输出≤2048 tokens、SDK仅一次尝试、无grounding/其他付费工具；按所有输出都用较高$30/百万保守计算，`4×(4096×1.50+2048×30)/1,000,000 = $0.270336`，留$0.029664余量。当前CLI未实现这些限制和真实用量账本，也未换有效模型，**现在不能保证该上限、不能据此启动付费调用**。税费、换汇与宿主图像工具不属于上述计价；严格含税上限须先取得实际账户账单规则。该数额仅覆盖风格样张，不覆盖完整动作制作。

低价替代 Grok 官方[价格](https://docs.x.ai/developers/models/grok-imagine-image)为输出$0.02、每张参考输入$0.002；4次、每次最多一个参考和一个输出的保守用量为$0.088，可建议税前US$0.10，但技能已提示精确构图/角色一致性较弱。也没有可用key，不把它写成已准备好。

逐次执行和记账，禁止自动连发/无限重试/自动换更贵模型。鉴权、配额、型号错误立即停止；超时或返回不完整先核对供应商任务/账单，不假定未收费再投。图像CLI没有Tripo的可恢复任务sidecar；不能把Tripo `resume` 的说明套到图片。所有尝试（包括失败和纠错）计入请求上限；用量未知时停止。无具体批次费用授权前维持零调用。Host-Native 后端须由主线程明确选择和记录宿主额度/费用边界，不与上述CLI预算混用；本子任务不向用户另行发问。

## 完整单元的后续分层与帧方案

按最新 `combo-spec.md`，军剑主攻须分别具备肩侧横斩、回身斜切、踏步下斩及独立进身斜斩武器技，保留各自前摇/有效/完整恢复；一次离地只用第一段。不要把旧单斩或同一6帧素材换名字算三段。共同玩家动作、轻甲形变与受击/死亡也须覆盖实际状态；沉石骑士另需休眠/苏醒、接近、盾锋冲阵、盾沿横撞、失手/撞墙完整恢复、受击和死亡。

采用共同身体骨架＋近远手臂/腿＋轻甲前后层＋一份独立剑层；剑以grip_primary和weapon_tip定位，按姿态分近/中/远遮罩而不复制整把剑。石像的身体与盾分层。保留可编辑源与关键姿态，再导出所有已承诺动作所需帧；固定逻辑canvas、ground pivot、逐帧握点、裁剪偏移和一次镜像规则。512×512角色逻辑画布/脚底(256,440)、独立武器画布与握柄锚点沿D12，不把PNG边长当世界厘米。动画只消费真实事件，图片不决定伤害或命中时间。

## 离线图集校验器

已交付 `tools/scripts/validate-content-atlas.py`、`tools/scripts/tests/test_content_atlas.py` 和本目录 `atlas-schema.md` / `example-manifest.json`。范围仅固定首件v2，当前22个必需动作绑定（玩家13、石骑士9），全部动作必须有完整帧层。示例为 `template_unfulfilled`、0个实际帧、`runtime_complete=false`，实际CLI退出1；没有把空模板或旧64帧改标为正式完成。

TDD实际日志摘要（完整最终输出在 `visual-preflight.json#/atlas_validation/green_full_python_suite/log`）：

```text
RED: real validator API skeleton — 29 tests, 27 expected assertion failures, 0 errors
GREEN: first implementation — 29 tests, OK
RED: phase sample coverage + null units — 31 tests, 2 expected failures, 0 errors
GREEN: 31 atlas + 4 audio tests, OK
RED: explicit air-primary binding — 32 tests, 1 expected failure, 0 errors
RED: generated provenance + unknown geometry kind — 34 tests, 2 expected failures, 0 errors
GREEN: 34 atlas + 4 audio tests, OK
RED: prototype directory relabel — 35 tests, 1 expected failure, 0 errors
FINAL GREEN: 39 tests (35 atlas + 4 existing audio), OK, exit 0
```

完整Python工具测试命令：

```powershell
& 'F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe' -X utf8 -B -m unittest discover -s 'F:\Ourgame\tools\scripts\tests' -v
```

另以CLI读取完整合成夹具，退出0：真实解码1张微型测试PNG，核对210个帧层记录；这是多层/多动作的数据夹具，不是210张生产图片。实际来源预检另解码历史原型的64角色帧＋5图标，均为256×256 RGBA。测试创建的微型PNG均在临时目录，未修复或改写项目原图。只读性测试也核对manifest、许可、PNG字节和文件集合保持原样。

校验覆盖真实PNG解码、8-bit RGBA与有效alpha、逻辑尺寸/脚底一致、源哈希、所需动作/帧/完整层、绝对阶段时轴/每攻击阶段有采样、条件emit点/握点、左右一次镜像合同、武器甲双向许可、来源及授权证据与生成prompt哈希、占位/模板/已知prototype目录拒绝、路径不越界。当前每层要求可见内容，不支持完全隐藏空层、trim atlas、异形长武器或非对称单独左向绘制；schema已写清边界。

`passed=true` 始终伴随 `engine_executed=false`、`runtime_status=not_evaluated`。它不能识别绘画是否真的手绘、不同动作是否只是重复图、握点是否画在真实手柄上，也不能证明引擎确实只镜像一次或许可声明真实；这些仍需人工来源/画面审阅和运行核查。普通交互/换装状态的实际表现、极端攻速/射程、声音与首区流程不在该离线门槛内。没有启动Editor/Blender、调用生成API、安装依赖或修改全局配置；当前正式内容完整验收数量仍未由本任务增加。
