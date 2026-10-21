# Air production presentation tooling v001

Root只在实际production archive/session、prereg及frozen v002 checker真实结果存在后执行；脚本先原样只读重跑该checker并与已保留结果逐字段等值，不会构造Native PASS或启动UE。新增输出必须是 `F:/Ourgame/过程图稿与视频` 下不存在的直接子目录。

```powershell
$airPython='F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe'
$airMedia='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\production-observer-candidate-v001\presentation-tooling-v001\prepare-Air-production-media-v001.py'
& $airPython -B -X utf8 $airMedia --archive '<实际archive根>' --root-prereg '<实际Root批准>' --independent '<真实v002独立结果.json>' --validate-only
# Root复核后，用新的F媒体目录：
& $airPython -B -X utf8 $airMedia --archive '<同一archive根>' --root-prereg '<同一批准>' --independent '<同一真实结果>' --output 'F:\Ourgame\过程图稿与视频\<日期_主题_新版本>'
```

原始MovieFrame全保持原nativearchive，索引逐帧path/bytes/SHA/实际wall offset引用；本新包只另存18个原幅见证、真实joins原幅、末原幅、metadata以及完整engine/canonical WAV副本，不重复整套PNG或98bin。Root须在View前保全**完整原nativearchive和新presentation包**，脚本不写E、不View，不把引用文件谎称新包内部副本。

VFR直接复用旧已验证microsecond helper（SHA655457...）全部PNG、不drop/造帧/速度拟合，silent编码PTS始于首callback；mux对video加真实firstoffset，完整canonical PCM从PTS0编码AAC，禁止-shortest/-t/trim/替换音频。原enginePCM与canonical仅BlockAlign修正已由frozen audio checker验证，两份完整WAV都原字节拷贝。音频PTS0绑定helper Recording协议原点；不宣称设备sample onset/延迟已测量。

合成测试明确发现默认MP4 movie_timescale1000虽video_track_timescale1e6仍把offset量化到毫秒；失败原件保留。现在mux同时设置movie_timescale1000000，随后独立完整AV解码、copyts framemd5全frame/实际absolutePTS核对；固定derived N×1us+2us门没变。完整AAC解码检查samplerate/channels、原samplecount差≤2048（最多两1024 priming/padding），不声称AAC与PCM逐字节一致，完整原WAV保持可核。

LGT六相含原幅纵板和256×320裁板；None/LGT/rejump18相另板，三组实际相邻Land5→Air0/Ready原幅pair板。label32/gap12，cellH364或764，逐rectangle非重叠，并重解码PNG验证每个game rectangle RGB等于原图exact crop，无resize/重绘/标签压原图。索引包含README；索引自身按惯例不包含自身pin。

实际ffmpeg binary/hash/version、Python/Pillow/imageio_ffmpeg版本和module pins写入正式输出环境记录。工具制作时只运行小规模6张合成PNG/.25s合成PCM测试，不运行真实archive/preflight/native/E/View；所有合成原件和失败保留且标为synthetic。最终5/5测试PASS；最后唯一改动为README写入移到索引扫描前，保全前源并按AST验证，仅写序变化，不重复AV测试或扩大门槛。

输出状态全部View=false、visual_reviewed=false、audio_listened=false、FinalAccepted=false；正式20、J/Shift/save及美术/音色验收仍OPEN。任何失败保留NEW目录、日志和partial文件，不覆盖或自动重试。
