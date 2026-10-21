# 原局内存档：真实两个进程继续验证

事实：2026-10-16，UE5.5.4，`F:/Ourgame/UnrealGame/CodexDungeon.uproject`。生产共享几何判断实际由1Fail/4errors/0warnings到1GREEN，原生pristine入口3GREEN，再完整138GREEN，旧134测试名完整保留。v112的1587文件/3174当前与冻结端点SHA零差。探针准入后两次真实编译失败记录保留，修正宏分支花括号、不完整私有状态删除器及SpectatorPawn显式include；162916编译0，162940完整138/138，所有测试errors/warnings/notRun/inProcess为0，冻结v113。

第一次真实两个进程v001均正常退出，但原独立Python把Codec的`RunGuid={A,B,C,D}`误作UUID字符串，原session保持failed_preserved。新增v002核验器按本机Codec四个canonical uint32字段、native FGuid A/B/C/D顺序拼接身份；实际GUID与envelope吻合，6种缺字段/多字段/非canonical/零/溢出输入拒绝。旧session另做只读复核通过，没有覆盖其失败状态、原件或重新写凭据。此故障是核验器格式错误，不是游戏功能semantic RED。

随后使用全新目录、全新Profile做v002实跑，Source PID44460退出0后才启动Restore PID52000，后者退出0。两进程Source及DLL前后SHA相同，DLL为`494c396d26db1646a8c8617fadd3c3b6817401fc4aa46b17d51e320b10d6b6dd`，对应实际162916构建/v113。实际session：`UnrealGame/Saved/RunPristineProofs/20261016-163507-native-two-process-v002`。

Source在正常场景中真实Enter、官方Register空猎弩、真实E完成原装备deadline、真实T装填；在原Reload.Start+.65之后、End之前的实际GM/HUD完成边界保存。原生自定义枪口24/7/65保留。真实writer lease、Adapter.Commit generation1/parent0、磁盘bundle和marker、Load读回均完成。整个证明没有手动Game.Tick、设弹药、改deadline或重置新Run。

Restore的原生InitGame/Login/BeginPlay入口为`FirstRoom?DungeonContinuePristine`：无Pawn、无Run、seed/draw/serial0、输入封门；真实R按下释放仍保持该完整空状态。实际Load→PreparePristine→Install创建隐藏/tick与collision关闭的staged组，并进入AwaitExplicitContinue。安装、暂停至少.2秒后的整局Codec与Source原字节完全相同；原生Controller随后拥有恢复的玩家，输入neutral后的新Enter才恢复模拟。

原Reload的ActionId/InstanceId/Start/End、RunGuid/OwnerId、CombatSeed/NextCritDraw不变。原End仅追加一次库存0→1补弹及对应WA资源回执。暂停时不重播旧draw/insert，未来complete只请求一次；额外原生Tick窗口没有重复补弹或声音事件。音频证明为HUD请求/producer事实，未试听设备。

独立核验器还直接读取实际`slot-A.bundle.json`与commit，核generation/parent/Profile/build/versions/原SimulationTime位串、原Codec嵌入字节、bundle长度/SHA/CRC、marker完整性摘要及实际IO文件集合，未只相信两个passed字段。Source Codec30900字节，SHA`a8afb7d10f55262d4926edaa5ce4fc5f4784f2622543b56384308baed80a2db9`；bundle31738字节，SHA`2414395f6bfb74d16bd5f5282d7ea861458ae1ab14244c4270a5c1713a29db0b`；marker350字节，SHA`450746d34913a978fccedf549151079ffb6c3ba5895415df61ca40c199575ea9`。详细原件及独立receipt见该session。

推理：原局内数据已能在真正新进程恢复并沿原动作期限继续，之后可在稳定合同上实现玩家保存/继续入口与完整内容集成。共享几何判断仅接受精确原生GameplayDebugger渲染组件、正确所有权/root/唯一primitive及无BodySetup/有效rawBody/weld；实际PhysicsStateCreated=1不代表存在形状，真实foreign Box和debugger额外Box仍拒绝。

风险与边界：这仍是独立`BoundDevelopmentRunV1`/`BoundRunOnly-v1`局内存档证明，完整D13 Account/settings/journal owners尚未实现；没有玩家保存菜单、额外平台/版本迁移、设备试听或本次保存过程的画面录像验收。旧正常目标Capture、失败回滚、原测试条件保留。ArcB美术实录仍绑定旧v110，不能重标为v113。正式完整内容单元0/15，目标active。
