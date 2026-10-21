# Guard full57 versioned candidate v003

事实：Root current partial baseline为Source222、Content1226、strict180GREEN；旧partial真实首次捕获v001 RED（唯一Wake漏frame1）已交独立driver rounding fix v003及observer failfast v004，本完整候选不覆盖该失败或当前partial实录。Worker只读actual，未UE/UBT/import/View媒体。独立实际DungeonStoneGuard.cpp C++17 selector Stage0 compile0/run1语义RED、production compile0/run0GREEN，不等于UE/world/render/art验收。

本候选新增versionednamespace DungeonFairytaleGuardFullV003 / SelectFull / PlanFull / ProfileFull。原DungeonFairytaleGuard::Select/Plan/Profile及原三tests不改；MissingMove仍真。HUD仅小unifiedpatch，新flag `-DungeonFairytaleGuardFullPreview` 显式选择full。无flag时原partial路径保持；full开启时缺row返回同请求clip的明确procedural gap，不落回partial Ready。全身一张包含固定斧，early return禁止额外axe/grip draw；finite GuardFeedback仍原consumer一次。

完整语义只消费 action-contracts-v005...JSON SHA f58f6fd6107a2f99004f753d97fe05fdc42a1f1f5ebd73c3a5f18c798750b5e1。v004 Move96、combinedFollow、Stomp旧350/350/400/400、Death坐标散文600ms均history，不消费。

| State | Logical frames | Runtime sample source |
| --- | ---: | --- |
| Dormant |1|explicit Wake0 alias，零新Texture |
| Wake |6|真实WakeStarted/End，原1s offsets0/.167/.333/.5/.667/.833 |
| Ready |4|真实Wake完成后的1s loop，不改AI idle窗口 |
| Move |6|真实accepted path128world cycle，blocked/stop无path不走帧 |
| AxeWindup |6|原Action.Start→ActiveAt1s，原.5锁向 |
| AxeActive |4|0/50/100/150ms，原ActiveEnd200ms |
| AxeRecovery |4|0/350/700/1050ms，原RecoveryEnd1400ms |
| StompWindup |6|0/150/300/450/600/750ms，原900ms及450锁 |
| StompActive |2|0/75ms，原150ms |
| StompRecovery |4|0/375/750/1125ms，原1500ms |
| Stunned |4|真实poise85/原400ms；普通Damaged仅真实material tint |
| Death |6|唯一Died时钟，1s视觉，首100ms余辉，末帧hold；gameplay0延迟 |
| InterruptedRecovery |4|仅StunUntil结束后仍在原OccupiedUntil的正区间，按变量余量归一，不固定400ms |

总57logical、最大56unique。Sample保留真实entity/attack/eventIDs/clock/interval/nativephase、movementdistance；死亡仅实际GameOver deadactor可取既有terminalAnimationTime，原kernel/time/history冻结，材质tint到.22必须结束。SourceEventID按原AttackStarted/ActiveWindow/RecoveryStarted定位，selector不发声音/事件/伤害。

## 精确源/注册边界

resource map独立列每frame原PNG+RGBA SHA/对象路径/rowbodybasis/groundpivot/证据pin。原16已导入路径复用GuardWhole_v001；另28个已知独立源仅提案新namespace GuardWhole_full_v003，并未导入。现10行45logical/44unique含Dormant；缺Move6、StompActive2、Recovery4共12source/registration entries。所有13行TrialAllowed=false/FinalAccepted=false；先前缺18条均未被本候选运行准入。Root必须为full版本逐row留独立trialrecord再开门，不能复用partial开门作为full授权。

211整行拒绝；221/223Move拒绝；profile也显式硬拒这3sourceID，缺Move不拿Ready遮。222FARlift/NEARsupport是同ENM-STN-003视觉变体，nativeSourceId不当runtime ordinal。精确Root future source/registration锁handoff SHA afa00509b6434224c909a92b93f501b9eac9b6395360b7a3ec65750f50e09df1 已并入：basis388 ONEcanvas133.01443299、[[251464],[246463],[260463],[259463],[266463],[309463]]，typed ArtistNearSupportDeltaPropagation，仍Trialfalse。224只有source接受、registration与WU→Active接续风险待Root，不捏造2帧注册；新版Rec源仍待。

215/216原strip layoutFAILED保留，仅完整独立512pose可用，不能把source独立接受称atlas通过或无pop。Active2/3地面Y432是鞋，不用斧刃alpha464。Death后四脚遮挡，只消费v002standing-root propagation设计参考（typed ArtistStandingRootPropagation），不用pile center，也不称测得骨/COM/隐藏足。ONErow density：Ready415、Wake398、WU212273、A215342、R216366、Stun213410、Death214365、IR217415、StompWU222388；各目标body100.8，无逐帧height归一。leftpivot=512−rightpivot，再由同GroundScreen放TopScreen，不改actorXY/sourcepixel。

## Root实际Stage0→production

1. 当前partial路径/tests保留。先仅加production FullProfile.h/DataV003.inl + stage0 FullPoseV003.h到模块，tests的三组复制到module Tests（stage0同字节）。不加FullPresentation/DrawState/HUDpatch。Root编译后执行 `./tools/scripts/test-first-room.ps1 -TestFilter CodexDungeon.Content.FairytaleGuardFullV003 -ExpectedTests 3`，应每组首个真实kernel/actor selector witness语义RED；必须保全真实结果。
2. 只把FullPose换production版，增加FullDrawState+FullPresentation，并从UnrealGame目录apply小HUDpatch。已 `git -C UnrealGame apply --check -- ../source-assets/production/fairytale-guard-v001/presentation-full-candidate-v003/patches/minimal-HUD-full-versioned-entry-v003.patch` 通过。Root自行合并后来的HUD改动，禁止整个HUD覆盖。先同filter3GREEN，再严格全注册回归：原180+此3=183；若独立Wake rounding第4回归已准入则181+3=184。以Root真实注册数/Source snapshot为准，不提前造新DLL/hash。
3. 三组test分别：实际kernel Axe4/R4+Stomp6/2/4及原窗/锁向/event只读；实际acceptedPath128/64与128footstep/stopblocked/普通Hit vs85poise/正余量IR/latebreak无新Active；实际UWorld/public Guard死亡+真正player死亡GameOver的central terminalclock/原kernel全sig冻结/restore同Died/material过期，以及onewholeaxe镜像pivot/Death/222元数据和legacy MissingMove隔离。UWorld fixture是integration回归，不当onscreen proof。
4. full全部门默认closed，先独立Root source/import/registration/trialrecord。import提案UI compression/NoMipmaps/NeverStream/sRGB/alpha untouched/bilinear；必须实核objectpath/尺寸/原源→importprovenance/内容不变hash，源码64字符pin不是导入证明。未来fullcapture observer必须另版本，当前v002partial actor只收旧DTO，不能加fullflag假称57覆盖。

风险：Active200ms/2×75ms会受真实系统卡顿影响；每row冠底/bodyroot是设计注册不是足锁或自动无pop，Root需真实实景检查join/facing/floor。首用加载仍须实际trace核查；当前partial漏Wake已发现更直接driver ensure，不用文档推论代替原生验收。此freeze只可编译准入准备，未称完整enemy接受。
