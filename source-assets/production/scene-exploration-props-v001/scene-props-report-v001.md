# 侧路苔墙与旧城碑候选：源资产交付 v001

日期：2026-10-15，Asia/Shanghai。仅新增两件场景视觉候选，不代表地图、碰撞或运行验收完成。

本次在已授权内置流程中执行两次请求：102 苔石低墙、103 旧城石碑。任务上限 2/2 已用完并停止追加；唯一总账为 `F:/Ourgame/source-assets/production/first-unit-animation-v003/generation-ledger.json`，交付时累计 103 请求、103 完成、无 pending；窗口 5 使用 7/24，剩余 17。外部 API 调用 0，内置费用未知。

冻结合同：`F:/Ourgame/source-assets/production/scene-exploration-props-v001/manifests/import-scene-exploration-props-v001.json`，SHA256 `a6eb21c81c1c2a29ac703454ee03318604e4cf5c96bde8070540e3f8c2a5c969`。两份均为实际 512×512 RGBA、alpha 0..255、四角透明；保留工具原件、1254×1254 原图、原尺寸抠图、固定画布统一缩放结果、prompt、参考及处理报告。没有 bbox-fit、单轴拉伸、局部重画或新增碰撞。

| 候选 | PNG | 真实可见 bbox | 源根点 | 唯一均匀缩放 | 世界地面锚点 |
| --- | --- | --- | --- | --- | --- |
| 苔石低墙 | `processed/moss-low-wall-512-v001.png` | [14,297,498,413] | [256,408] | 260/478 = 0.5439330543933054 | [-900,60]，原 AABB 近侧前沿中心 |
| 旧城石碑 | `processed/old-city-stele-512-v001.png` | [166,123,348,439] | [256,431] | 0.18 | [-920,300]，原调查锚点 |

低墙可见前沿手测 478 源像素对应 260 logical px；含轮廓与 AA 的完整 bbox 宽约 263.26 logical px。实际顶面深约 45、正面高约 70 源像素，手测不确定性约 ±5；缩放后约 24.48 深、38.08 高，**与原目标 38 深、24 高不一致**。保留这个偏差，不拉伸图像。采用主线程明确的组合路径：真实既有 XY AABB `[-1100,-700]×[60,160]` 使用已有石地纹理绘制基础地面，本 PNG 仅覆盖墙立面与顶面。隐藏后脚与 footprint 均为 inferred，`full_AABB_footprint_alignment_ready=false`；源图 465 列连续实体检查通过不能证明游戏碰撞对齐。根点 [256,408] 位于实际不透明像素；[256,410] 透明，未采用。

石碑实际可见尺寸约 32.76×56.88 logical px，有凹刻日/余烬纹样、短刻痕与苔色，未烘焙现代 UI 文字。后左基脚被遮挡，footprint 为 inferred；不改变交互范围或障碍体积。纹章仍是原创视觉候选，尚无用户正式图案批准。

F/E 同步留存目录均为 `2026-10-15_侧路苔墙与旧城碑美术候选_v001`，各有原件、展示副本与 index。两份交付 PNG 的 8 份归档副本、两次请求的 C 工具原件/规范 raw/F-E 共 12 路径均核对 SHA。源图和测量诊断图已在保全后逐张查看。

建议由主线程在新包 `/Game/Production/SceneExploration/v001` 导入 `T_scene_moss_low_wall_v001`、`T_scene_old_city_stele_v001`，直接使用冻结 PNG，不二次裁切或 refit。导入工具由另一 owner 制作。此任务未启动 UE/Blender、未改 C++/Actor/HUD、未运行导入；风格、尺度、底座、遮挡与调查可读性须由真实游戏复核。石蝠27与猎弩装填16冻结合同保持不变，完整15项内容目标仍未完成。
