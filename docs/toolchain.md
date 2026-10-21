# 工具链核查记录

> 历史记录：用户于 2026-10-10 明确改用 UE5。当前工程、实际 MCP 读写、C++ 工具链与素材检查见 [UE5 准备状态](preparation-status-2026-10-10.md)；下方 Unity 方案不再作为默认启动入口。

日期：2026-10-02（Asia/Shanghai）。用户已选 Unity + C#，配合 Blender；项目主目录为 `E:\codex_game`。

## 2026-10-10 复核补记

下方原始环境表保留 2026-10-02 的历史测量，本节记录最新事实，避免把历史记录当作当前环境。

- Blender 最新 `--version` 为 **5.2.2 LTS**，路径仍为 `E:\SteamLibrary\steamapps\common\Blender\blender.exe`；未启动 GUI 或 addon。
- Unity 四个已安装编辑器的 EXE 产品版本仍为 2021.3.45f1、2022.3.60f1、6000.0.42f1、6000.0.43f1；未验证启动、许可证或编译。`Game/` 工程仍不存在。
- 已定位 **uv / uvx 0.12.3**：`C:\Users\22499\AppData\Roaming\Python\Python314\Scripts\uv.exe` 和 `uvx.exe`，版本命令成功；不在当前 PATH。后续使用绝对路径，不需要仅为找不到命令而重复安装。
- 系统 Python 3.14.6、Codex 随附 Python 3.12.14；各工具依赖兼容性尚未验证。GPU 经 `nvidia-smi` 核实为 RTX 3060 Laptop、6144 MiB 显存；不作为模型已可推理的证据。
- 三个工具 checkout 的提交未变，工作区干净；Unity / Blender MCP 仍未安装连接，Codex 配置未修改。已完整复制 Unity MCP Skill 和 asset-gen 到项目 `.agents/skills`，不代表工具已接入。
- 已下载两个 Kenney CC0 原型包并核查包内许可，未导入 Unity。新的资源、包、Skill 与成本边界见 [2026-10-10 清单](resource-catalog-2026-10-10.md)。

## 本机环境事实（2026-10-02 快照）

| 工具 | 核查值 | 绝对路径 | 验证范围 |
| --- | --- | --- | --- |
| Blender | 5.2.0 LTS | `E:\SteamLibrary\steamapps\common\Blender\blender.exe` | `--version`；未启动编辑器或 addon |
| Unity | 6000.0.43f1 | `G:\UNITY\6000.0.43f1\Editor\Unity.exe` | 文件产品版本；未启动、验证许可证或编译 |
| Unity 其他安装 | 2021.3.45f1、2022.3.60f1、6000.0.42f1 | 对应 `G:\UNITY\<版本>\Editor\Unity.exe` | 文件产品版本 |
| Python / uv | 待定位与核实 | 待确定 | 当前 PATH 与用户 `.local\bin` 未找到 uv / uvx；其他位置未排除 |
| Codex MCP | 当前没有 Blender / Unity 服务 | 用户 Codex 配置 | 当前会话也没有对应工具；尚未配置连接 |

## Blender MCP

源码：`tools/mcp-for-blender`，版本 2.1.3，提交 `60d2a31b4632a7bc178f3dd636f7e68dfb5c8ae4`，MIT。这是制作桥接，不是游戏运行时。

连接关系：Codex → STDIO Python MCP server → `localhost:9876` socket → Blender addon。官方最低要求 Blender 3.0+、Python 3.10+，推荐 uv 管理的 Python 3.11。官方提供 `uvx mcp-for-blender install-addon`；执行安装及确认运行能力尚未完成。

源码实现可建模、修改材质、运行 Blender Python、导出 FBX / GLB。该实现尚未在本机完成实际导出或 Unity 导入验证。当前 checkout 中 `telemetry.py` 导入 `.config`，但该模块被 `.gitignore` 排除且源码副本缺失；直接运行源码的相关初始化可能失败。尚未执行，也未核查发行包是否补齐。

