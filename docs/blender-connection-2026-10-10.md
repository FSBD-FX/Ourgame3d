# Blender MCP 连接验证（2026-10-10）

## 事实

已验证真实 Blender GUI 进程、STDIO MCP 握手与工具调用、场景读取和修改、`.blend` 保存、FBX 导出。`tools/mcp-for-blender` Git checkout 保持原样。主代理已将 Blender 与 Unreal MCP 合并到 Codex 全局配置；本子任务没有自行改写全局配置，没有调用付费生成服务或下载模型权重。当前引擎方向是 UE5，之前的 Unity 交接安排仅作为历史记录。

| 项目 | 实际值 |
| --- | --- |
| Blender | 5.2.2 LTS，build hash `d13f752e3b9c`，Windows Release，build date 2026-09-15 |
| Blender EXE | `E:\SteamLibrary\steamapps\common\Blender\blender.exe` |
| Blender PID | `71412`（2026-10-10 09:26 验证时；重启后会变化） |
| socket | 仅 `127.0.0.1:9876`，由上述 Blender PID 监听 |
| Python | Codex 随附解释器创建的项目 `.venv`，3.12.14 |
| MCP distribution | `mcp-for-blender==2.1.3`，官方 PyPI wheel |
| MCP SDK | `mcp==1.30.0`；协议 initialize 的 serverInfo.version 取 SDK 版本，不能据此误写 distribution 版本 |
| Blender addon | 1.8，protocol 13，MCP `get_addon_status` 回报 `up_to_date=true` |
| 源码来源 | `https://github.com/ahujasid/mcp-for-blender`，commit `60d2a31b4632a7bc178f3dd636f7e68dfb5c8ae4`，工作区保持干净 |
| 用户配置 | 项目内隔离 profile：`tools/runtime/blender-mcp/blender-profile` |
| 遥测 | MCP 环境 `DISABLE_TELEMETRY=true` / `BLENDER_MCP_DISABLE_TELEMETRY=true`；addon 偏好 `telemetry_consent=false`，已通过握手读取 |
| 更新检查 | Blender 启动时 `BLENDERMCP_NO_UPDATE_CHECK=1` |
| 可选外部服务 | Poly Haven / Hyper3D / Hunyuan3D / Sketchfab / Tripo / Poly Pizza 均关闭 |

## 发行包与依赖

源码 checkout 的 `telemetry.py` 引用被 `.gitignore` 排除的 `config.py`。官方 PyPI 2.1.3 wheel **包含该模块**，因此采用发行包解决，不添加源码补丁或遥测配置占位文件。

- wheel：`tools/runtime/blender-mcp/packages/mcp_for_blender-2.1.3-py3-none-any.whl`
- wheel SHA256：`ca4bd001b317019ff888820317c10e8c533f9a31532f980310f82af30c450b20`
- PyPI 原始元数据：`tools/runtime/blender-mcp/packages/pypi-2.1.3.json`
- Windows/Python 3.12 已验证依赖锁：`tools/runtime/blender-mcp/requirements.lock`（31 个包）
- `uv pip check` 已通过：31 个包兼容；实际读取 `get_telemetry().config.enabled` 为 false。
- 安装在 `tools/runtime/blender-mcp/.venv`；没有向系统 Python 安装这些包。
- 安装脚本先校验上述 wheel 哈希，再同步锁定依赖并安装存档 wheel；不会覆盖现有异常/不完整 `.venv`。
- wheel 自带 addon 与 checkout addon 的差异只有 LF / CRLF；`git diff --no-index --ignore-space-at-eol` 返回 0。已安装 addon 与 wheel 自带 addon 字节相同，SHA256 `eb0facf69781a30e69792532087d8d41c6a14fcd323353250abe7988ee297fa5`。

## 复现命令

PowerShell：

```powershell
& 'E:\codex_game\tools\scripts\install-blender-mcp.ps1'
& 'E:\codex_game\tools\scripts\start-blender-mcp.ps1'
& 'E:\codex_game\tools\runtime\blender-mcp\.venv\Scripts\python.exe' 'E:\codex_game\tools\scripts\verify-blender-mcp.py'
```

`start-blender-mcp.ps1` 将 addon 安装到项目 profile，使用 `Start-Process -WindowStyle Hidden` 启动真实 GUI Blender（没有 `-b`）。上游 addon 明确拒绝 background 模式，因为命令需要 Blender GUI 主循环处理。引导脚本启用 addon、关闭外部服务与内容遥测，并只在项目 profile 保存偏好。重复启动检测到本项目 PID 已监听会直接返回；其他进程占用 9876 则报错并保留该进程。

安装和启动脚本设置的是被调用 PowerShell/子进程环境，未写入 Windows 用户或系统环境变量。默认 `--factory-startup` 保证诊断从干净场景开始；正式制作源文件应另存到 `source-assets`，不可把未保存场景视为交付。

脚本文件：

- `tools/scripts/install-blender-mcp.ps1`
- `tools/scripts/start-blender-mcp.ps1`
- `tools/scripts/blender-bootstrap.py`
- `tools/scripts/verify-blender-mcp.py`

## 验证结果与交接文件

验证通过完整路径 `Python MCP client → STDIO server → 127.0.0.1:9876 → Blender addon`，未用直接 socket 操作冒充 MCP 成功。

