# Root 快照／预注册最小复用说明

事实：只读时 actual Source231 / Production1254，`last-build.json` 指向 `build-editor-20261018-130513.log`、ExitCode0。当时最新落地125540仅focused3GREEN，新full184报告尚未落地，不能用focused报告建立全回归快照。pins在本目录JSON；这不是新的原生验收。

直接在 NEW Root helper 复用 `tools/scripts/freeze-guard-partial-current-build-v131.py` 的 set去重、copy2非Content、Content原位pin、DLL晚于Source检查及两轮源／副本SHA。以下局部改动已足够，不需要另造快照格式：

1. `--report`仍接实际全套 `index.json`，校验`succeeded == len(tests) == len(unique fullTestPath)`，各state=Success/errors=warnings=0，其余failed/succeededWithWarnings/notRun/inProcess=0；实际registry当前应184，以完成的真实注册清单核定。`current_build`继续pin last-build.json且ExitCode0。旧181/Source223/Production1226常量不能留到full模式；source/prod从实际文件集计算，并与Root本次明确准入数量核对。
2. 文件集合保留actual Source/Config/Content、uproject、DLL、build+log、全套report、新helper自身。追加冻结fullv00336项、v00412项、Known44observer15项及各freeze，Rootfull的row-trial/import-manifest/independent-import-verification，native import receipt。full rows非alias的每帧source、registration_evidence、source_index与Dormant.alias_evidence作为输入pin加入。旧partial历史输入可保留，勿替换成历史Source副本作为current Source。
3. full审批顶层是`RootApproved`，不是旧`TrialAllowed`；Dormant没有`registration_evidence`，只有`alias_evidence`；full.frames使用`object_path`，不是旧`proposed_object_path`。最省事是完全替换旧prereg生成尾段，直接read新的 `presentation-full-known44-observer-candidate-v001/root-templates/known44-AxeCycle-Root-prereg-TEMPLATE-v001.json`。
4. 新prereg只填`compiled_manifest_sha256`、`strict_registered_tests`、`source_files`、`production_files`；`admitted_source_files=[actual[row['path']] ...]`取实际快照pins；`candidate_freeze_pin`取 `known44-AxeCycle-freeze-v001.json` 当前整件pin。然后显式`is_template=false`、`pre_registered_before_capture=true`。写NEW路径，不改模板。模板已绑定实际Root10 known行/13 allrows/三closed gaps及现有28 import两SHA，无需再跑旧approval循环改门。

`compiled-source-manifest.json`最小必需键如下，现helper均已有：`files:[{path,bytes,sha256}]`、`full_suite:{path,bytes,sha256}`、`current_build:{path,bytes,sha256}`、`strict_registered_tests`；建议继续保留`source_files`、`production_files`、`source_verification_passes:2`、`source_hash_mismatches:0`、`content_packages_pinned_in_place:true`。新checker自己从files重算实际Source/Production集合及数量。

路径契约：manifest.files与prereg.admitted_source_files的`path`必须是相对于 **F:/Ourgame** 的POSIX，例如`UnrealGame/Source/CodexDungeon/DungeonHUD.cpp`；checker以此前缀选文件集，不能改成全绝对paths。`full_suite.path`、`current_build.path`、Root审批/import/twoPass/candidate_freeze pin支持Root相对或绝对路径，但相互比较的pin对象必须一致。source frame.source.path已有绝对路径，可以直接保留。参数`--snapshot`支持Root相对或绝对；`--root-prereg`/PS RootPrereg建议绝对，因为Path.resolve/GetFullPath按调用者CWD解释。工作目录保持F:/Ourgame即可。

风险：快照后改Source、Content、已pin工具/helper或last-build.json会被source-only严格拒绝。Root应先完成全部准入与全套测试再冻；实际prereg在snapshot完成后、第一次capture前另写。编译成功/加载44不等于本次24必需纹理原生覆盖，更不等于full57视觉通过。