内容遥测默认 opt-in 关闭，基础使用统计仍默认启用。后续 MCP 进程应设置 `DISABLE_TELEMETRY=true`；Blender 进程可设置 `BLENDERMCP_NO_UPDATE_CHECK=1` 关闭联网更新检查。socket 无认证，保持本机 loopback；`BLENDER_MCP_SAFE_MODE=1` 只校验 MCP 代码执行通路，不保护所有原始 socket 命令，也不是进程沙箱。

依据：[官方 README](https://github.com/ahujasid/mcp-for-blender)、[遥测源码](https://github.com/ahujasid/mcp-for-blender/blob/60d2a31b4632a7bc178f3dd636f7e68dfb5c8ae4/src/blender_mcp/telemetry.py)、[addon](https://github.com/ahujasid/mcp-for-blender/blob/60d2a31b4632a7bc178f3dd636f7e68dfb5c8ae4/addon.py)。

## Unity MCP

源码：`tools/unity-mcp`，main 提交 `30d22075093d1d35dfb0091c1c7550e9ad948577`，Unity package 和 Python server 的 manifest 均声明 10.2.0，MIT。仓库默认 beta 副本曾在初次核查位置下载；新项目工具副本使用 main。

这是 Unity 编辑器桥接，不是游戏模板；官方支持 Unity 2021.3 LTS 至 6.x、Python 3.10+。实现具备场景 / GameObject / C# 编辑、Play 控制、Console、截图、测试与构建能力；尚未在本机验证。

推荐本地 HTTP：Codex → `http://127.0.0.1:8080/mcp` → Python server → `/hub/plugin` WebSocket → Unity C# plugin。Python 裸 CLI 默认 stdio，HTTP 要显式选择 `--transport http`。Unity 插件与 Python 服务需匹配并固定版本；GUI 配置时核实 uv / uvx 的绝对路径，避免仅依赖终端 PATH。这里只记录拟议连接，没有修改 Codex 配置。

源码默认启用遥测，与官网首页的默认无遥测表述冲突；按源码记录启用，并计划通过 `UNITY_MCP_DISABLE_TELEMETRY=true` 或 `DISABLE_TELEMETRY=true` 关闭。HTTP 模式这些变量必须设置在实际 Python server 进程，不能只放在 Codex 的 URL 配置块中。工具能修改脚本、删除资产和执行 C#，保持本机 loopback。

依据：[官方 README](https://github.com/CoplayDev/unity-mcp)、[包 manifest](https://github.com/CoplayDev/unity-mcp/blob/30d22075093d1d35dfb0091c1c7550e9ad948577/MCPForUnity/package.json)、[服务 manifest](https://github.com/CoplayDev/unity-mcp/blob/30d22075093d1d35dfb0091c1c7550e9ad948577/Server/pyproject.toml)、[传输说明](https://coplaydev.github.io/unity-mcp/architecture/transports)、[遥测说明](https://coplaydev.github.io/unity-mcp/architecture/telemetry)。

## 资产交接、成本与验收边界

建议先以 Blender 导出的 FBX 验证 Unity 导入、材质、骨骼及动画，再选具体角色和美术制作方案。Unity MCP 的 `import_model_file` 接受 FBX / OBJ / GLB / glTF，其中 GLB / glTF 需要额外 glTFast。工具存在不保证导出兼容性、模型适合游戏或运行性能。

两套开源桥接无需付费生成服务即可完成普通本地建模和编辑器操作。Tripo、Meshy、fal.ai、Hyper3D、腾讯云等生成服务属于可选项，费用与授权需另行确认；没有核查价格，也未调用任何付费生成。视觉资产执行 `$asset-gen`。

下一阶段验收：Unity 工程可打开与编译 → 两套 MCP 能读取各自场景 → 一个简单模型从 Blender 导出并在 Unity 正确显示 → 基于已明确玩法制作可玩片段并验证实际运行。源码保存、工具连通及游戏交付分别记录。
