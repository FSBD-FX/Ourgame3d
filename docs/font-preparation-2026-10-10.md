# 中文字体准备记录 — 2026-10-10

事实：已从 [Noto 官方 CJK 仓库](https://github.com/notofonts/noto-cjk) 下载一个未经改动的 `NotoSansCJKsc-Regular.otf`，固定提交 `f8d157532fbfaeda587e826d4cd5b21a49186f7c`，字体内嵌版本 2.004。原文件 16,437,364 字节，完整上游 SIL OFL 1.1 与字体内嵌作者版权声明同时保存。免费下载，无账号、无付费调用、无系统字体安装。[原文件](https://github.com/notofonts/noto-cjk/blob/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf)、[上游许可](https://github.com/notofonts/noto-cjk/blob/f8d157532fbfaeda587e826d4cd5b21a49186f7c/Sans/LICENSE)。

本地目录：`E:\codex_game\source-assets\third-party\fonts\noto-sans-cjk-sc\2026-10-10-v1`。`source-manifest.json` 记录固定 URL、下载时间、每个文件的 SHA256、字体结构和抽样字符覆盖检查。字体 SHA256 为 `2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b`。

推理：UE 默认拉丁字体不能作为中文 UI 完整覆盖的依据；准备一个完整简体中文 Regular 足够开始 UI 原型。[UE5.5 官方支持 TTF 和 OTF 导入](https://dev.epicgames.com/documentation/en-us/unreal-engine/importing-fonts-in-unreal-engine?application_version=5.5)。原文件结构检查确认 OTF/CFF、65,535 个字形和 44,810 个 Unicode 映射；探针中的常用中文菜单、战斗和背包文字、数字与标点均可在 cmap 中找到非零字形。

导入脚本：`E:\codex_game\tools\scripts\ue-import-prepared-font.py`。普通 Python `--preflight` 已通过，只读源文件；实际导入由工程负责人在现有 UE5.5 Editor 中串行执行。目标为 `/Game/ThirdParty/Fonts/NotoSansCJKsc/FF_NotoSansCJKsc_Regular`（FontFace）与 `F_NotoSansCJKsc_Regular`（运行时 Font）。脚本依据 [FontFileImportFactory](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FontFileImportFactory?application_version=5.5)、[Font](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/Font?application_version=5.5) 和 [StructBase.import_text](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/StructBase?application_version=5.5)，复合字体序列化字段同时对照本机 UE5.5 `CompositeFont.h`。

实际导入：2026-10-10 02:10:16 UTC，工程负责人在同一图形 Editor 中执行脚本；`UnrealGame/Saved/Bootstrap/font-import-report.json` 记录 UE `5.5.4-40574608+++UE5+Release-5.5`、`success=true`。`FF_NotoSansCJKsc_Regular` 的真实类型为 `FontFace`；`F_NotoSansCJKsc_Regular` 的真实类型为 `Font`、缓存类型 `RUNTIME`，导出复合字体数据确认 `Regular` 正确引用该 FontFace。

当前状态：原始字体、许可、来源、校验和 UE 运行时字体导入已就绪。报告明确 `rendering_tested=false`；尚未完成 UMG 中文文本实际渲染、国际化文化包、字号/换行调整或打包显示验证。不得把源文件覆盖或引擎资产导入写成游戏 UI 验收通过。

风险与下一步：OFL 允许嵌入并随软件分发原字体，发布时携带版权声明与完整许可，不能单独售卖字体。中文字体约 15.68 MiB，运行时字体加载和字形缓存需要后续测量；本次保持原文件完整，避免为了包体提前裁剪而误删未来文本。正式菜单接入时用实际 UI 字符串逐项检查，并测试打包版本中的中文显示。
