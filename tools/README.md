# 制作工具与脚本

当前项目使用 UE5 + Blender。源码、安装环境和实际编辑器连通分别记录，不能互相替代。

| 目录 | 来源 / 固定版本 | 状态 |
| --- | --- | --- |
| unreal-mcp | [chongdashu/unreal-mcp](https://github.com/chongdashu/unreal-mcp)，4e5f00da50733190481311e254d16d137a84ef33 | Python 依赖已锁定，项目插件已编译，真实 Actor 读写通过；完整 LICENSE 缺失见核查文档 |
| mcp-for-blender | [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender)，60d2a31b4632a7bc178f3dd636f7e68dfb5c8ae4 | 实装官方 PyPI 2.1.3 wheel；Blender 5.2.2 场景读写 / FBX 导出通过 |
| ue5-mcp | [VedantRGosavi/UE5-MCP](https://github.com/VedantRGosavi/UE5-MCP)，c284cecd5fbba58778a07c26e417df15f112ad50 | 仅设计文档，无可安装服务 / 插件，不运行 |
| unity-mcp | [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp)，30d22075093d1d35dfb0091c1c7550e9ad948577，10.2.0 | 历史 Unity 方案，Codex 服务已禁用 |
| UniMate | [Friedrich-M/UniMate](https://github.com/Friedrich-M/UniMate)，2c5b384715aa63d8639b1ed7eb74bfe614570c7a | 离线动画研究候选；代码 MIT / 预览权重 CC BY-NC 4.0；未安装模型 |

runtime/ 保存各工具独立 Python 环境与日志，不向系统 Python 混装。上游 checkout 不修改；UE 插件副本中的接收缓冲区 / UTF-8 修复保存在 scripts/unreal-plugin-fixes.patch。

| 入口 | 用途 |
| --- | --- |
| scripts/Start-ProjectTools.ps1 | 启动 / 复用当前项目 Blender 与 UE Editor |
| scripts/unreal-build.ps1 | 编译 UE Editor；默认最多两个并行动作 |
| scripts/unreal-open.ps1、unreal-status.ps1 | 当前工程启动与实际进程 / 端口 / 构建状态 |
| scripts/install-unreal-mcp.ps1、run-unreal-mcp.py | 安装锁定的 UE MCP Python 环境 / Codex STDIO 入口 |
| scripts/verify-unreal-mcp.py --global-config | 按正式 Codex 配置握手、读取真实关卡与 Actor 属性 |
| scripts/install-blender-mcp.ps1、start-blender-mcp.ps1 | Blender MCP 安装与项目隔离 profile 启动 |
| scripts/check-blender-mcp.py | 只读验证正式 Codex 配置的 Blender 状态与场景 |
| scripts/verify-blender-mcp.py | 创建新版本诊断场景、保存 .blend / 导出 FBX，会修改测试场景 |
| scripts/ue-import-prepared-assets.py | UE 内导入代表素材并生成逐项报告；普通 Python --preflight 仅检查来源 |
| scripts/ue-import-prepared-font.py | 核查官方中文字体来源并在 UE 内导入 FontFace / Runtime Font |
| scripts/Invoke-AssetGen.ps1 | UTF-8 环境下运行项目 asset-gen；调用付费服务前另行确认花费 |

完整证据与缺口见 [准备状态](../docs/preparation-status-2026-10-10.md)、[UE MCP 核查](../docs/ue5-mcp-evaluation-2026-10-10.md)、[Blender 连接](../docs/blender-connection-2026-10-10.md)、[UniMate 核查](../docs/unimate-evaluation.md)。历史 Unity 脚本保留，不由当前总启动器调用。
