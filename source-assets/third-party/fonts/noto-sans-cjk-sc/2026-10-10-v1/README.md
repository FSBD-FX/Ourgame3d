# Noto Sans CJK SC Regular — 原始字体

准备日期：2026-10-10。只下载一个 Regular 字重，没有下载字体全集、转换、裁剪或修改字体。

| 文件 | 用途 | 大小 | 校验 |
| --- | --- | ---: | --- |
| `NotoSansCJKsc-Regular.otf` | 简体中文 UI 原型字体，内嵌版本 2.004 | 16,437,364 B | 见 `source-manifest.json` |
| `LICENSE` | 上游完整 SIL Open Font License 1.1 | 4,301 B | 见 `source-manifest.json` |
| `COPYRIGHT.txt` | 从原字体 name ID 0 提取的作者版权声明 | 原文保存 | 见 `source-manifest.json` |

官方仓库：[notofonts/noto-cjk](https://github.com/notofonts/noto-cjk)。固定提交：`f8d157532fbfaeda587e826d4cd5b21a49186f7c`。实际原始下载 URL、SHA256、结构检查均记于清单；不使用第三方镜像。

OFL 允许将原字体嵌入游戏并随软件分发；分发时应携带原版权声明和完整 OFL，不得单独售卖字体。字体没有改动，保留其原名称。本地准备不代表已完成游戏发布许可清单或所有目标平台测试。

源文件的 SFNT / cmap 检查通过：65,535 个字形、44,810 个 Unicode 映射，所选常见中文 UI 探针文字没有缺字。UE5.5.4 真实导入报告 `UnrealGame/Saved/Bootstrap/font-import-report.json` 记录 `success=true`：FontFace 与运行时 Composite Font 已创建，Regular 引用正确。`rendering_tested=false`；首次使用界面时还需验证字号、中文标点、换行与打包后显示。

引擎内执行 `tools/scripts/ue-import-prepared-font.py`；普通 Python 加 `--preflight` 只检查原始来源，不启动引擎或修改项目。
