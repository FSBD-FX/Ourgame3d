# Air production checker derivative v002: relative freeze members

旧tooling/v001冻结088360...及全部fixture原件保留。真实full-production冻结719770...的42members使用相对本freeze目录路径，v001错误地相对项目根处理；已只读复现找不到F:/Ourgame/before-source/DungeonFairytaleSwordAirV001.cpp。

本NEW sibling目录保留HERE.parent=production-observer leaf层级。contract frozen()中的member check改为c.check(row,root=freeze_path.parent)。绝对member仍按原绝对路径验证，路径毒化/字节SHA/两遍检查不放宽。另修明确Source准入边界：full-production fallback仅existing-source/new-source源码7项可匹配after，before-source旧5及host源码不能冒after；observer显式source_files3保持。Root最终production6+observer3合法，不强制数量7。主native/pair/source-pixel/audio/几何/身份/普通输入验证代码逐字节复制v001，完整命令仍是同名verify-Air-production-native-v001.py的--source-only、--verify-preflight、--native、--paircheck。

Root未来prereg checker_pin/checker_freeze_pin须指本NEW版本，采用父host-checker-protocol-v002.json。source_probe_freeze e7b9不动，其他未来真实CM/203GREEN/admission/import回执要求不变。新增真实full42两SHA闭包正例、缺文件/错误bytes/poisonrelativepath负例及绝对member正例，旧13组行为PASS仅绑定原封未改逻辑；不重复生成98MiB合成GPU fixture，不跑UE/native，不覆盖旧结果。

```powershell
$airPython='F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe'
$airChecker='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\production-observer-candidate-v001\tooling-freeze-relative-v002\verify-Air-production-native-v001.py'
& $airPython -B -X utf8 $airChecker --source-only
& $airPython -B -X utf8 $airChecker --verify-preflight --root-prereg '<Root新实际批准>'
& $airPython -B -X utf8 $airChecker --native --root-prereg '<Root新实际批准>' --archive '<真实archive根>' --output '<新host结果>'
& $airPython -B -X utf8 $airChecker --paircheck --left-prereg '<left实际批准>' --left-archive '<left根>' --right-prereg '<right实际批准>' --right-archive '<right根>' --output '<新pair结果>'
```
