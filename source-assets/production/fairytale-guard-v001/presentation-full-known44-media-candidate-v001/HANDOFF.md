# Known44 AxeCycle 媒体候选 v001

这是NEW候选工具，不改actual `tools/scripts/prepare-guard-partial-native-media-v011.py`、旧工具冻结、Source或原生报告。原v011源码保留为只读reference。时序/编码/解码段仅改输出文件名：每项ffconcat `framerate 1000000`、真实offset差、passthrough、encoder/track微秒timebase、帧数cap、decoded framemd5逐帧PTS舍入上界及decoded-last-frame验证均逐字保留。没有在候选制作时运行UE、ffmpeg或View，没有生成新媒体或声效验收。

输入只接受 native=`guard-art-known44-native-observer-v001`、session=`guard-art-known44-native-session-v001`、scenario=AxeCycle，以及NEW `independent-known44-AxeCycle-v002.json` 成功回执。session必须绑定已冻tooling-v002 SHA，native与独立同首cycle_attack_id、63/15/63/15/15 masks、185HP、原生像素CRC/FIFO成功且帧数相符；错schema或旧partial回执直接失败。

24 required样本为Wake6/Ready4/WU6/Active4/Recovery4。每张必须在独立 `coverage_witnesses` 精确对应observation/DrawId/clip/frame/SampleTime/AttackId/SourceEventId/真实player+guard位置/object path，而且实际Drawn/SpatialCoverageEligible/DrawStack恰单层；WU/A/R再要求同首AttackId与native当前未interrupted。Wake和Ready并不误要求攻击ID，因为Ready合法event0/旧retained AttackId不是该行权威。Dormant与procedural gap只记录实际seen/unobserved，不要求补样本，不伪造缺口图。

样本直接copy2原整幅1280×720 PNG并复核SHA/尺寸，既不crop也不resize。生成三类join候选：WU5→A0、A3→R0、R3→同一retained首Aid的实际Ready。每侧同样来自合格witness；索引明确原frame_index/offset/sample/ID及中间隔了几帧。无合格后继Ready则如实missing_join，不能用后来另一次攻击补join。join只提供两个原幅PNG，不插值、不冒相邻或无pop验收。

Root在F:/Ourgame先进行只读输入核对：

```powershell
& .\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-guard-v001\presentation-full-known44-media-candidate-v001\tooling\prepare-known44-native-media-v001.py --archive 'F:/Ourgame/过程图稿与视频/<fresh-known44-AxeCycle-session>' --validate-only
```

去掉`--validate-only`才实际生成完整静音MP4、24原比例样本、join pairs和source-version-status-index。输出不会覆盖原有媒体/索引，失败原件保留。不同侧用各自fresh native archive原件执行，不能拼两个进程补首cycle。

新产物均`visual_reviewed=false`/`join_visual_accepted=false`/`formal_complete_units=0`，仍须Root E双SHA保全后才能View。CRC只证明捕获像素一致，不能从metadata直接推出每个资源的可见像素、足锁、完整57、全部44渲染或最终画风通过；MP4有损，原PNG才是像素原件。视频保留原真实时序且静音，不宣称声音被录下。
