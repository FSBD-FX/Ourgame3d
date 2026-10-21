# Death v006：仅修真实 C4456 局部变量遮蔽

原 v005 全部冻结和真实失败 `UnrealGame/Saved/Bootstrap/build-editor-20261018-154754.log` 保留。实际编译器指 CPP387 的 collection `C` 遮蔽 CPP345 的 PlayerController `C`。本候选只将 collection 声明及其随后两行引用改为 `Collection`，共三行。没有状态／时间／帧／HP／receipt／奖励／移动行为变更。

Root可以仅替换 new-source/DungeonGuardArtDeathProbeV005.cpp；H与protocol原字节不变。`patches/Death-source-v005-to-v006-C4456.patch`是对应actualSource目标的最小delta。HUD两个startup补丁与v005原件相同，已经准入时不再应用。

主checker仍名verify-Death-v005.py，native/session/Root prereg schema和独立receipt均维持v005；只改自身whole freeze文件名到Death-candidate-freeze-v006.json。launcher改文件名capture-Death-v006.ps1，并只改whole freeze绑定。PID在Start后立即落盘、exit/nativepassed在checker前落盘顺序保持原字节。没有放松任何oracle。Root模板filename v006且freeze path指新目录，仍is_template=true/所有新SHA null，必须Root新build/full-suite/snapshot后填真实prereg，不能复用第一次编译失败的DLL。

完整操作、时钟、范围和风险沿用原v005/HANDOFF.md。Root命令：本目录tooling/capture-Death-v006.ps1 -Snapshot '<freshactual>' -ProfilePrereg '<NEWsourceprofile>' -RootPrereg '<NEWDeathprereg>' -ApproachSide -1 -Version v001 -ValidateOnly；确认source-only后去掉ValidateOnly才启动。此候选没有启动UE/UBT/View，静态通过不冒编译或nativeGREEN。
