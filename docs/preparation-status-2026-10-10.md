# UE5 制作准备状态

> 2026-10-12：主目录已指定为 `F:\Ourgame`；当前路径与新目录启动核验见 [迁移记录](project-location-2026-10-12.md)，长期内容系统及逐次要求见 [需求台账](../项目需求台账.md)。下文的E路径与2026-10-10运行报告属于历史证据。

> **2026-10-11方向更新**：用户已确定参考《失落城堡》一、二部制作2.5D横版动作游戏，继续UE5，首版单人。下面保留2026-10-10的环境验证记录；3D素材验收不能视作2.5D画面已完成。当前方案与资源缺口见 [最新方向](2.5d-direction-2026-10-11.md)。

核查日期：2026-10-10，Asia/Shanghai。当前目标为 `E:\codex_game` 中的 UE5 + Blender 单人动作地牢原型，后续扩展合作。

## 事实、推理、风险

**事实**：用户已明确从 Unity 改为 UE5。实际使用 UE5.5.4、Blender5.2.2；C++ 工程和 Editor 插件真实构建成功，图形 Editor 已启动。Blender MCP 场景读写 / FBX 导出、UE MCP 正式配置的 STDIO 握手 / 真实场景读写已通过。8 包免费 CC0 素材完整落盘并保留许可、来源和哈希。当前没有角色控制、战斗、敌人或地牢循环。

**推理**：先用已取得的 Mini Dungeon 人类 / 兽人及其原包动作、Modular Dungeon 房间、现有 UI / 音频做一个单人战斗房间，可验证视角和打击感。无需为了“全部准备”安装所有候选插件、生成模型或联网框架。后续按真实玩法和美术需求补足。

**风险**：UE MCP 为实验性社区桥接，固定版本没有完整 LICENSE 文件；本地验证与分发须区分。当前 30 个工具不包含任意 Python 执行或 PIE 起停，导入与运行检查需要 UE 自身自动化。简化角色骨架不直接适配标准人形动作。16 GB RAM / 6 GB VRAM 限制并行构建和重型渲染；当前以 DX11、关闭 Lumen / Nanite / 光追的轻量配置起步。最终画面、输入、碰撞、动作、音频、存档与打包仍需原型实跑验证。

## 已通过的制作环境检查

| 检查 | 实际结果 / 证据 |
| --- | --- |
| UE 版本 | G:/UE_5.5；5.5.4 / CL40574608 |
| C++ 工具链 | 补装 VS2022 MSVC14.38，UBT 实际选择14.38.33145与 Windows SDK10.0.19041.0 |
| Editor 构建 | 退出码0，22动作；UnrealGame/Saved/Bootstrap/build-editor-20261010-094110.log |
| 基础工程 | CodexDungeon Runtime / Editor Target、EnhancedInput、PythonScriptPlugin、EditorScriptingUtilities、UnrealMCP |
| 准备地图 | /Game/Maps/Foundation；7个准备Actor和空 BP_WorkspaceMarker；foundation-report.json |
| 图形 Editor | RTX3060 / D3D11 / SM5；editor-20261010-094422.log；不能用 nullRHI 建图代替该结果 |
| UE MCP 读取 | global config command/args/env → STDIO → bridge → 非空Actor及属性；tools/runtime/unreal-mcp/logs/2026-10-10_094554/verification.json |
| UE MCP 写入 | 创建 / 变换 / 读取 / 删除诊断Actor，核对诊断对象已删除、原Actor名字未变；logs/2026-10-10_094856/verification.json |
| Blender MCP | 36工具，真实建模 / 保存 / 导出；source-assets/blender-mcp-smoke/2026-10-10_092600/verification.json |
| 免费原包 | 8包 ZIP，94,920,296字节；逐包来源 / 许可 / CRC / SHA256留存 |
| 中文字体 | Noto Sans CJK SC Regular OTF，16,437,364字节；完整OFL1.1与版权声明；FontFace / Runtime Font已真实导入，font-import-report.json success=true；中文UI实景 / 打包未测 |
| 生成工具依赖 | tools/runtime/asset-gen 独立 Python3.12.14；64包依赖与实际import通过；FFmpeg7.1可启动 |
| Skills | asset-gen / unreal-mcp-orchestrator；新 Skill 官方 quick_validate 通过；Unity Skill 仅历史参考 |
| 代表素材 | 14项来源、80个对象：6 StaticMesh、2 SkeletalMesh、2 Skeleton、64 AnimSequence、3 Texture2D、3 SoundWave；最终完整检查无缺失任务 |
| 角色动画 | 人类 / 兽人各32动作，实际补齐左右近战；动画导入根轴 +90° 后隔离 / 正式姿势检查通过，未用 Actor 倾斜掩盖问题 |
| 单位交接 | Blender 1×1×2m probe → UE StaticMesh 实测 XYZ=100×100×200cm，最长轴Z |
| 素材实跑 | AssetIntake 地图；图形 PIE 8.016秒、6个采样、正常停止；角色站立、待机与贴图可见；pie-report.json passed |
| 启动器 | 首次实际启动 Blender / 复用 UE，二次执行两个 PID 均未变；evidence/preparation/launcher-idempotence-2026-10-10.json |
| 最终原生连接 | 当前 UE 19个Actor及角色属性可读，Blender新进程场景可读；evidence/preparation/final-native-check-2026-10-10.json |

