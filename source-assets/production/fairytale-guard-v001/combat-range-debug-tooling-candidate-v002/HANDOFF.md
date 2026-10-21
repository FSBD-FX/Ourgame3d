# Combat range debug native tooling v002（新候选）

原Hurt observer/source/checker/CRC/光学阈值全不改，仍精确绑定 `hurt-native-observer-candidate-v001/Hurt-native-observer-freeze-v001.json`（8100c1bd…37eb97）。Root需先完成新4Source编译、实际全187、fresh Source/Production1286 snapshot、Guard source-profile extension approval和NEW Hurt Root prereg；此候选不制造这些尚未提供的证据。没有新Actor或游戏状态写入。

小launcher复制原Hurt流程，candidate与checker路径明确指回原Hurt目录。仅新增两flags：每次 `-DungeonCombatRangeProof`；`RangeMode=debug1`另加 `-DungeonCombatRangeDebug`，default0绝不传debug。新topic/version保存原件；session原schema/PID/snapshot/Rootprereg/official candidate契约保持，只加range模式、flags、工具freeze和后验range结果字段。原官方checker先照常写入原receipt；额外readonly checker再使用原官方checker无写入重跑，结果必须逐字段等于原receipt，不调光学、HP、时序或quad门。日志checker仅stdout；launcher成功后保存新的range receipt和final index。所有失败原件保留。

Root三次顺序执行（同fresh snapshot，不同对应side的NEW Root prereg，每次新version）：

```powershell
& '<candidate>/tooling/capture-Hurt-combat-range-v002.ps1' -Version default_left_v001 -Snapshot '<freshactual>' -RootPrereg '<NEWleftprereg>' -ApproachSide -1 -RangeMode default0
& '<candidate>/tooling/capture-Hurt-combat-range-v002.ps1' -Version default_right_v001 -Snapshot '<freshactual>' -RootPrereg '<NEWrightprereg>' -ApproachSide 1 -RangeMode default0
& '<candidate>/tooling/capture-Hurt-combat-range-v002.ps1' -Version debug_left_v001 -Snapshot '<freshactual>' -RootPrereg '<NEWleftprereg>' -ApproachSide -1 -RangeMode debug1
```

以上默认只作原官方source-only预检；每个命令增加 `-ExecuteNative` 才启动实际新进程。debug1明确只允许左侧正对照。默认两侧及正对照都走同原Hurt路线／真实Guard出斧／真实Hero HP和原.4 Hurt，不能改或跳官方checker。

只读重核：项目Python `-B -X utf8 <candidate>/tooling/verify-combat-range-log-v001.py --archive '<actualnewarchive>' --snapshot '<freshactual>' --root-prereg '<matchingNEWprereg>' --expected-mode default0`（正对照改debug1）。不会写archive，也不会启动UE。它会按原规则解码原PNG作官方CRC/quad/固定光学测试，但不View或改像素；本候选作者仅跑静态测试，没有执行新native核验或解码。

日志合同：`CombatRangeProof frame=%llu sim=%.17g enabled=%d lines=%d`。原Hurt observations已有sim与guard_action。每个原observation必须有完全相等binary64 sim的日志，不用nearest/宽容差、不编造frame或DrawId。开局sim0可重复，重复sim的所有Draw日志enabled/lines必须一致，frame与sim不倒退；额外callback以真实日志行号和HUD proofFrame记录。default0全部日志enabled0/lines0。debug1全部enabled1，计数只能0/4/32；与原hit_attack同一真实Axe Windup和Active窗口分别至少一条合格日志，每条该窗口日志lines≥4。原官方Hurt PASS仍是先决条件。只验证Guard helper提交的范围线，不把其他FX／Knight／Bat普通Line统计混进来，计数不冒视觉形状或最终美术验收。

range receipt绑定原runtime-report/log/official receipt/freshmanifest/Rootprereg的真实SHA；session绑定全部稳定字段及canonical SHA，明确只排除launcher最后更新的status/range-pass/failure字段，因此不会对尚在finalize的index写一个必然过期的whole-file SHA。最终index仍由Root完整归档／E两SHA保全。

四Source只读快审已保存在root-four-source-static-review-v001.json：比actual v136 Source246，恰4文件变、其他242 Source字节不变；Full/Partial各两call名称+一注释，HUD新增flags/helper/reset/log与两call，Header仅getters/fields/helper声明，反向重建相等。矩形／椭圆geometry、color、HP、kernel/driver/GameMode/Fighter/Hurt actor不变，未见明显shadow/Canvas/count阻断。该结论是静态差异，不能代替新build/full187或三次native。默认范围是否视觉消失仍待Root保全后View。


v002仅修日志marker词边界与自身freeze路径。原v001 substring门会误把LogInit启动参数-DungeonCombatRangeProof当作畸形证明行；旧c3cb1bdf冻结完整保留。v002跳过嵌于参数/identifier中的同名后缀，只消费独立CombatRangeProof消息词；真实独立marker若字段格式错误仍拒绝。native/session/range receipt schema、官方checker、关联/HP/clock/Count/coverage规则全不变，无需重编译。新增test-log-marker-contract-v002.py为合成日志合同测试，不能代称实际native通过。
