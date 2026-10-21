# Ourgame3d · 钟盔地牢

UE 5.5.4 / C++ 的 2.5D 横版动作地牢开发快照。单人优先，怪诞暗黑童话风格、小比例钟盔冒险者；后续扩展合作。当前仍是制作中的有限试玩，完整首批内容尚未验收。

## 恢复与启动

需要 Git、Python 3、Unreal Engine 5.5.4 和 Windows C++ 构建工具。先克隆，然后在工程根运行：

```powershell
git clone https://github.com/FSBD-FX/Ourgame3d.git
cd Ourgame3d
powershell -NoProfile -File .\tools\github\restore-and-build.ps1 -EngineRoot 'G:\UE_5.5'
```

入口先核验 **308 个源码文件、1495 个生产资源及工程描述文件**，按固定提交恢复 UnrealMCP 外部依赖和本地修补，再编译并使用当前开发试玩参数启动。`-VerifyOnly` 只做源码与资源校验；`-NoLaunch` 编译后不启动。

Enter 开始；WASD 移动；E 拾取/穿戴；J 三段普通攻击；K 军剑副攻；Space 跳跃；Shift 闪避；R 重开。

原来的 v148 试玩入口和编译清单保留为历史记录；该入口要求本机旧 DLL 与旧日志的精确哈希。GitHub 恢复应使用上面的新入口，重新构建本机二进制。

## 已保存的内容

- Unreal 工程源码、配置、地图与运行资源。
- 制作源图、分层、原音频、参数、生成账本及尚未导入的 AirJ request264 候选。
- 武器/防具/附魔/道具/敌人/关卡等设计文档及需求台账。
- 构建、导入、核验脚本；第三方素材原件和实际许可说明。
- 当前编译输入清单、来源记录及恢复依赖的固定版本和文件 SHA256。

| 内容 | 当前状态 | 仍需完成 |
| --- | --- | --- |
| 钟盔角色、军剑与轻甲 | 已有动作分层和原生运行记录 | 全状态与搭配适配、动作衔接和最终视听验收 |
| 军剑 K | 八姿态、前踏及左右边界已有记录 | 连续动作与听感验收 |
| AirJ 空中斩 | request264 六姿态源图与 QC 已保存 | AJ2 留白、尺度/握柄校准及接入 |
| 敌人 | 石像系与斧守卫等已有试样 | 首批完整敌人、Boss和全部状态 |

工作工程迁移后的历史原生测试记录为 **203 成功、0 警告、0 失败**。本备份保持当前源码与资源字节；源码恢复校验与重新运行测试是不同步骤，完整游戏内容仍未完成。

## 备份范围与来源

缓存、预编译 EXE/DLL、工具安装环境、过程录像、大型历史重复快照及凭据不进入 Git。完整历史和故障证据继续保存在本地 `G:/OurGameArchive`，本仓库用于恢复当前开发内容。

UnrealMCP 来源于 [chongdashu/unreal-mcp](https://github.com/chongdashu/unreal-mcp)，固定提交 `4e5f00da50733190481311e254d16d137a84ef33`。本仓库保留来源说明、项目修补和精确文件 pin；插件本体在恢复时下载。其他素材许可见 [第三方说明](docs/github/THIRD_PARTY_NOTICES.md)。项目本体未另行添加开源许可。

[原工作页](docs/github/local-development-status-2026-10-21.md)保留制作边界；其中本机盘符和历史归档链接用于来源追溯，不能在 GitHub 网页直接打开。
