# 首个战斗房间：二维占位素材 v1

2026-10-12，使用已下载的 **Kenney Mini Dungeon 2.0 / CC0** 原始 FBX，在独立 Blender 5.2.2 LTS 后台进程中转绘。无付费 API 调用，费用为 0。实时 Blender 场景未改动。许可原文见 `LICENSE-Kenney-MiniDungeon.txt`，输入与输出 SHA256 见 `source-index.json`。

这些 PNG 是二维运行资产，原始建模画风仍为低模卡通，供首版操作与战斗验证。它们不代表最终画风已获验收。

## 使用约定

角色画布统一 **256×256 RGBA**，朝右；朝左可在运行时水平翻转。每帧地面原点固定为 **(128, 220)**（左上角为像素坐标原点）。人物本体约占 140 px 高，建议以 200 px 方形画布显示，再根据游戏可读性调整。

| 动作 | 每角色帧数 | fps | 循环 | 原始动作 |
|---|---:|---:|---|---|
| idle | 8 | 8 | 是 | idle |
| walk | 8 | 12 | 是 | walk |
| attack | 6 | 15 | 否 | attack-melee-right |
| hurt | 2 | 10 | 否 | idle + 9°/5°临时后仰；原包无 hurt |
| death | 8 | 12 | 否，保持末帧 | die |

路径示例：`sprites/human/attack/human_attack_003.png`、`sprites/orc/death/orc_death_007.png`。动画由 `manifest.json` 规定顺序，不依赖文件枚举顺序。攻击动作只有手臂挥击，未在手上绑定武器；运行时攻击弧与武器绘制可单独实现。hurt 需配合运行时闪色、位移等受击反馈。

另含 `items/` 下剑、金币、药水、盾牌、宝箱五个独立 256×256 图标，居中原点 (128,128)。物件分别自动适配画布，不表示它们的真实比例一致。

## 检查与留存

- 64 张角色帧全部通过 256×256、RGBA、非空 alpha、包含透明区域检查，见 `quality-report.json`。
- 已检查 10 行动作联系表：角色直立、朝右，行走、攻击与倒地姿态可区分；统一原点保留，死亡动画自然倒地。
- 五个道具图标均已归档后视觉检查，轮廓清晰且未被裁切。
- 原始帧、展示联系表与状态索引分别保存在 `F:/Ourgame/过程图稿与视频/2026-10-12_首房间二维角色动作检查_v002` 和 `2026-10-12_首房间二维道具图标_v003`。初始单帧预览另存 v001。
- 这些检查针对素材结构与外观，不代表游戏动作时序、命中或实际运行已通过。

## 重现

从项目根目录以独立后台进程运行，不连接实时 MCP：

```powershell
& 'E:/SteamLibrary/steamapps/common/Blender/blender.exe' --background --factory-startup --python tools/scripts/render-prototype-sprites.py
& 'E:/SteamLibrary/steamapps/common/Blender/blender.exe' --background --factory-startup --python tools/scripts/render-prototype-sprites.py -- --items
```

重新制作前先保留上一版原件；新的审阅批次必须使用新的归档版本。脚本 `--inspect` 导出源骨骼/动作/材质信息，`--preview` 仅转绘两张 idle 预览，`--index` 重建输入输出哈希索引。
