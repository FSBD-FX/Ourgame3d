# 项目 Skills 索引

2026-10-10 当前引擎为 Unreal Engine 5。Skills 是工作流指引，编辑器插件 / API 是否就绪另以实际调用为准；本目录不安装全局 Skill。

| Skill | 来源 | 状态 |
| --- | --- | --- |
| [unreal-mcp-orchestrator](unreal-mcp-orchestrator/SKILL.md) | 本项目已验证的 UE5.5 / Blender 操作流程 | 当前工程入口、构建、MCP、素材与验收路径 |
| [asset-gen](asset-gen/SKILL.md) | F:\Documents\游戏\.agents\skills\asset-gen | 完整 8 文件复制 / SHA256 一致；隔离依赖及 FFmpeg 已准备，未配置密钥或付费生成 |
| [unity-mcp-orchestrator](unity-mcp-orchestrator/SKILL.md) | CoplayDev/unity-mcp 固定提交 30d22075093d1d35dfb0091c1c7550e9ad948577 | 完整 5 文件复制 / SHA256 一致；历史 Unity 工程参考，当前服务禁用 |

## 当前适配

- UE 工程为 F:\Ourgame\UnrealGame\CodexDungeon.uproject；运行资产为 UnrealGame/Content，C++ 为 Source，编辑器插件为 Plugins。Blender 源、生成输入和原包放 source-assets。asset-gen 的旧 Godot 路径不覆盖此约定。
- 2026-10-11已确定《失落城堡》一、二部参考的2.5D方向，见 [方向记录](../../docs/2.5d-direction-2026-10-11.md)。当前缺完整二维角色动作，3D素材可保留作占位 / 转绘源，不能视作二维美术已齐备。
- 当前可直接使用免费 CC0 素材建立原型。视觉生成按 asset-gen 执行，首次付费前确认具体费用；旧 Skill 价格不能当作当前报价。
- tools/runtime/asset-gen 已安装 requests / xai-sdk / google-genai / Pillow / numpy / imageio-ffmpeg / rembg / onnxruntime 等，64 包依赖检查与导入通过。FFmpeg 7.1 实测可启动；未声称已安装 ffprobe。
- 未下载 rembg 或 3D 生成模型权重，未验证实际抠图 / 生成 API；密钥、账号登录和付费模型不是当前首个免费原型的前置。
- 展示媒体先遵守主项目 AGENTS.md 归档规则。工具 schema、引擎对象与真实运行结果是执行依据。

其他本机 Skills 的早期盘点见 [资源清单](../../docs/resource-catalog-2026-10-10.md)，其中 Unity 方案属于切换前快照。
