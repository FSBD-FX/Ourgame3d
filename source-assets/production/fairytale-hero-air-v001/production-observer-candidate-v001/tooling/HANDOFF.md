# Air6 production independent host checker v001

本NEW工具只读源与运行原件，绝不启动UE、改Source/Content/E/ledger、构造媒体/音频或创建Root批准。optional `--output` exclusive创建一个新JSON；失败保留原件和固定阈值，不搜索配准、不放宽门槛。

运行接口已定在父leaf `host-checker-protocol-v001.json`。本工具独立冻结 `Air-production-proof-checker-freeze-v001.json`；父 `HeroAir-production-observer-source-freeze-v001.json` 独立冻结C++/HUD，两个freeze不互相包含以防环。未来Root prereg同时绑定两者、真实production candidate/Source admission、实际compiled Source与DLL、逐条203GREEN、源49、实际import/tooling/native/independent saved回执。

Root实际import现使用v002，其contract代码虽与v001相同，host receipt的__file__ pin位于v002，故preflight必须使用Root prereg `import_tooling_freeze_pin`动态载入正确已冻contract目录。source-only没有native回执，可用原已冻v001合同只读检查source48+旧Sword49。

`production_Source_admission_pin` 的 after_files 可以是未被observer覆盖的最终6条；`observer_Source_admission_pin` 的 after_files为最终3条。每条必须是最终CM原样project-relative path/bytes/sha256、实际磁盘一致，且basename/bytes/SHA匹配相应frozen candidate源。不会要求旧production HUD仍覆盖observer HUD，也不要求production条数恰为7。CM source_files必须等于当前实际Source成员数量；必须含实际UnrealEditor-CodexDungeon.dll pin，Production精确1419。

Root prereg的root_run_directory是archive根目录，Probe的DungeonContentProofDir传archive/原件。archive/index.json使用 `hero-Air6-production-native-session-v001`，记录真实process_id整数、exit_code、root_prereg_pin/compiled_manifest_pin/checker_freeze_pin/source_probe_freeze_pin。模板RootApproved=false/is_template=true，入口先拒绝模板，不会代填批准。

Native验证重算真实3跳与6相速度键、None6的9-slot索引缺口和LGT9、全部49resident、当前owner/run/room/epoch（epoch0合法）及原子Clock/gear/tint；实际float .65f/.38f投影、72/416、高度.70、剑.50和单次镜像。普通Space的实际before/after及时间必须夹在前一地面callback与第一空中callback之间，E在首个完整跳跃后、第二Space前，第三Space在原landing[.06f,.12f)，最后Land5→两个相邻普通Ready callback/新DrawId。观察序号从实际H/V变化重算，绝不叫game jumpId。

startup49的98份真实BGRA bin均做CRC+全RGBA逐字节对PNG（RHI和editor source各一次），不能用sourceSHA字符串或CPU数据替GPU。source49读回全部完成于真实MainSubmix Recording origin/movie/input之前。原PNG逐像素CRC、一callback一MovieFrame、serial异步FIFO、exclusive文件名保留、实际Stop先于最终PNG flush。

原Dodge字节冻结的linear/sRGB/逆刚体bilinear函数直接复用；每3跳×6相各选按时间序号居中的实际callback，共18见证；body>=150/median<=40/fraction(error<=55)>=.60，blade>=8/median<=50/fraction(error<=65)>=.60全保持。原MainSubmix独立checker直接复用，检查engine/canonical原PCM、仅BlockAlign32/33可修、非静音和WAV/真实wall时长<=150ms，真实原点/首帧100ms门不改。试听、每个cue辨识、最终画风、J/Shift/save和正式20搭配仍OPEN。

```powershell
$airPython='F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe'
$airCheck='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\production-observer-candidate-v001\tooling\verify-Air-production-native-v001.py'
& $airPython -B -X utf8 $airCheck --source-only
& $airPython -B -X utf8 $airCheck --verify-preflight --root-prereg '<Root实际新批准.json>'
& $airPython -B -X utf8 $airCheck --native --root-prereg '<同一实际批准.json>' --archive '<实际archive根>' --output '<新host结果.json>'
& $airPython -B -X utf8 $airCheck --paircheck --left-prereg '<实际left批准>' --left-archive '<leftarchive>' --right-prereg '<实际right批准>' --right-archive '<rightarchive>' --output '<新pair结果.json>'
```

工具产出时实际只执行source-only（原source49准备检查）与合成host测试，未运行未来Root preflight/native/pair，未证明任何实际GPU/原生运行/试听PASS。13组host测试覆盖36个左右draw正例、None6/full49、finite/半开/tiny positive、时钟/owner/HP/UI/重复DrawId/缺相/重跳窗口/普通输入因果、203逐条、真实形状49BGRA转换正例及更新CRC但错RGBA负例、PNG CRC/FIFO/StopFlush和pair PID/编译版本负例。合成source/RAW bins/PNG只用于算法验证，全标synthetic，不能当原生媒体。

validation-runs旧迭代全部保留；早期11/13组结果不代表最终源版本。只以本freeze accepted_host_result唯一pin为最终结果。多个旧合成98MiB RAW fixtures保持原位，不复制至E，不重复生成；fixture manifest单独登记其provenance，工具执行闭包与大fixture payload分开。任何后续修复必须NEW版本，不能修改当前冻结工具/门槛或删除失败原件。
