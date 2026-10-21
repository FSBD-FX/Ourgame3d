完整候选仅供 Root 实际准入与验证；本打包脚本没有启动 UE、写 actual Source/Content/E/ledger 或创建批准。

当前源码 freeze：e7b9f44fe53fa2c827d962b359494badf2efbf1ffb8d2e2face8dd2449fa6140（14 members，三个准入 Source），保持旧 baseline h/cpp 原 bytes。
当前独立 checker freeze：66f1dd8e0978ea05b89356bb99953a99c282af53bd150fbf7ee6c8bbc8483bfb。
当前协议：F:/Ourgame/source-assets/production/fairytale-hero-air-v001/production-observer-candidate-v001/host-checker-protocol-v002.json。
旧 checker v001 freeze 0883605a2d612fc979d3adb68e3df8191969d288e196db3dd2424efe061a34b6 原位保留；它不能用于真实 full-production preflight，因为相对42-member闭包从错误根目录解析。

总 freeze 是补充打包索引。Root prereg 的 source_probe_freeze_pin 仍绑定源码 freeze e7b9...，checker_freeze_pin 绑定上方当前 checker，不把总 freeze 冒充实际准入或批准。

Root 先确认实际48 import、Production1419、当前源码和 DLL、逐条完整203GREEN，再准入两个新观察器 Source 与窄 HUD overlay 并真实编译。Production after_files 可列最终6项，observer after_files列最终3项；旧7项准入历史/HUD overlay单独留存，不伪称旧 HUD bytes 仍是当前 CM。

已只读核真实 build-editor-20261019-010618.log 的三项 RHI LNK2019/LNK1120。静态头文件可见不能证明模块链接；旧失败保留，Root负责NEW显式RHI Build.cs补充修复与实际准入记录。必须观察器准入/修复后的当前 DLL 真正链接成功，再以当前源码/同 NativeRHI 全203严格GREEN绑定最终CM，不能以此前Source294通过替代当前296验证。源码 e7b9 和旧静态审查原件均不倒改。

Root 为每侧建立独立实际 prereg 与 archive：root_run_directory = archive根，DungeonContentProofDir = archive/原件；index.json 必须记录真实退出码/PID及对应pins。不得同时启动旧baseline/ContentProbe。启动前49实际原RHI和editor source的98原bin读回全部完成并Flush；之后按真实audio Recording原点→movie/普通输入→最后真实callback Stop→terminal→PNGFlush。

Probe 核心flags：-DungeonHeroAirProductionProofV001 -DungeonFairytaleSwordAirPreview -DungeonFairytaleSwordEquipmentBoundPreview -DungeonContentProof -DungeonFastLosslessCapture -DungeonAsyncLosslessCapture -DungeonHeroAirProductionFacing=-1或1；仅当 Root prereg 明确允许时加 -DungeonHeroAirProductionClearKnightDiagnostic。保持普通variable clock/隐藏UI/rangeoff，不加固定步长、时间/角色/HP/Guard改写。

普通Enter→定向A/D→NoArmor6六相Space→普通E换LGT→LGT9六相Space→原landing[.06f,.12f)普通Space再次跳→第三跳六相→相邻两次普通Ready。左右fresh PID。没有gameplay jumpId，只重算实际H/V的观察序号；NoArmor不计正式20搭配。

PowerShell运行工具（占位符由 Root 换成真实新路径；本脚本没有执行这些未来命令）：
```powershell
$airPython='F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe'
$airCheck='F:/Ourgame/source-assets/production/fairytale-hero-air-v001/production-observer-candidate-v001/tooling-freeze-relative-v002/verify-Air-production-native-v001.py'
& $airPython -B -X utf8 $airCheck --source-only
& $airPython -B -X utf8 $airCheck --verify-preflight --root-prereg '<Root实际新批准.json>'
& $airPython -B -X utf8 $airCheck --native --root-prereg '<同一实际批准.json>' --archive '<实际archive根>' --output '<NEW独立host结果.json>'
& $airPython -B -X utf8 $airCheck --paircheck --left-prereg '<实际left批准>' --left-archive '<leftarchive>' --right-prereg '<实际right批准>' --right-archive '<rightarchive>' --output '<NEWpair结果.json>'
```

所有 source-pixel 门槛、单次镜像、实际float几何、PNG CRC/FIFO、原PCM时长/非静音门不变。失败原件保留，工具修复走NEW版本。约 415,472,188 bytes 的480份合成fixture仍在原位，按独立provenance两SHA核，未复制到E、未当原生媒体；总freeze只索引其provenance，不自称包含全部fixture payload或全部49源PNG。源49闭包仍由原native-ready e378...、E599/E600与固定输入索引约束。

事实：候选源码静态审查、冻结闭包与主机算法/反例有记录。推理：这些可支持 Root 开始真实编译和原生验证。风险：运行时49纹理、原生动作覆盖/重跳、动态起落与Ready身形衔接、各cue辨识和听感仍由真实录制判定；本候选不声称它们通过。landing J/Shift/真实save_restore/正式20搭配/最终画风仍OPEN。
