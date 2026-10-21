NEW production observer source-only freeze，尚非完整工具/原生PASS。

Root可将new-source/DungeonHeroAirProductionProbeV001.h/.cpp作为新增两文件，并将new-source/DungeonHUD.cpp作为其future full-production HUD上的窄include/互斥spawn变更准入；未来HUD基准6f86936...，不要覆盖Root当前未准入的旧HUD。旧baseline h/cpp只在before-source保全，实际6366d0.../37812b...未改，旧baseline flag分支保留。

新增flag -DungeonHeroAirProductionProofV001，配合-DungeonFairytaleSwordAirPreview -DungeonFairytaleSwordEquipmentBoundPreview -DungeonContentProof -DungeonFastLosslessCapture -DungeonAsyncLosslessCapture -DungeonHeroAirProductionFacing=-1或1及NEW绝对DungeonContentProofDir。若Root明确选择前置Knight公共clearance，另加-DungeonHeroAirProductionClearKnightDiagnostic；只允许该Knight ApplyCombatHit，不Player/Guard/HP赋值/位置/AI/时间改写。

主flow正常Enter、A/D定向、SWD/NoArmor六相跳，正常E换LGT，LGT六相跳，第一LGT真实Land5 callback后原[.06,.12) landing内正常Space再跳，完整第三跳六相与两次普通Ready callback。所有mask63；没有伪造gameplay jumpId，只记录观察器transition ordinal。None6不算正式20搭配，landing J/Shift/真实save_restore OPEN。

49实际RHI原BGRA8与49 editor Source mip0原BGRA8在预热、audioOrigin/movie/输入前读取并Flush，原bytes/CRC独立保存。DTO不是GPU字节替代；host checker还必须对源RGBA/原PNG CRC/FIFO/实际float几何单镜像/固定source-pixel误差门/真实clock/音频PCM非静音与时长独立核。原helper Arming→Recording origin→最后真实callback Stop→Poll terminal→Flush沿用。两freshface PID需要分别预注册与完整archive，不跨side复用。

本Source-only静态API审查无剩余确定性阻断，但没有编译/UE/纹理导入/GPU/原生/试听证明。Root实际48 import+productionSource294+full203GREEN及后续观察器Source准入/编译仍是运行前必要项；独立tooling正在等Root import同步边界修复后续写，不可用部分tooling冒验证通过。整体候选最终freeze待独立checker/负例完整完成。
