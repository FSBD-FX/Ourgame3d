# 探索迷雾显示纯核

日期：2026-10-15，Asia/Shanghai；对应用户 EV-042 的更大房间、较小角色及随探索揭开的边缘迷雾。本任务只实现探索显示数据；房间尺寸、角色显示比例、相机及实际雾渲染由根任务接线。

## 事实、方案与边界

采用根任务固定的接口与视觉参数：64世界厘米栅格、620×280椭圆视域，归一化半径0.68内全亮，0.68至1之间 smoothstep 衰减，外侧为0。每次只接受房间内有限的真实观察点；顶点记忆取历史最大值，因此单调增加、相同点重复揭开无变化。任意查询点的已探索强度由所在格四顶点双线性插值，输出0–1。

栅格从 Bounds.Min 起步，末端不足64的格补 Bounds.Max 顶点。边界包含房间自身的 Min/Max；房外或 NaN/Inf 查询返回0，非法观察点不改记忆。无效、退化、跨度非有限或超过1,048,576顶点分配上限的 bounds 安全禁用记忆。此上限是防异常分配的实现边界，不是游戏地图尺寸方案。

`Reset(RoomId)` 清空该实例记忆并设置房间身份，包括同ID显式重置。它保留构造时 bounds；若房间尺寸改变，外层应创建相应新实例。本核没有 Actor、UObject、AI、伤害、碰撞、掉落或时钟状态，视觉迷雾不能作为战斗权限。没有 D13 序列化、磁盘IO或整批恢复，不能声称已完成持久探索存档。

## 文件与接口

- `UnrealGame/Source/CodexDungeon/DungeonExploration.h`
- `UnrealGame/Source/CodexDungeon/Tests/DungeonExplorationStandalone.cpp`
- `UnrealGame/Source/CodexDungeon/Tests/RunExploration.ps1`

```cpp
namespace DungeonExploration {
struct FPoint { double X=0, Y=0; };
struct FBounds { double MinX=0, MaxX=0, MinY=0, MaxY=0; };
// FExploration(FBounds, int RoomId)
// void Reset(int RoomId)
// void Reveal(FPoint Observer)
// double MemoryAt(FPoint) const
// static double VisibilityAt(FPoint, FPoint Observer)
// std::size_t ExploredVertexCount() const
// int RoomId() const
}
```

`ExploredVertexCount` 统计记忆大于0的顶点，不是面积或房间完成率；count维护为常数时间读取。一次 Reveal 遍历当前栅格，MemoryAt 以二分定位格后插值。外层应只按真实 player XY 揭开，不以相机中心、虚构路径或截图采样点提前探索。

## 验证过程

使用 TDD：先写21条关键行为断言和可编译空桩，真实编译成功后10条行为失败；再最小实现得到21条全过。没有把编译失败当作 RED。测试覆盖：

- 视域中心、内边界、横纵半衰减、外边界、椭圆斜向与平移/左右对称。
- 初始远处未知、移动揭开、回访记忆、软边强度单调、重复揭开幂等。
- 房间换ID重置及同ID显式重置。
- 四顶点插值、精确顶点、末端短格/最大边界、房外与非有限输入、退化 bounds。

插值期望为独立手算夹具：Observer=(0,20.8)，四角(0,256)/(64,256)/(0,320)/(64,320)的强度分别为0.5、0.47039586917282794、0、0，中点(32,288)应为0.24259896729320699；没有调用被测 VisibilityAt 来生成期望值。

测试整体翻译单元由 `DUNGEON_EXPLORATION_STANDALONE` 包围，脚本先真实预处理确认无宏时文件为空，再以 `/EHsc /utf-8 /std:c++17 /W4 /WX` 编译运行。产物和日志均按新时间戳目录保存，finally恢复原 INCLUDE/LIB。

```powershell
& 'F:\Ourgame\UnrealGame\Source\CodexDungeon\Tests\RunExploration.ps1' -Phase VERIFY
```

本次只运行该新独立套件，没有运行 UE、UBT 或项目其他模块套件；根任务并行负责真实游戏集成。21项纯核通过不是迷雾已经显示或可玩验收的证明。

## 原日志与指纹

RED：`C:/Users/22499/AppData/Local/Temp/OurgameExploration/20261015-023923-076-RED/standalone.log`，SHA256 `2face9a0a6181f7629fe4299afd08c6706c7532ed6f5d863cf543dbb43147bc5`。

```text
PHASE=RED; standalone C++17 visual exploration only; no UE/runtime or D13 IO acceptance.
DungeonExplorationStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonExplorationStandalone.cpp
COMPILE_EXIT=0
FAIL observer center fully visible
FAIL inner ellipse remains fully visible
FAIL horizontal and vertical midpoint fade is half
FAIL translated left direction shares same fade
FAIL start reveals local area while distant region stays unknown
FAIL moving reveals new area while retaining old area
FAIL returning does not clear distant explored memory
FAIL memory uses four-corner bilinear interpolation instead of nearest cell
FAIL exact grid vertices retain their own memory
FAIL short final grid cell includes max room boundary only
CHECKS=21 FAILURES=10
EXIT_CODE=1
```

GREEN：`C:/Users/22499/AppData/Local/Temp/OurgameExploration/20261015-024011-814-GREEN/standalone.log`，SHA256 `26fd2d13b9bc34577763e8e85008686b2e9b70cf7be94c55f702ff0ac54a3c4b`。

```text
PHASE=GREEN; standalone C++17 visual exploration only; no UE/runtime or D13 IO acceptance.
DungeonExplorationStandalone.cpp
NO_MACRO_TRANSLATION_UNIT_EMPTY=true
DungeonExplorationStandalone.cpp
COMPILE_EXIT=0
CHECKS=21 FAILURES=0
EXIT_CODE=0
```

| 源码 | SHA256 |
| --- | --- |
| `DungeonExploration.h` | `d3ab726c41169b3f7d81f9727332577f1fe2412c06787576588a2645b4ccfd50` |
| `Tests/DungeonExplorationStandalone.cpp` | `f612e4a81041c018055defe71f9b7df2f2809440443a8c8b1a0051dc8b4700bf` |
| `Tests/RunExploration.ps1` | `022b54608e745c3fac3401296835b37cd69e4753099a1eccc756c123dca1031e` |

本轮编辑仅以上三个新源码/测试文件与本报告；未改其他 agent 的 Actor/GameMode/HUD/Probe、战斗测试或文档，未调用任何生成/API。