80 个对象是代表来源在专用目录中的实际对象数，不包含字体、验收材质 / 地图及诊断副本，也不等于 8 个原包全部导入。中文字体另有 2 个正式对象。最后一次完整导入检查为 `asset-import-report-20261010T021821_408549Z.json`，采用已有资产检查模式；14项跳过重导的提示属于保留既有资产的记录，不表示原 FBX 没有着色警告。

最初仅导入每角色30动作，30fps取样拒绝半帧边界的左右近战片段；修复为60fps动画独立导入后补齐32段。随后发现原动画根轴与网格参考姿势不同，通过隔离试验确定动画导入 `roll=+90°`，正式64段动画已修复并保存；`character-axis-repair-report.json` 为 `canonical_root_alignment_passed_pose_samples`。原资产备份、失败对照及原生日志留存。源近战约0.416667秒，UE实际片段为0.400000006秒，后续命中窗口以引擎内实际片段为准。

运行证明已按归档约定保留于 [v004索引](E:/OurGame/Knight/过程图稿与视频/2026-10-10_UE55角色轴修复与运行采样_v004/index.json)，包含原件、展示副本、6个真实 PIE 帧、时间戳、报告、哈希和 [低帧率实跑采样](E:/OurGame/Knight/过程图稿与视频/2026-10-10_UE55角色轴修复与运行采样_v004/展示副本/asset-intake-low-fps-pie-samples.mp4)。FFmpeg完整解码180个编码帧 / 6秒 / 1280×720，退出0；制作代理及主代理均审阅首 / 中 / 尾，角色站立且道具材质可见。视频的30fps编码来自约1fps的6个源采样，没有实时帧率、输入操作、音频试听或游戏玩法验收主张。首帧取景较广，后续取景较近，索引已记录。

## 启动入口与配置

```powershell
& 'E:\codex_game\tools\scripts\Start-ProjectTools.ps1'
& 'E:\codex_game\tools\scripts\unreal-status.ps1'
& 'E:\codex_game\tools\runtime\unreal-mcp\.venv\Scripts\python.exe' 'E:\codex_game\tools\scripts\verify-unreal-mcp.py' --global-config
```

Codex 配置为 `C:\Users\22499\.codex\config.toml`。改动前副本为 `C:\Users\22499\.codex\backups\config.pre-unity-blender-20261010-092130-530.toml`，原有设置保留。当前启用 blender-mcp / unreal-mcp，unity-mcp 已禁用，旧 node_repl / godot-ai 配置保留。STDIO 由 Codex 拉起，不额外常驻启动。两个编辑器桥接只监听 loopback。

当前会话原生工具已自动加载（Blender36 / Unreal30），两套均已实际调用成功。UE 原生中文对象名创建 / 变换 / 读回 / 删除通过，前后19个Actor名称集合相同；证据为 `evidence/preparation/native-unreal-utf8-roundtrip-2026-10-10.json`。Blender 原生证据为 `evidence/preparation/native-mcp-check-2026-10-10.json`。此前独立官方 MCP 客户端已按正式配置完成真实场景读写；本次无需用户重启 Codex。

## 已知缺口与下一步

| 项目 | 当前边界 | 下一步 |
| --- | --- | --- |
| 首个可玩房间 | 尚无游戏玩法 | 确认视角、接入移动 / 攻击 / 受击 / 敌人 / 掉落 / 清房 |
| 动作与武器 | 原包32动作已导入、根轴修复及待机实跑；简化骨架，UAL2未重定向 | 接通移动 / 攻击状态，逐个核查动作、武器挂点与实际片段命中窗口 |
| 地牢碰撞 / 导航 | 模型候选不等于可走场景 | 原型房间里检查地面、墙体、门口与敌人移动 |
| 音频 | 来源 / 格式核查，不等于曲风 / 循环验收 | 实跑试听、响度与衔接检查 |
| 中文UI / 发布包 | 字体对象已导入；尚无UMG中文实景、Game Target独立构建或打包 | 首个房间加入UI后核查中文显示，再验证运行包 |
| 付费生成 / 账号 | 密钥未配置、模型权重未下、无付费调用 | 明确需求 / 当前报价后确认首次花费；不阻塞免费原型 |
| UE MCP许可 | README称MIT，完整许可文件缺失 | 分发插件前补证；保持Editor-only，不计入运行包 |
| UniMate | 预览权重非商业许可；未安装 | 保留研究，首版不依赖 |
| 合作模式 | 用户确定后续再做 | 单人逻辑先保持输入 / 战斗 / 状态边界，后续单独选联网方案 |
| 版本与备份 | Git已初始化，无提交 / 远端 / 另盘备份 | 制作第一阶段形成检查点后建立可恢复版本；不自动推送 |

旧 Unity 准备工程和切换前资源清单保留历史。详细来源见 [素材记录](asset-preparation-2026-10-10.md)、[字体记录](font-preparation-2026-10-10.md)、[UE工具核查](ue5-mcp-evaluation-2026-10-10.md)、[UE构建记录](unreal-bootstrap-2026-10-10.md)、[Blender连接](blender-connection-2026-10-10.md)。
