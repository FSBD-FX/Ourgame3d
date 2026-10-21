# 石像骑士追击终点停滞：实际运行修复 v001

2026-10-16。美术观察与此玩法修复分开绑定证据。

## 原问题与实际失败

奖励Stage0首次完整115运行035214在同一Run第二房正常J击杀过程中崩溃；进程exit3、没有完整index。原栈为KnightKernel Emit→Move→StepTo→Driver→GameMode PredictMotionBodies，申请20,341,674,119字节。原日志和v073保留。没有改变页面文件来掩盖循环。

原header的有界C++17复现由正常构造/靠近唤醒到Idle，再用合法Target220.00000000000009从X300追击。首段达到X262.00000000000011后，剩余Gap为半位置ULP，时间与坐标均不再变化，Move不断发出Movement。第17次测试专用非法Fraction2使原核原子回滚，避免再OOM；生产没有这种限次。这个合法反例证明机制，不冒称其小数就是原崩溃现场值。

原UE实际041814回归0/1、恰3错误、零警告/未运行；日志确认17次查询及相同bitpattern。构建041658exit0，源码/DLL/资源冻结v074。

## 最小生产改动

仅在成功Move后的既有停止条件增加 `(!AlignY && Travel==Gap)`，表示横向预定间隔已耗尽。Sweep校验仍先执行，墙/体阻挡、Y对齐后继续X、微小时步下合法与非法查询、已有快照schema均保留。

普通C++镜向、Y→X、微小Y、nextafter时间预算、非法Sweep原子拒绝和原77项核检查通过。新UE同组回归保留原3条失败断言并补充上述控制。旧112对应50个测试文件未改。

## 最新实际结果和边界

042449 Editor构建exit0。完整[042628报告](../../../UnrealGame/Saved/Automation/FirstRoom-20261016-042628/index.json)为116注册、113Success、3Fail、零warning/notRun。原112全部原名Success，新KnightProgress Success且反例只需1次Sweep；原来的第二房正常击杀返回，未再OOM。

三个失败仍在RunRewards Stage0：Coin测试的“死亡后必在60cm外”前提不成立；另外两组暴露尚未实现的奖励源ID/退休历史/恢复。未把夹具失败写成生产规则失败，也不把全116称为GREEN。奖励生产仍stubs，不宣称整局聚合/磁盘Continue完成。默认runner仍ExpectedTests112，当前新注册应显式116检查并如实报告3RED。

v075冻结：1,111文件74,611,989字节；生产header SHA0303c6be23e95e97103e262194b340df4477962cf762bdd46b74ce5a2e236b0e，新test SHAc0f93b72d421b9a7b01cf156998c04c698599bcaf0b2df7ef455dc641012d76d。美术录像仍绑定035039/v073的旧DLL，不能倒填成修复后录像。

这只关闭追击数值停滞这一缺陷。完整内容0/15、实际步态/甲层/声音/来源/续档等持续目标继续。
