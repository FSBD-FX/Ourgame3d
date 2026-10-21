# 稳定 Editor-game 试玩副本候选

事实：已只读核对运行清单为1778文件、143122086字节（136.491857MiB），包括全部Content1768、Config3、uproject、游戏模块DLL/modules、CodexDungeonEditor.target，以及项目UnrealMCP descriptor/DLL/modules。源模块、插件与已安装G:/UE_5.5的BuildId均为37670630。没有实际stage，也没有启动UE。

推理：把这些文件逐字节物理复制到独立项目根后，后续修改开发目录的Source或Content不再影响这份试玩。启动检查只读副本的固定runtime/编译历史/实际stage证明和固定G引擎，不解引用编译历史JSON中原Source的路径。

风险：这是依赖本机完整G:/UE_5.5（含engine plugins、VC runtime）的Editor -game副本，并非打包分发游戏。引擎仍是共享依赖；启动检查固定EXE、modules、Build.version和BuildId，不声称冻结整个引擎安装。插件Content当前为空；若以后增加plugin Content/Config/Resources，必须新做清单，不能借本清单漏拷。第一次副本原生运行可能建立新的Saved/Intermediate/缓存；这些运行生成目录不从开发目录复制。实际新运行仍须Root证明。

## Root 实际复制

1. 核验本候选freeze，另在Root自己的新目录写非模板stage request。模板为Root-stage-request-TEMPLATE-v001.json；只把复制scope授权为PHYSICAL_RUNTIME_COPY_ONLY，填本实际inputmanifest/candidatefreeze及已经真实完成的原v003 native pair pins。此授权不授予试玩、不授予最终验收。
2. 运行：

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-hero-air-v001/stable-preview-candidate-v001/stage-stable-preview-v001.py' --input-manifest 'F:/Ourgame/source-assets/production/fairytale-hero-air-v001/stable-preview-candidate-v001/runtime-input-manifest-v001.json' --Root-stage-request '<Root实际新request.json>' --report '<Root实际新copy-result.json>'
```

3. 工具只接受NEW目标F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906。它在复制前核Root request/candidate pins、原CM全部当前成员、完整runtime成员集、原native pair与固定引擎；每个文件用xb创建，禁止覆写/链接，不复制Source/Intermediate/Saved/PDB/exp/lib。源/目标各做两遍SHA，副本runtime目录精确核员（包括hidden/system），原CM成员在复制后再次核验。成功生成_proof/runtime-snapshot-manifest-v001.json及stage-copy-receipt-v001.json，仍不批准试玩。
4. 任一步失败保留目标已复制文件，不删、不覆盖、不重试旧目标。--report必须是新文件；退出3表示复制失败。已有目标完全保留。新一轮修复应由Root选择新版本，而非覆盖失败证据。

## Root 副本原生证明与有限试玩批准

Root须实际从副本uproject运行固定G引擎，留存真实PID/命令行/加载副本DLL或等价原生依据、正常试玩flags以及前后runtime固定字节核验。Root-staged-native-proof-TEMPLATE-v001.json列出所需事实；工具绝不生成伪造native success。原开发项目pair不能代替这一步。Root按已有E保全规则保全实际媒体后审阅，另写真实staged proof及visible review receipt，所有证明及其pin应放副本_proof下。

仅Root可在_proof/Root-stable-approval-v001.json写非模板LIMITED_WIP批准，并填副本runtime_manifest_pin、stage_copy_receipt_pin、staged_native_proof_pin与Root_visible_review_receipt_pin。pins均为相对副本根的正斜杠路径/字节/SHA。不得把完整原速观看/试听/最终验收冒填为通过：full_realtime_playback_reviewed=false、audio_listened=false、FinalAccepted=false、known_pose_join_refinement_open=true。

副本根“启动钟盔轻甲试玩.cmd”调用副本_proof/tools中的PowerShell脚本。正常Enter/WASD/J/Shift/Space/E/R，保留全部v013普通flags、轻甲与Guard，绝无ProductionProof/自动输入/诊断伤害。正常入口将完整核验副本runtime全部字节、Config/Content/Binaries/Plugins精确成员、复制证明、编译历史、实际副本原生证明与固定引擎，然后才启动；不再读取F:/Ourgame/UnrealGame/Source，也无需Python或旧tools launcher。

## 候选验证边界

小host fixtures测试复制后独立性、不覆写、源错SHA、复制中变更、目标改字节、hidden额外成员、hardlink/路径逃逸与falseRootrequest。首轮fixture漏建空Binaries导致1ERROR已保留；修正host fixture后新session7/7通过，未放宽实际runtime门。PowerShell语法0错，false批准模板在UE前拒绝。host fixtures保留，故意hardlink反例目录不进入准入代码闭包；其测试源码及真实结果进入freeze。没有用fake批准跑正向native入口，也没有实际stage/原生/试听/美术验收。
