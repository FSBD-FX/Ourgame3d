# 独立Walk核验器v002：正常开局restart oracle窄修

事实：实际PID53212已正常退出；native报告passed/flow_complete=true、196 observations、restart_serial="1"。首版独立核验器仍在Scope/restart门失败，原log/index保留。源码链：GameMode.h146初值0；GameMode.cpp1168非pristine StartPlay调用RestartRun；2061 Scene分支在2068调用SetupSceneExplorationPreviewRun并提前return；654调用BeginEquipmentRun；508唯一++由0到1；1861 Enter只撤销waiting。Probe202记录初始serial，203及后续每tick与Run/owner/sword同时要求稳定，真实按键没有R。

推理：Walk正常ScenePreview已bound新局的合法serial应精确1；Guard pristine无初始Run的0属于另一启动路径。v002只将checker一处==0改为==1，不接受0或其他任意值，不放松其余scope门/动作/距离/层/像素断言。source依据和实际JSON只读pin见diagnosis-source-evidence-v002.json。

风险：尚未重跑完整独立核验。Root须在同一未改原件上执行新checker，不重录、不改report/PNG、不覆盖首版失败日志；若有下一问题，继续单独定位并保留证据。未打开任何媒体、未启动UE/UBT。

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-lgt-readability-v003\walk-native-proof-candidate-v001\tooling-v002\verify-walk-native-proof-v001.py --original 'F:/Ourgame/过程图稿与视频/2026-10-18_棕皮军剑双向行走与三连斩实录_v001/原件' --snapshot-manifest 'F:/Ourgame/source-assets/production/backups/v127-walk-169G/compiled-source-manifest.json' --expected-profile 'F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/walk-native-root-profile-input-v001/expected-profile-root-from-source-manifest-v001.json'
```

需要记录成功receipt时追加--write-receipt（只能新建，不覆盖）。重核输出另存新文件，如independent-verification-v002-output.txt；原independent-verification-output.txt必须保持。所有同目录依赖已经复制；HERE.parent仍是candidate根。首次工具freeze和工具目录完全不动。
