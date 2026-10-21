# 猎弩专属射击身体候选接入记录 v001

2026-10-15。当前阶段：实际导入成功，专属身体运行尚未验证；正式单元验收仍为0。

## 事实

冻结来源 `import-XBW-primary-v001.json` SHA256 `79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f`。6真实身体源姿势，拆为18张512×512原生RGBA far/support/near，重用独立猎弩组件。导入工具 `ue-import-xbw-primary-v001.py --validate-only` 已逐项核验37个冻结路径/哈希引用、18张实际PNG透明度/尺寸、每帧Grip/Support/Emit共同仿射矩阵及前摇/出手/恢复半开区间。

UE实际导入日志：`UnrealGame/Saved/Bootstrap/xbw-primary-import-20261015-113250.log`，commandlet退出0。收据：`xbw-primary-v001-import-20261015-033308-558883.json`，success=true、actual_count=18、saved_count=18，目的地 `/Game/Production/FirstBatch/v017/XBWPrimary`。此前v016持弩待机来源未改。

## 推理与接入边界

身体姿势读取Actor已经接纳的WeaponActionsState，每个实际前摇/出手/恢复区间各取2帧；加速后仍使用实际阶段边界，不能按AnimationTime或固定0.68秒播放。仅地面XBW Primary可选用；其他武器、装填、空中动作或过期Action不能借用此姿态。画序far→独立武器→support→near，统一根[256,472]，左右只镜像一次。图像与HUD均不发伤害、不消耗或补给弹药。

新 `DungeonXBWBodyPoseTests.cpp` 1组先以返回false桩建立实际RED，再实现阶段采样；Source/DLL/实际报告另行记录。导入成功不等于运行测试通过。

## 风险与未完成

静态弩组件没有弦释放机构动画；Source Emit是图像坐标，不可直接换成CombatHeight。出箭/命中特效仍有脚部偏低问题，Actor枪口契约另文记录。新身体还没有四种护甲表面；根坐标继承旧配置，未取得完整脚锁证明。四姿势装填清单9a0f99另存，尚未实际导入/运行，不把它并入本18张收据。