1. initialize 返回服务 `MCP for Blender`；list_tools 返回 36 个工具。
2. `get_addon_status` 返回 addon 1.8 / protocol 13 / Blender 5.2.2 LTS / up_to_date=true / telemetry_consent=false / premium_generators=[]。
3. `get_scene_info` 读取初始场景中的 Cube / Camera / Light。
4. `execute_blender_code` 在 safe mode 下创建诊断网格并保存 `.blend`。
5. `get_object_info` 读取 `MCP_TransferProbe_20261010092600`：1×1×2 m，已应用缩放，8 顶点 / 12 边 / 6 面；底面位于 z=0，材质 `MCP_Probe_Slate`。
6. `export_scene` 仅导出上述对象到 FBX，文件 15,244 字节，二进制头 `Kaydara FBX Binary` 校验通过。

交接给 UE5 的文件：

- FBX：`E:\codex_game\source-assets\blender-mcp-smoke\2026-10-10_092600\connectivity-probe.fbx`
- Blender 源：`E:\codex_game\source-assets\blender-mcp-smoke\2026-10-10_092600\connectivity-probe.blend`
- 详细 MCP 调用结果：`E:\codex_game\source-assets\blender-mcp-smoke\2026-10-10_092600\verification.json`
- 该次 MCP stderr：上述目录下 `mcp-server.stderr.log`
- FBX SHA256：`919e82eb06fa82c85c9d41e13c91555a8f4fa725dad0ebb2810ce4dba301dd6c`
- 最新结果索引：`tools/runtime/blender-mcp/logs/latest-verification.json`
- GUI 启动状态：`tools/runtime/blender-mcp/logs/blender-startup-status.json`
- GUI 日志：`tools/runtime/blender-mcp/logs/blender-20261010-092542.stdout.log` / `.stderr.log`（stderr 为空）。

每次验证以时间命名新目录保留结果，不覆盖之前的 `.blend` / FBX。本次网格只是本地传输诊断几何体，既不是最终美术资产，也不是用户已验收的效果图。没有向用户展示视觉媒体。

## Codex 已合并的配置

主代理已合并到 `C:\Users\22499\.codex\config.toml`。改动前备份为 `C:\Users\22499\.codex\backups\config.pre-unity-blender-20261010-092130-530.toml`。以下是读取正式配置得到的 Blender 服务块：

```toml
[mcp_servers.blender-mcp]
command = 'E:\codex_game\tools\runtime\blender-mcp\.venv\Scripts\mcp-for-blender.exe'
args = ['--host', '127.0.0.1', '--port', '9876']

[mcp_servers.blender-mcp.env]
BLENDER_HOST = '127.0.0.1'
BLENDER_PORT = '9876'
DISABLE_TELEMETRY = 'true'
BLENDER_MCP_DISABLE_TELEMETRY = 'true'
BLENDERMCP_NO_UPDATE_CHECK = '1'
BLENDER_MCP_SAFE_MODE = '1'
BLENDERMCP_ADDONS_DIR = 'E:\codex_game\tools\runtime\blender-mcp\blender-profile\scripts\addons'
```

STDIO MCP server 由 Codex 启动，不应再单独常驻另一个 STDIO 实例。诊断客户端已退出，Blender GUI 在验证结束时保持运行。全局配置已写入，两套服务均显式设置 startup 30 秒 / tool 180 秒。新增工具随后已在当前会话自动加载，主代理通过原生 get_addon_status / get_scene_info 读取到 Blender5.2.2、telemetry_consent=false 与含尺寸探针的4对象场景；不需要用户为本次验证重启。证据为 `evidence/preparation/native-mcp-check-2026-10-10.json`。

只读正式配置检查入口为 `tools/scripts/check-blender-mcp.py`；09:56 结果保存到 `tools/runtime/blender-mcp/logs/configured-check-20261010-095636/verification.json`。完整读写 / FBX 导出证据仍为上方09:26记录。

## 推理与边界

实际的建模、读取与 FBX 导出成功证明本机 Blender 5.2.2 能执行该 addon 的已测基础流程，不能推断所有生成服务、所有 Blender API 或骨骼动画兼容性都已通过。UE5 导入、坐标方向、材质与游戏运行由 UE5 工程侧单独验收。测试网格尺寸和 binary header 是结构验证，不代替 UE5 运行画面；早期 Unity 验证不作为当前引擎交付依据。

socket 无认证；保持 127.0.0.1 可以避免将其暴露到局域网。`BLENDER_MCP_SAFE_MODE=1` 只限制 MCP 代码执行通路，不是进程沙箱，也不保护直接原始 socket 命令。项目 profile 只在上述启动脚本启动的 Blender 中生效，用户从 Steam/普通快捷方式另开 Blender 不会自动使用它。

## 官方依据

- [官方 README](https://github.com/ahujasid/mcp-for-blender)：安装、STDIO → addon socket 架构、Codex 配置、addon 启动与 safe mode 边界。
- [PyPI 2.1.3](https://pypi.org/project/mcp-for-blender/2.1.3/) / [PyPI JSON](https://pypi.org/pypi/mcp-for-blender/2.1.3/json)：发行包版本、下载地址与哈希。
- [固定提交 addon](https://github.com/ahujasid/mcp-for-blender/blob/60d2a31b4632a7bc178f3dd636f7e68dfb5c8ae4/addon.py)：GUI 主循环要求、loopback 默认、遥测偏好与更新检查开关。
- 本机 `blender.exe --help`：`BLENDER_USER_RESOURCES` / `BLENDER_USER_CONFIG` / `BLENDER_USER_SCRIPTS` / `BLENDER_USER_EXTENSIONS` 的隔离配置含义。
