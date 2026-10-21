# Current Hurt1286 checkpoint tooling v001（待Root实际执行）

只准备本次fresh compiled snapshot、Guard source-profile、精确Hurt32 Production扩展审批及正常手动launcher，不改Source/Content/tools/README/CMD/旧prereg，不运行UE/UBT。Hurt生产与正常AxeHurt observer源码由其他worker/Root准入，本工具不复制或覆盖它们。已有Hurt32实际导入成功／独立old1254+new32两SHA为事实，不等于生产实现已编译、187GREEN、GPU完成或原生Hurt视觉验收。

Root复制 `root-templates/Root-checkpoint-input-TEMPLATE-v001.json` 到一个NEW实际Root输入文件（不要改本冻结模板）。在真实生产准入、成功build、全187每项Success/0Error/0Warning后填：

- `full_suite_pin`：本次真实全187 index.json；`last_build_pin`：本次实际last-build.json；`DLL_pin`：本次DLL。
- `snapshot_output`：NEW `source-assets/production/backups/<Root实际版本>`，不得已存在；`registration_output`默认NEW `source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v001`。
- `checkpoint_tooling_freeze_pin`：本目录whole freeze实际path/bytes/SHA；`Hurt_production_candidate_freeze_pin`：runtime worker最终冻结版的真实pin，不能用Stage0 stub冒生产。其目录预计 `fairytale-hero-state-gap-v001/hurt-runtime-production-candidate-v001`，文件名/hash以worker最终交付为准。
- `Hurt_actual_native_import_receipt_pin`与`Hurt_independent_twoSHA_verification_pin`：Root核实后填当前两实际件，精确pins列于 `observed-real-input-pins-v001.json`。模板维持null，不冒Root审批。
- 若同时准入新observer：在`additional_admitted_candidate_freeze_pins`填其最终冻结pin，在`additional_admitted_source_paths`填actualSource相对POSIX路径。也可暂不准入；不要求Axe/Stun/Death重新同时capture。其他需保全事实可填`additional_pinned_inputs`。
- 保留已绑定实际v135 baseline/source-profile和已冻`guard-known44-profile-extension-candidate-v004`；检查后只在NEW实际Root请求设`is_template=false,RootApproved=true`。

所有pin均为恰好path/bytes/sha256三字段；Root请求pin可绝对或workspace相对，Source清单／manifest rows必须workspace相对POSIX。Source数量不填、不预判，从届时真实Source目录动态计算；Production严格1286。代码要求实际DLL不旧于Source、真实报告不旧于DLL。

Root命令：

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 source-assets/production/fairytale-guard-v001/current-Hurt1286-checkpoint-tooling-candidate-v001/tooling/freeze-Hurt1286-current-build-v001.py --root-input '<NEW实际Root请求绝对路径>' --validate-inputs-only
```

validate-inputs-only只检查新编译输入/全187/候选pin/1286数量等前置，不写输出，也不冒完整extension source_check通过。删掉该开关才执行冻结：沿v135 set去重／NonContent复制／Content原位pin／两轮全部source和copy SHA，生成NEW manifest；再生成绑定真实fresh manifest SHA的Root extension approval及Guard source-profile，调用原已冻v004 checker执行完整Guard44/Hurt32 exact old1254∪new32／sourceRGBA／native32／两SHA门，全部成功后才发布manual-input和checkpoint receipt。失败保留新输出，不覆盖、删除或伪改旧失败；下次用NEW输出版本。既有Root trial10/allrows13/gaps和Guard28来源不变，FinalAccepted始终false、preload/runtime凭据null。候选没有自己审批或新native成功。

生成文件位于registration_output：

- `production-extension-Root-approval-Hurt1286-v001.json`（仅Root执行且显式审批请求才能生成）；
- `guard-known44-source-profile-prereg-Hurt1286-v001.json`（source-only，schema沿既有Guard接口；不声称新Axe/Stun/Death capture）；
- `manual-input-v001.json`及`checkpoint-receipt-v001.json`（仅完整source preflight成功后产生）。

手动launcher候选 `tooling/launch-guard-room-native-trial-v007.ps1` 保持旧v006参数 `EngineRoot/Snapshot/LightArtTrial/GuardFullArt/ValidateOnly`；新增RootCheckpoint默认指上述推荐registration目录的manual-input。旧CMD当前只传LightArtTrial/GuardFullArt，因此Root后续只需将CMD脚本路径改为本候选v007绝对路径，不在此修改CMD。先加ValidateOnly验证，之后正常运行才可见启动UE。所有棕皮Ready/P1/P2/P3、SWD Walk/EquipmentBound flags保留，新增HurtPreview；不带ContentProof/observer/自动输入/公开伤害/固定时钟。试玩仍Enter/WASD/J/Shift/Space/E/R手动，普通LGT E提交保持.50s。

精确Hurt三目标：ActualPoiseBreakFourPhasesAndExclusions、RealBindingSource32MirrorAndAtomicRejection、RealCodecPauseContinueKeepsAgeAndEquipment，完整前缀CodexDungeon.Content.FairytaleSwordHurtV001。生产必须实际包含只读接口／HurtPlan/Profile与3新presentation文件；旧Guard仍仅known44，Move/StompA/R有显式gap。当前本候选仅AST／PS parser／现有184与模板拒绝边界检查；没有实际新187/preflight/试玩/录制成功，后续原生和视审由Root。
