只读结论：v001不可准入；Root已决定v001/v002不准入，待guard_two_process新增v003。

阻断1：cpp142–144跨Step共用按Facing索引的cycle/postWalk计数，无预期held键/方向约束且不清earliercredit。必须phase-owned并核对实际held A XOR D与符号位移。

阻断2：cpp136/143/144每截图累加draw次数与纯getter完成位移，没有DrawId/FromTime→ToTime唯一witness。正常capture通常每帧一次，但重复采样可膨胀距离/次数。必须保留所有capture原行，只给新draw/新motion计数或重复fail。没有制造运行计数或声明复现。

非阻断：WalkFrame应独立从P.AnimationTime+compiledGait导出；已运行fixture可能跳过Enter，若声称actualEnter需明确起始条件/请求receipt。

成立：A/D/E/J使用InputKey无actor/animframe/clock强制；public LGT注册后通过实际E事务，sameID/version/operation+1；真实J三段owner/ID/帧核对；src Pending Profile必fail。未运行UE/UBT/import，不重复审美术原图。
