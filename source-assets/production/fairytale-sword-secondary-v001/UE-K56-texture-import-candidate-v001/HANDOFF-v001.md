# K56 exclusive native import candidate v001

仅准备工具，未启动UE，未导入，实际Source303/Production1439仍旧ae00569b基线。主机最终预检reports/host-preparation-preflight-v002.json实际exit0；16个malformed/alias/SourceContract/同PID非零退出门测试GREEN，Python4文件语法和PS静态解析通过。v001主机预检是早期未冻结代码的历史准备证据，最终以v002当前工具pins为准；两者都不是可用于Native的冻结准入proof。Root launcher会在新F evidence目录重新执行包含candidate_freeze pin的主机预检。

输入manifest：50346B /28c4ee7fad74b065eac69ef6a62f6439c888d44576badfb23fd2e6a621599f34；SourceContract156178B/ef1d2418b7bae89da963fe6d3963c250fa84f89b7108581058dbf06d12be1d4b。CM421789B/ae00569bad81eae953b989b964ed2592e6f1e8e0dff43b81163358c43bb3007a。Root实际源数据审阅2192B/53e35660e49db55b7f66862033f045d28821547ac1998f8bfdcd72ccd806ce58已作为freeze依赖，范围仅首次56纹理试导入。

来源是8帧×7层的新56 Texture2D；所有56源PNG的原bytes/SHA、RGBA512解码hash、8帧四body-owner原RGBA排他重组均实际校验。K6只复用K0源，但56各自独立target，剑只检查既有引用不导入。Native输出唯一 /Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_{Owner}_{Frame:02d}_v001。

旧14真实脚本和实际导入receipt均为srgb=true、TC_EDITOR_ICON、TMGS_NO_MIPMAPS、TEXTUREGROUP_UI、TF_BILINEAR、never_stream=true。本次沿用这些实测设置，纠正最初false前提；不新增Material，不替换/删旧asset，不自动重试或清理失败。TC_EDITOR_ICON设置/尺寸/类/源文件名会在保存后实测；GPU实际像素格式和显示像素属于后续native pixel checker，不以本导入receipt虚构GPU证明。

执行前必须无UnrealEditor/UnrealEditor-Cmd/UnrealBuildTool进程。PS首先核对固定CM/manifest/freezeSHA，再创建此前不存在的Root F evidence目录，主机decode+CM1746全pins+全Content快照通过后才启动UE。Native使用旧14已实际成功的API，保留claim/native结果/逐56saved uasset pins/manifest SourceLineage；既有1439文件每个SHA不变、Source303及其它Content全成员不变、新增恰56、总1495、全/Game registry新增恰56均双pass实测。原生退出log、launch/exit同PID和OS实际退出码单独保存。OS非零直接失败；OS0但Python导入失败/receipt缺失也由只读验证拒绝，不能当成功。

Root最简命令（在本候选freeze独立审阅后，将下列REVIEWED_FREEZE_SHA换成交接消息的实际SHA；不是自行重算后绕过审阅）：

```powershell
& 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/UE-K56-texture-import-candidate-v001/run-K56-native-import-v001.ps1' -Manifest 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/K8-production-contract-builder-candidate-v001/output/source-contract-package-v001/texture-import-manifest-v001.json' -ManifestSha256 '28c4ee7fad74b065eac69ef6a62f6439c888d44576badfb23fd2e6a621599f34' -CandidateFreezeSha256 'REVIEWED_FREEZE_SHA' -Out 'F:/Ourgame/docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-native-K56-import-v001'
```

只读复验脚本verify-K56-import-v001.py已由launcher自动调用；它只写新verification JSON，不修改asset。须在后续Source接入/新编译之前完成，因为其条件刻意要求Source303与旧ae00569b各pin仍全相同。任何非零或部分导入都保留原目录/asset，不得重跑覆盖。新trial须由Root审查实际失败后另行决定。

本候选不分配E编号，不生成新图/音频，不View，不改actual Source/Content/tools/status/ledger。Native导入、真实56Texture2D属性、1495结果、渲染、动作、音频、完整装备单元与FinalAccepted均未由本代理宣称完成。
