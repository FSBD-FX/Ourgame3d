# Native 请求观察补充候选 v001

只改一份实际文件的提案：`projected/DungeonHeroLandingPriorityProbeV001.cpp`。基线是 Source303 / Production1425，compiled manifest SHA `97d4d0290ce17ff2bb0c4a97b3c03d8921bb398c8d0eddef1505809eae77ebd5`。没有新 Actor、播放、强制 cue、模拟或新的失败闸；原四段插入以外的所有字节可以严格还原。实际 Source/Content/tools/UE/E/状态均未改动。

Root admit 前执行 `python check-candidate.py --against-current`，检查六份依赖仍等于候选内 `before/` 历史副本，然后独立 review `native-observation.patch` / `exact-seams.json` / projected CPP。Root 仅将完整 reviewed CPP 安装到现有实际 probe 路径；Source 文件数保持303，不复制 fragments/tests 到实际 Source。修改后 `python check-candidate.py` 默认只验证候选内历史副本与 projected，不要求已被修改的实际 probe 仍等于旧文件；冻结成员全部在本目录内。

观察字段固定为每条 `observations[i].hero_locomotion_audio`：current_scope、callback_wall_window、真实 QueryCompletedGroundMotion 的 ground_witness、getter ring snapshot 的首尾 sequence/count、scope_changed、new_requests 与 captured_request_prefix_count。Finalize 顶层 `hero_locomotion_audio.captured_requests` 保存完整首次看见请求序列。每请求保留真实 Sequence/Source.Scope/Cue/对象路径/增益/pitch/AtTime/RequestedAt/StepOrdinal/FallSpeed/FallDistance/DodgeEventId/DodgeActionId，以及首次看见 callback index/phase/sim/wall窗口。

信息边界：getter 没有原事件 From/To、原始地面距离、RunGuid 或墙钟，相关字段明确 null/available=false；source_cause 明确由现有 cue enum 映射，不是新产生的游戏事件。ground_witness 是当前 completed callback 的已完成移动见证，不能冒充每条请求的原始区间。first_seen_wall_window 是两次 callback 之间的观察窗，不是发声时间戳。RunGuid 记录在 first_seen_current_scope，不能被宣传为源请求携带。

getter 是256条环且切换实际 owner/run/room/restart/epoch 时清空。观察端按 current-run +真实 request scope + sequence 去重；首次看见后复制到自身数组，随后 getter 淘汰不会丢已捕获记录。最终数组只保证完整保留所有**观察到**的请求，不能重建两次 callback 间的未观察淘汰/清空；ring_limit_seen/first_snapshot_truncation_possible/sequence_gap_count 显式报告此限制。sequence 缺口也可能来自 producer 被抑制/缺资源，不能直接当丢声或丢请求证明。

主机检查：18 checks，RED10 failures→GREEN0；测试直接使用当前实际纯 producer 的280cm、起跳和自然落地输出验证观察去重。另检查六份历史 source SHA、四处唯一 insert、全部旧代码逐字节 roundtrip、投影使用了同一已测试 cursor、无新增播放/控制/失败调用。未做 UE/UHT 编译、native运行或PCM/设备听感；Root fresh review 后继续原完整203、单次 Shift_right 与原 MainMix/PNG/因果检查。Light landing 若实际未出现，应按 captured_requests 如实标为未覆盖。

请求记录始终标记 request_only=true、audible_or_mix_attribution_proven=false。现有 CLI、正常走路280cm→E→Space→落地Shift、电影帧、主混音、纹理像素、装备ID、HP与所有原通过条件均原样保留。
