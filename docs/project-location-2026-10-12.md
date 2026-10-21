# 项目主目录更新

日期：2026-10-12，Asia/Shanghai。用户最新指定主存储目录为 **`F:\Ourgame`**。后续工程、源资产、工具、需求记录和本项目展示归档在此维护。

当前入口：[项目总览](../README.md)、[持续需求台账](../项目需求台账.md)、[UE工程](../UnrealGame/CodexDungeon.uproject)。旧 `E:\codex_game` 保留为迁移前副本，另有新位置提示文件；后续不同时维护两份活动工程。

## 事实与验证

复制前F目标目录为空。以非破坏性复制保留现有UE工程、Unity历史准备工程、Git状态、源素材、工具和隔离依赖；未使用镜像删除，未删除源目录。复制得到 **44,240个源文件、5,245,787,676字节**；逐文件存在性与大小核对无差异，其中UE工程、源资产、脚本和项目Skills共 **1,725个文件、2,817,318,413字节**另作SHA256比较，无差异。这是目的地后续路径适配前的副本验证，不宣称全部Python运行库和Unity缓存逐一哈希。[复制核验](project-copy-verification-2026-10-12.json)

已修复当前活动入口：

- README、AGENTS、工具索引和UE项目Skill指向F；新增需求持续追加规则。
- Codex全局配置仅调整本项目Blender / Unreal两个MCP的路径，其他设置保留；修改前配置另存C盘backups。[配置改动记录](mcp-path-migration-2026-10-12.json)
- 复制的Windows console EXE可能嵌入旧E解释器。Blender改由F环境的Python调用项目 `run-blender-mcp.py`，启动器安装addon也走该入口；Unreal同样直接调用F Python。避免使用复制来的activate脚本或旧MCP EXE。asset-gen使用项目PowerShell包装器和F Python。
- 素材脚本读取历史来源清单时，将已知旧E根映射到实际当前工程根；原始来源manifest不改写，缺失期望SHA现在明确失败。14项来源实际哈希全部匹配，字体和许可预检通过；三脚本语法通过。[源路径验证](asset-path-verification-2026-10-12.json)
- 含旧绝对编译路径的两个Intermediate副本已保存到 `tools/runtime/migration-backups/2026-10-12`，避免后续构建复用旧路径；新Editor已自行生成新的资产注册缓存。未删除缓存副本。[缓存保存映射](intermediate-backup-2026-10-12.json)

**F目录实际启动与连接通过**：2026-10-12启动器打开F的 `.uproject`，图形Editor日志 `UnrealGame/Saved/Bootstrap/editor-20261012-192323.log` 确认初始化完成；Editor PID34216，Blender PID5268。Blender使用F独立profile，遥测同意为false。依正式全局配置启动独立官方客户端，Blender36工具场景读取成功，Unreal30工具真实场景读取成功。对应新证据：

- `tools/runtime/blender-mcp/logs/configured-check-20261012-192359/verification.json`
- `tools/runtime/unreal-mcp/logs/2026-10-12_192358/verification.json`

PID只是本次观测值，不是后续固定配置。当前继续使用已编译的同版本Editor / 插件DLL；本次没有重新执行C++构建、资产重导、PIE或游戏内容验收。复制来的旧 `last-build.json`、导入报告与PIE报告继续只证明旧E运行，不冒充F重测。

重复启动复用相同进程；三个活动PowerShell入口语法无错误，10份活动文档链接无缺失，UE项目Skill验证通过，Blender / Unreal / asset-gen环境分别31 / 31 / 64包依赖兼容检查通过。[最终路径与入口核验](project-location-verification-2026-10-12.json)

## 媒体与历史路径

仅将本项目UE测试的v001–v004四批媒体复制到 `F:\Ourgame\过程图稿与视频`，42个文件逐一SHA256相同。原件、展示副本、旧索引和旧哈希清单按字节保留，索引中的E路径仍描述当时来源。新副本映射另存 [媒体复制记录](media-copy-verification-2026-10-12.json)。其他Knight项目材料不在本次复制范围，旧归档全部原位保留。

G盘UE、E盘Steam版Blender、C盘Python / uv仍是软件安装路径，用户指定的F项目目录不要求搬迁这些软件。历史文档、来源manifest、备份、日志、第三方上游源码和素材内部路径不无差别替换。

## 后续注意事项

部分UE资产的导入元数据可能仍记录旧E源文件；正常运行使用已复制的 `/Game/...` 包。本次没有二进制替换 `.uasset`，也没有逐个规范化GUI Reimport来源。后续重导使用已适配的F脚本；若使用Editor的直接Reimport，应先用UE API确认 / 更新目标资产来源路径，避免读取保留的E副本。

新目录内后续修改C++时应实际构建并记录新退出码；新玩法仍须真实PIE / 运行包验证。2.5D玩法、二维角色动作及武器 / 装备 / 道具系统尚未实现。本次完成的是需求记录、存储切换和活动入口连通性，不是游戏系统交付。

E源副本目前只作保留，不会与F自动同步。F与E为不同盘符，未据此证明是不同物理磁盘或异地备份；尚无远端Git或云端备份。
