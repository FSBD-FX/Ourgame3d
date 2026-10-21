# UE5 MCP 仓库核查与本地准备（2026-10-10）

## 判断

用户提供的 `VedantRGosavi/UE5-MCP` **只有设计文档，没有可安装的 MCP server 或 Unreal 插件**。不能把文档中的命令和功能表当作已实现能力。用户随后明确改用 Unreal Engine 5；因此经主代理确认，采用有实际 Python 服务和 C++ 编辑器插件的 `chongdashu/unreal-mcp` 作本机最小验证方案，并保留已经通过验证的 Blender MCP。

本文件区分源码准备、Python MCP 握手、UE 插件编译和真实编辑器连接。Python 服务握手成功不代表 UE 场景读取已经成功。

## 事实：用户提供的仓库

| 项目 | 核查结果 |
| --- | --- |
| 来源 | [VedantRGosavi/UE5-MCP](https://github.com/VedantRGosavi/UE5-MCP) |
| 本地浅克隆 | `E:\codex_game\tools\ue5-mcp` |
| 固定提交 | `c284cecd5fbba58778a07c26e417df15f112ad50` |
| 该提交时间 | 2025-06-01T23:35:50-04:00；消息 `Update README.md` |
| 实际文件 | 16 个 `.md`，合计 103,024 字节（不含 `.git`） |
| 缺失实现 | 没有 `.py`、`.cpp`、`.h`、`.uplugin`、`.uproject`、`pyproject.toml` 或 `requirements.txt` |
| 版本/发布 | 没有代码 manifest 或可核实的软件版本号；远端 `git ls-remote --tags` 成功且无输出；[Releases 页面](https://github.com/VedantRGosavi/UE5-MCP/releases)显示没有发行包 |
| 作者状态声明 | [README](https://github.com/VedantRGosavi/UE5-MCP/blob/c284cecd5fbba58778a07c26e417df15f112ad50/README.md)明确说明因时间限制没有继续推进，可使用文档 |
| 许可 | [LICENSE.md](https://github.com/VedantRGosavi/UE5-MCP/blob/c284cecd5fbba58778a07c26e417df15f112ad50/LICENSE.md)包含 MIT 条款，但版权年份和主体仍为占位符；不能声称作者/年份已完整填写 |

README 的安装示例仍使用 `your-repo` 占位地址，并要求安装仓库不存在的 `requirements.txt`。这不是当前可执行安装流程。

文档声称需要 UE5.1+、Blender3.x+、Python3.x；依赖列出 numpy / scipy / pillow / requests / openai / unrealcv，以及 UE Python Editor Script / UnrealCV / PCG 插件。**这些只是文档要求，没有对应实现或兼容性测试**；没有可核实的端口、真实 MCP 传输入口、C++ 工程要求或 Codex 启动命令。没有为这个文档仓库安装依赖。[依赖文档](https://github.com/VedantRGosavi/UE5-MCP/blob/c284cecd5fbba58778a07c26e417df15f112ad50/dependencies.md)

场景生成、Blueprint 自动生成、性能诊断、自动优化、Unity 集成和认证等说法均没有代码支撑。API 文档里的 `generate_terrain` / `generate_blueprint` 与 CLI 示例没有实现。安全文档同时声称具备认证，又把认证标准列为未来工作；缺少实现，无法验证。[API 文档](https://github.com/VedantRGosavi/UE5-MCP/blob/c284cecd5fbba58778a07c26e417df15f112ad50/api_reference.md)、[架构文档](https://github.com/VedantRGosavi/UE5-MCP/blob/c284cecd5fbba58778a07c26e417df15f112ad50/architecture.md)

## 推理：可运行替代的选择

| 仓库 | 已核实情况 | 本次选择 |
| --- | --- | --- |
| [chongdashu/unreal-mcp](https://github.com/chongdashu/unreal-mcp) | README 声明 UE5.5+，有 Python FastMCP 服务、C++ Editor 插件、Actor / Blueprint / UMG 工具；明确标为实验性 | 最小本机方案，源码已准备 |
| [flopperam/unreal-engine-mcp](https://github.com/flopperam/unreal-engine-mcp) | 有本地开源 Python 服务和 C++ 插件；README 明确区分基础本地版与独立托管商业服务 | 保留为后续备选，未安装；其托管版“50+工具”不能算作本地版能力 |

选择前者是为了验证本地场景读取和对象操作。它不是成熟的完整游戏生产系统，也不是厂商官方 Unreal 插件。当前 checkout 的最后提交为 2025-04-22，不能描述为持续维护到 2026 年。没有因为 GitHub 名称或星数就假定可用。[上游 README](https://github.com/chongdashu/unreal-mcp/blob/4e5f00da50733190481311e254d16d137a84ef33/README.md)、[另一候选的本地安装说明](https://github.com/flopperam/unreal-engine-mcp/blob/main/LOCAL_SETUP.md)

## 已准备的实际方案

| 项目 | 值 |
| --- | --- |
| 源码 | `E:\codex_game\tools\unreal-mcp`，稀疏浅克隆，仅准备 Python / Docs / C++ 插件相关内容 |
| 提交 | detached HEAD `4e5f00da50733190481311e254d16d137a84ef33` |
| 提交时间 | 2025-04-22T10:01:56+08:00 |
| Python 项目声明 | `unreal-mcp` 0.1.0；实际以源码模块启动，未安装该项目本身 |
| 插件声明 | UnrealMCP VersionName 1.0，Editor 模块 |
| 源码插件路径 | `E:\codex_game\tools\unreal-mcp\MCPGameProject\Plugins\UnrealMCP` |
| 目标工程 | `E:\codex_game\UnrealGame\CodexDungeon.uproject`；插件复制、C++ 编译和启动由 UE 工程 worker 完成 |
| 引擎要求 | README 为 UE5.5+；本机目标 UE5.5.4。插件需要本机 C++ 编译工具链；可用 C++ 工程承载构建，但游戏逻辑仍可使用 Blueprint |
| 插件依赖 | `EditorScriptingUtilities`；没有该桥接需要 UnrealCV / PCG / OpenAI API key 的代码证据 |
| 连接链 | Codex STDIO → Python MCP → `127.0.0.1:55557` TCP → C++ UnrealMCP Editor 插件 |
| Python | 项目 `.venv`，3.12.14 |
| 依赖 | 原始 `Python/uv.lock` 的固定版本；mcp 1.5.0 / fastmcp 0.4.1，共31包；`uv pip check` 已通过 |
| 日志 | `tools/runtime/unreal-mcp/logs`；未向源码 checkout 写日志 |

Python 与 C++ 均将 endpoint 写为 `127.0.0.1:55557`。插件绑定位置在 `Private/UnrealMCPBridge.cpp`，Python 配置在 `Python/unreal_mcp_server.py`；不存在通过环境变量换地址的上游实现。运行 wrapper 会拒绝变化后的 HEAD 或 endpoint，不依赖 Codex GUI 的 Git PATH。

### 许可缺口

上游 README 只有 “MIT” 声明；`git ls-tree -r --name-only HEAD` 的完整文件清单**没有独立 LICENSE / COPYING 文件**。部分 C++ 模板文件还保留 Epic 的版权注释。这里没有把“README 声明 MIT”写成“已保存完整 MIT 条款”，也没有自创/补写版权主体。本次继续本地验证，不打包分发该 Editor 插件；发行游戏前需要另行解决插件分发许可依据，并确认编辑器插件不进入游戏运行包。

### 安装与启动

```powershell
& 'E:\codex_game\tools\scripts\install-unreal-mcp.ps1'
& 'E:\codex_game\tools\runtime\unreal-mcp\.venv\Scripts\python.exe' 'E:\codex_game\tools\scripts\verify-unreal-mcp.py' --list-only
```

安装脚本验证提交与 Python 版本，再通过 `uv sync --frozen --no-install-project` 使用上游锁文件，环境位于 `tools/runtime/unreal-mcp/.venv`。没有安装模型、权重或付费服务。没有改写下载源码。

主代理已将下列服务写入 `C:\Users\22499\.codex\config.toml`，STDIO 由 Codex 拉起，不单独常驻。改动前备份：`C:\Users\22499\.codex\backups\config.pre-unity-blender-20261010-092130-530.toml`。

```toml
[mcp_servers.unreal-mcp]
command = 'E:\codex_game\tools\runtime\unreal-mcp\.venv\Scripts\python.exe'
args = ['E:\codex_game\tools\scripts\run-unreal-mcp.py']
startup_timeout_sec = 30
tool_timeout_sec = 180

[mcp_servers.unreal-mcp.env]
DISABLE_TELEMETRY = 'true'
MCP_DISABLE_TELEMETRY = 'true'
```

上游 Python 服务未见遥测或外部 API 上传实现；关闭变量用于统一进程环境，不声称源码读取了这些变量。服务需修改关卡和 Blueprint，插件没有身份认证；保持 loopback，不向局域网暴露。旧版依赖锁是可复现兼容基线，不等同于已经完成所有依赖的安全审计。

以下实链证据由独立官方 MCP client 读取正式全局配置并启动服务得到。新增原生工具随后已在当前 Codex 会话自动加载（UE30 / Blender36）。主代理通过原生 UE 工具创建中文名诊断Actor、变换、读回中文名、删除，前后19个Actor名称集合一致；中文UTF-8回环成功。证据为 `evidence/preparation/native-unreal-utf8-roundtrip-2026-10-10.json`。Blender原生状态 / 场景读取亦成功。本次无需用户重启；配置、独立客户端与原生调用分别核实。

### 当前验证证据

2026-10-10 09:40，真实 STDIO initialize / list_tools 通过，服务名 `UnrealMCP`，返回30个工具。`serverInfo.version=1.5.0`来自 MCP SDK，不是插件或项目版本。结果文件：

`E:\codex_game\tools\runtime\unreal-mcp\logs\2026-10-10_094034\verification.json`

该次运行显式记录 `engine_verified=false`：当时编辑器插件尚未启动，日志明确连接失败。不得据此宣称 UE 接入完成。UE 插件监听后，运行下列只读验证，必须读取非空 Actor 数据才记为真实引擎连接：

```powershell
& 'E:\codex_game\tools\runtime\unreal-mcp\.venv\Scripts\python.exe' 'E:\codex_game\tools\scripts\verify-unreal-mcp.py' --global-config
```

上游 `get_actors_in_level` 在空关卡与连接错误时都返回 `[]`，因此本地验证脚本不把空列表当成功。关卡需至少有一个 Actor。

09:44 已使用 `--global-config --list-only`，正式读取 `C:\Users\22499\.codex\config.toml` 的 `mcp_servers.unreal-mcp` command / args / env，initialize / 30工具枚举通过。记录：`tools/runtime/unreal-mcp/logs/2026-10-10_094429/verification.json`。此时仍为 `engine_verified=false`。正式实链模式还会读取一个 StaticMeshActor 的属性并要求 `status=success`。

09:45 **真实编辑器连接验证通过**：`--global-config` 按当前全局配置启动 STDIO，initialize / list_tools / get_actors_in_level / get_actor_properties 均成功。结果：`tools/runtime/unreal-mcp/logs/2026-10-10_094554/verification.json`，`engine_verified=true`。读取13个 Actor，包含7个准备对象和6个引擎内置/调试对象；`StaticMeshActor_0` 返回 `status=success`、location `[0,0,-25]`、scale `[15,15,0.5]`。该次 `127.0.0.1:55557` listener 属于真实图形 UnrealEditor PID65996。

09:48 **可逆写入验证通过**：通过同一全局配置和 MCP client，创建唯一 `MCP_Diagnostic_20261010_094857` → 读属性 → 修改位置/旋转/缩放 → 读回 → 删除 → 再列出全部 Actor。变换为 location `[120,230,340]`、rotation `[0,45,0]`、scale `[1.25,0.75,1.5]`，读回在容差内一致；`diagnostic_absent=true`、`original_actor_names_unchanged=true`，原有13个对象名称集合完全恢复。证据及全部30工具的实际 JSON schema：`tools/runtime/unreal-mcp/logs/2026-10-10_094856/verification.json`。没有修改准备对象或保存诊断对象到关卡；测试客户端已退出并释放连接给素材导入工作。

可逆验证入口（会临时创建并删除一个诊断 Actor，应确保没有其他 MCP 客户端并发操作）：

```powershell
& 'E:\codex_game\tools\runtime\unreal-mcp\.venv\Scripts\python.exe' 'E:\codex_game\tools\scripts\verify-unreal-mcp.py' --global-config --roundtrip
```

实际 schema 摘要：

| 工具 | 参数 |
| --- | --- |
| `get_actors_in_level` | `{}` |
| `spawn_actor` | 必填 `name:string`、`type:string`；可选 `location:number[]`、`rotation:number[]`，默认均 `[0,0,0]`；没有 scale 参数 |
| `get_actor_properties` | 必填 `name:string` |
| `set_actor_transform` | 必填 `name:string`；location / rotation / scale 为可省略 number[]，默认 null |
| `delete_actor` | 必填 `name:string` |

动态枚举的30工具中没有 `execute_python` 或任意代码执行工具，也没有 PIE Play/Stop 控制。源码中的 `focus_viewport` / `take_screenshot` 未注册为 MCP 工具，不能将 README 描述算成当前可调用功能。资产批量导入、PIE控制或证明录制需采用另外经验证的 Unreal 编辑器/命令行机制。

### 已发现的源码风险

`MCPServerRunnable.cpp` 原始接收代码在 8192 字节数组上写入 `Buffer[BytesRead]`，读满时存在越界；原始发送代码按 TCHAR 字符数计算 UTF-8 字节数，可能截断中文。UE 工程 worker 已在**工程插件副本**为两条接收路径预留 NUL 字节，并将两条发送路径改为 FTCHARToUTF8 字节长度。补丁：`tools/scripts/unreal-plugin-fixes.patch`；说明：`UnrealGame/Plugins/UnrealMCP/UPSTREAM.md`。上游 tools checkout 保留原样。TCP JSON 接收对分包的处理也有限，应先验证小型 Actor / Blueprint 调用，不能推断任意大型调用均可靠。

## 本机 Unreal 的只读检查范围

仅检查常见 Epic 安装根目录、以下注册表键与 Launcher 文件，没有扫描全盘或启动/安装引擎：

- `HKLM:\SOFTWARE\EpicGames\Unreal Engine`：记录 `G:\UE_5.0`、`G:\UE_5.1`、`G:\UE_5.3`、`G:\UE_5.4`、`G:\UE_5.5`。
- `HKLM:\SOFTWARE\WOW6432Node\EpicGames\Unreal Engine`：另有旧 Epic 安装记录。
- `HKCU:\SOFTWARE\Epic Games\Unreal Engine\Builds`：不存在。
- `C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat`：记录 UE5.0.3 / 5.1.1 / 5.3.2 / 5.5.4；5.5.4 路径 `G:\UE_5.5`。
- `C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests`：目录存在。
- 已检查 `C:\Program Files\Epic Games`、`C:\Program Files (x86)\Epic Games`、D/E/F/G 的 `Epic Games` 根目录、E/G 的 `UnrealEngine` 根目录；只有 x86 路径下 Epic Online Services。

这些安装记录可能过期，不能单凭注册表认定编辑器实际可启动。EXE、引擎补丁版本、Visual Studio 工具链、项目编译与真实启动由主代理/UE 工程 worker 另行验证。
