# Scene v002：8原帧独立实看

2026-10-15，ranged_review。root确认F/E v027已保全729文件/2,666,989,428字节、两遍SHA零差后，本agent对下表8个distinct原件逐张调用view_image、原尺寸实看。未重复root的49（墙）/243（记忆）；root2+独立8为10unique，不称本agent独立看过10张。未改Source、archive index或原件，未UE/UBT。

F原件：`F:/Ourgame/过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v002/原件`。来源v035，仍为灰几何墙/碑，道具手绘稿后续才合入；本文不作美术终验。

独立读runtime-report：profile=`scene_exploration_normal_inputs`，Required13/Checks13，全部true、passed=true、failure为空；717电影帧另有prewarm。源快照proof2540f499.../State3c619c...与捕获DLL `7aacdae04df864af46a1e3cbcdd746702a7d42fcc9ab5b466dec478f782c17c6`对应。该证明仅sim0禁唯一Knight自主起手，真实追踪仍有效；后续调查、移动、Sword、E/Esc/Enter均正常输入。

选择遵循现有mapping：真实label观察对应最近native capture完成时刻，不声称GPU精确同步。mapping漏掉的exit_cancelled仅在本外部doc补录为688，不修改原mapping或archive。

| 原帧 | 对应label | trace/capture wall秒 | 实看观察 |
| --- | --- | --- | --- |
| 154 | before_survey | 5.905116 / 5.892671 | 玩家已到墙后碑位；灰碑和一部分“调查碎碑”字被玩家头身遮挡。顶部仍留“Enter开始”初始文案。 |
| 166 | after_survey | 6.305106 / 6.295084 | 顶部实际变为碑文“旧城守卫仍守着东门，碎墙西侧还有旧路”；HP100/金币00。贴身碑体/标签遮挡仍在。 |
| 509 | real_sword_clear | 18.130643 / 18.118749 | HUD房01/敌0、清房横幅与东侧出口指引可读，石骑倒下；金币/药水/斧的旧QA几何和重叠标签仍真实可见。 |
| 599 | old_exit_rejected | 21.134237 / 21.122531 | 玩家在旧665附近，仍房01/敌0，未出现确认层或换房；实际出口在更右方。画面同时出现“附近没有装备”反馈。 |
| 676 | exit_confirmation | 23.705807 / 23.693960 | 正确出现“前往下一个房间？”浮层，离开后无法返回/遗留物不带走，以及Enter离开、Esc继续探索清楚可读；仍房01。 |
| 688 | exit_cancelled | 24.105791 / 24.093469 | 浮层关闭、玩家仍在同一出口位置/房01；清房横幅回到画面。但顶部仍写“Enter离开，Esc继续探索”。 |
| 700 | before_fresh_exit_confirm | 24.505796 / 24.493908 | 重新E后确认浮层再次出现，按钮与风险文案可读；旧房仍在，尚未旅行。 |
| 716 | new_room_hud_reset | 25.045447 / 25.033661 | 房02/敌1、进入第2房文案明确，玩家回左入口，HP100/金币00/同军剑保持；旧房清房层消失。未调查灰碑轮廓和“旧城碎碑”名称仍透雾可见。 |

跨房读数与视觉分开核：上述label的RunGuid始终`A04ECF5644C2529153486DB87216D6A0`；676/688/700为RoomInstance1，688实际Pending=false；716为RoomInstance2/Pending=false，HUD room1→2、reset serial2→3、Survey memory1→0且visibility0，新房SurveyCount0。Survey前后真实Count0→1，金币/HP/Focus及来源/实例没有调查收入。军剑实例1贯穿，Focus100、ammo0/CD0；这段录像没有STF支出或非零CD迁移，后者已有独立Actor组证据，不把它混进本片视觉结论。

具体P2及处理状态（不倒填v002）：

- 688取消后顶部“Enter离开”与实际Pending=false及Enter不旅行合同冲突；154运行开始后仍留“Enter开始”也有同类旧文案问题。root已交producer处理，当前仅有修复安排，本文未验新运行结果。
- 154/166贴身碑/标签被角色遮挡。root已将close提示上移的HUD修改落盘，但尚未构建/复录，本片仍保留原问题。
- 716新房memory=visibility=0时碑体/名称仍显示，泄露未揭示的对象。root已在HUD加入二者都0不画、已记忆按淡化显示的窄修，尚未构建/复录。本片仅证明数据reset，不能宣称未知对象已完全遮蔽。

旧QA coin/potion/axe几何没有被隐藏；Bound E尚未接旧prototype拾取分支，清房出现物件不等于正式可拾来源或D08奖励链完成。8静帧不证明全段脚锁、pose衔接/frame snapping、完整攻击动画或听感；墙/碑仍灰几何，不验手绘道具、全Scene美术、正式AI、D07路图/D08隐藏收入/D13。正式15单元仍0/15。

运行报告SHA：`b09a217635bdd631cb32969d7a8e201b724a0495764c32aaacd5f97c7748155a`；原mapping SHA：`4136deff7b2ad3d79599959c76d7215d6d5545b9783a56083c7f4cb072f69361`。

| 原帧 | SHA256 |
| --- | --- |
| 154 | `bdc11143fcb0ce08779a452d0ae9fe02e5783c54f914e027e71ebe133d4a82c8` |
| 166 | `46b2bbdfb317dced9c4dabae354fc4bc561efa64fb740dacab555c6ed136e09c` |
| 509 | `32e277120091199a539b89d9b060268ae05ee756ce60fc8381577d3532ca891b` |
| 599 | `c45823a455108db55adab8e1c450e47c901c112baf14b2aacbc3a4a24a6fa037` |
| 676 | `f4876bdc35793edfeb3b2a17638e3dacfe23741274ba63265602a42538b0a405` |
| 688 | `bbc943aaa7af83eb42c09cecb8ccf31c695de8036640ac56cd693f8c0139a1ce` |
| 700 | `cd7cc17f09af55813aff8e546fb485752bee27e6dde07d7d41b60ae5d2026b31` |
| 716 | `f7635122f106166899e15ebee99b9ea318ef17bd88206762563ae9f80ef95bfe` |
