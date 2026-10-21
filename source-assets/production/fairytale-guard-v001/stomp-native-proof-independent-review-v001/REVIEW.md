# Stomp50 Source窄审 v001

结论：未见明确C++接口或当前路线的必然阻断。范围仅freeze621729的Source静态审查，不代表编译、native覆盖、光学或视觉通过。14冻结成员SHA0差，实际Stage0七接口pins0差，当前Source260，三patch `git apply --check` exit0。未修改实际Source/候选/媒体或运行UE。

原生Aid2路径有真实依据：Guard原Axe RecoveryEnd=Start+2.6，IdleReadyAt=Start+2.9，比Axe冷却Start+3.1先到。Driver在IdleReady边界重新选择，Axe暂不合法，而140world侧点仍在Stomp160×90椭圆内，所以ChooseAttack可以自然选择Stomp2。无需向70内挤、写AI/clock或改时长。实际路线可达性仍须新native记录，静态几何不能替代运行。

Probe cpp111–115只pin真实首个Stomp AttackStarted且Aid2、真实WU0首150ms。139–141计63/3/15并在153按原ActiveAt/ActiveEnd/RecoveryEnd失败，不由之后攻击补相。PinHits96–107将真实feedback损血关联原Issued Hit和HitReceipt，追所有Guard损血链，原Guard HP185/零incoming保持；正常回Ready不强制frame0。原窗口、锁定、Entity/Kind/EventId/AttackId和actual frame时钟的独立重算仍须新checker负责。

Normal Enter/E/WASD与Knight/Bat公开诊断damage分开记录，未发现Guard damage/SetState/teleport/time赋值。140侧路线检查真实body extent+8和房间障碍；英雄自身Poise受击不产生prototype敌人24px push（Fighter.cpp1555有bEnemy条件），不能误判为必然被推出范围。两侧空间、受击与首Stomp可达仍属真实运行风险。

Draw DTO patch消费的正是同一次DrawTexture实际float Top/Size/UV/Tint/Scale/Rotation/Pivot，未拿重算double替代。row驻留与pending initialization为只读。旧44 renderer分支只加readback和显式原默认参数，旧44 profile/probe/assert/checker未改；bootstrap只在独立StompProof旗抢占相应observer。新sourceOptics可用实际quad/UV/UIScale/source SHA/RGBA建立固定投影，但whole工具尚未冻结，本审不称光学实现或结果通过。

唯一P2范围边界：cpp143 AfterReady只核previous clip=StompRecovery3和当前Ready.Time≥首RecoveryEnd，未显式核两侧draw仍同Aid2，也未限首Idle窗口。当前静止路线通常会因下一Stomp实命中令StompConfirmedHits>1而阻止晚补，但这不是回Ready身份oracle。作者确认独立checker已核R3同Aid2，拟NEW source-boundary-fix-v002追加当前Ready同Aid2、首[RecoveryEnd,RecoveryEnd+.3)和未见及时fail；旧621729不改。此项是scope收紧，未宣称已找到当前输入可重现假PASS。

新版本审查应避免错误收紧Ready→首WU0：前一Ready合法仍携原AxeAid1，而WU0才StompAid2。WU5→A0、A1→R0、R3→Ready应绑定首同Aid2，原ReturnReady可为真实任意frame。等待作者新pin后只需局部diff和pins复核。
