# UniMate 动画工具核查

日期：2026-10-04（Asia/Shanghai）。项目仍采用 Unity + C#，配合 Blender。

## 事实

- [UniMate](https://github.com/Friedrich-M/UniMate) 是根据文本为不同骨骼结构生成动作的研究模型，支持动作补间、局部编辑与扩展；不是 Unity 插件或 MCP 编辑器桥接。
- 源码已浅克隆到 `E:\codex_game\tools\UniMate`，分支 `main`，提交 `2c5b384715aa63d8639b1ed7eb74bfe614570c7a`。只保存与核查源码，未安装依赖、下载权重 / 数据或运行生成。
- 仓库代码为 MIT；[官方预览权重模型卡](https://huggingface.co/Linzhan/UniMate/raw/main/README.md) 及 [权重 LICENSE](https://huggingface.co/Linzhan/UniMate/blob/main/LICENSE) 标注 **CC BY-NC 4.0**。模型权重不具有与代码相同的许可。数据仍受 Mixamo、各 Objaverse 对象、Truebones 等来源的各自许可约束。
- 当前推理入口使用训练配置、权重、归一化统计及数据集骨架条件，并不只需要一个 FBX 和文字。生成的 `.npy` 动作需经数据处理的动画阶段驱动骨骼网格，再导出 FBX / GLB；Unity 交接优先验证 FBX。

## 自制角色边界

仓库总览仍将新分布骨架的正式预处理流程标为 TODO。[数据处理文档](https://github.com/Friedrich-M/UniMate/blob/2c5b384715aa63d8639b1ed7eb74bfe614570c7a/data_process/README.md) 和源码已有自制资产导出、单角色预处理等底层入口，部分代码支持无动画动作的静止骨架条件；但当前 sampler 与 dataset loader 仍依赖参考动作 / motions 目录。

因此不能断言完全不支持自制骨架，也不能保证新角色仅凭 T-pose 就能完成端到端推理；模型卡仍要求新骨架至少有一个动画片段。总览、模型卡与底层代码存在表述差异，需在后续小样本实验中核实完整输入、骨骼映射及动画输出。

## 本机条件与成本

`nvidia-smi` 返回 RTX 3060 Laptop GPU、6144 MiB 显存、驱动 546.30。当前 PATH 的 Python 为 3.14，未发现 conda / uv / uvx；此范围以外的环境尚未排除。

[仓库依赖](https://github.com/Friedrich-M/UniMate/blob/2c5b384715aa63d8639b1ed7eb74bfe614570c7a/requirements.txt) 指定 Python 3.10、PyTorch 2.5.1 + CUDA 12.4、`bpy` 4.0。它们与现有环境不同，尤其不能将已安装的 Blender 5.2 直接视为 `bpy` 4.0 环境。仓库提供 Bash 包装脚本；Windows 部署需验证环境与入口。

本机的显存峰值、推理时长、驱动组合与导出兼容性均未实测；不能承诺 6 GB 显存足够或实时运行。部分数据处理阶段涉及可选 LLM / VLM 接口，费用需按实际后端核实。本轮没有付费调用。

## 判断与下一步

将 UniMate 保留为**离线动画研究候选**。适合评估多足、鸟类等特殊骨架的文本动作生成；正式生产使用前需先解决权重许可，并验证目标角色的完整处理链。商业用途应向权利方确认授权，不能按仓库 MIT 许可默认使用这些预览权重。

合理的小规模验证顺序是：选定许可明确的权重与一个现成骨架 → 独立环境推理少量动作 → Blender 驱动网格并导出 FBX → Unity 检查骨骼、比例、循环、脚底滑动和根运动。自制角色在这个流程通过后再适配。当前没有启动该实验，也未把模型加入游戏运行依赖。
