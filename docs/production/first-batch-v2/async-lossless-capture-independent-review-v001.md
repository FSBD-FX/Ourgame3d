# 异步原生PNG录制独立审查 v001

## 事实与审查范围

本审查只读Screenshots/Probe/PS/Python和本机UE5.5源码，没有启动UE/UBT、写Source/脚本/旧归档或查看本轮未开放的失败录像图像。四甲29两次失败的实际分类保留在 `xbw-four-armor-proof-independent-review-v001.md`：v001 HVY右缺primary bit2，v002 LGT左缺同bit，均耗尽global2；CRC/音画通过不等于29通过，也不证明PNG保存是唯一根因。

已读最终候选实际SHA256：

| 文件 | SHA256 |
|---|---|
| DungeonProofScreenshots.cpp | `1d1de2e6d21f238aa80f17bbac8fba889f33c296c4d5e3ba9b28646a87812ed0` |
| DungeonProofScreenshots.h | `52171255cf31cdbef1d887896361a0d706298099d3827b93412c64978b0579ae` |
| DungeonContentProbe.cpp | `85fc31d526c1d3d0697259879136d79f9b8bd4c9869c297d6ec676b566b6eff6` |
| verify-content-combat.ps1 | `688da2c4d09e3c21a4155e84038532b7f8191b86825a530357e71e7bb24ab997` |
| verify-native-capture-pixels.py | `be58db5f64b9daa41b32f6a9ba0894b85a507c4c432a5e4b488ab819af87e77d` |

## 所有权、顺序与生命周期

本机GameViewportClient2180–2206的实际顺序为GT接收Bitmap并设alpha255 → OnScreenshotCaptured → Reset请求 → Processed callback。异步分支在GT冻结文件名、尺寸、源CRC、捕获时刻，并对整份BGRA8作TArray深拷贝；worker只持有纯数据，不读UObject、viewport、FScreenshotRequest、GIsDumpingMovie或动作/音频状态。复制后再次算CRC并与源CRC比较，再真实SaveImageByExtension；receipt的saved为实际保存结果，不以enqueue冒充保存。

单FRunnable按FIFO处理，enqueue/dequeue、统计和Idle转换均在同Mutex内。成功入队后才增加Submitted/Pending，入队失败计Rejected而不会留下永远无法清零的Pending。Flush封队列后等待Idle，核Submitted=Completed=Saved=ReceiptsSaved且pending/failed/rejected为0；PNG或receipt失败都传播失败。重复Flush只返回已封存结果。未发现确定的丢唤醒、数据竞争、队列乱序或正常drain死锁。

预热不走后台队列，仍同步保存PNG及receipt后才由Processed开启音频；旧 `SaveNativeProofPixels` 函数与v041原函数文本逐字相同（各2,104字符）。安装时GT预载ImageWrapper，符合本机ImageUtils32–56的明确线程限制。正常结束先Stop记录/audio时间与movie，再在Save内flush，不用磁盘完成时刻延长已录音频。PreExit移除专用截图delegate后flush，销毁writer时Stopping并join线程，最后归还事件；此顺序让像素缓存活到其实际保存结束。

逐帧CaptureCallbackAt、EnqueuedAt、SaveStartedAt/CompletedAt分开保存。Probe的FrameWallOffsets仍在GT Processed callback产生，worker不替换这些时戳。它们仍不是GPU/音频sample-accurate时间；异步仅移走PNG压缩/写盘，不能保证每20ms姿态一定被读取。

## 外层证据门复核

初读外层仅requested/flush布尔值与旧CRC，建议追加实际queue摘要/序号核对；root随后已补入独立async gate。最终Python保留旧同步PNG尺寸、alpha、逐PNG BGRA CRC、完整且唯一receipt集合检查，只有metadata明确请求async才增加：

- metadata active与预热同步；summary requested/active/closed/flushed/success全真，enqueued/saved/completed/receipts等于实际movie数量，failed/rejected/pending为0。
- receipt按MovieFrame文件序，writer_sequence连续1..N；每帧async/copy_crc_matches为真，copyCRC等于nativeCRC，实际PNG仍独立解码核同nativeCRC。
- 每帧capture≤enqueue≤saveStart≤saveEnd，保存耗时一致；capture不晚于对应GT Processed时刻（1e-6只作9位JSON时戳舍入容差，不改动作/射程门）。offset数等于全部movie，预热仍为同步receipt，末保存不晚于flush完成。
- runtime要求真实flush与audio已Stop；PS命令行Async必须同时Fast，且最终强制`native_async_writer_verified`，不能仅凭命令行requested通过。

PowerShell独立ParseFile为0语法错误；未执行脚本。本静态审查未发现新增确定P1/P2。没有更改29名称、55秒/global2、动作/资源时序、原CRC、.1秒firstFrame或.15秒音画门；旧同步档案不被强制要求async receipt，也没有回写旧验证文件。

## 风险与验证边界

队列没有容量上限；55秒×60fps×1280×720×4的极端未保存BGRA积压约12.17GB。候选仅记录PeakPending/PeakQueueBytes，不能静态称内存或性能通过；必须保留实际峰值。单writer也可能因存储阻塞使flush等待，外层进程超时应保留失败来源，不丢帧/换帧来过门。

此文是最终候选的静态复核，不是UE83、异步实际count/CRC/flush或四甲29运行通过。后续必须由root实际编译/回归、实录、保全及原帧审看分别建立证据；没有四甲覆盖、完整美术、听感、D13或15单元完成声明。

## v003真实失败：命名分配依赖文件已落盘

已独立读取F批 `2026-10-15_猎弩四甲双向射击装填实际换装运行_v003` 的runtime-report/jsonl与文件名计数，未查看PNG。玩法29/29为true，但1853个movie receipts/offsets只对应1842个不同名字与实际PNG。00009共7次、00010共4次、00011/12各2次，额外覆盖合计11帧；严格唯一/完整捕获门正确拒绝。

真实同名时序：00009 seq10 capture17071637.6412116、saveStart17071637.7527346；seq11 capture17071637.6622891、seq12 .6794106均早于首个00009任务开始保存。已读本机FileHelper.cpp697–731：GenerateNextBitmapFilename先检查LastIndex是否FileExists，若不存在回0找空名。后台保存尚未创建路径时，后续GT请求重复取同一个exact名字。这是命名分配与物理文件生命周期之间的实际缺口，不是FIFO乱序。初轮静态审查未追到此UE落盘依赖，现按真实失败更正；旧“未发现确定P1/P2”仅是当时静态结论，不保留为通过认证。

runtime-report SHA `a85ccb1d1ec88fd1ab5593dd430cc7f2ce7ebf331d9e2802c8b760330d30dc2d`；jsonl SHA `3c24de66d52da4eaa4bbfd36409c3d3379cc343e17d92024b886a475978280e7`。root报告E v033保全1855files/6,833,813,202B、两遍SHA零差；本审查不复算全量保全，也未开放视觉验收。

拟GT提前创建exact请求路径的0字节占位，方向直接针对该依赖。但已独立读本机FileManagerGeneric.h77–79、cpp95–127与WindowsPlatformFile.cpp1471–1477：CreateFileWriter不处理FILEWRITE_NoReplaceExisting，非append OpenWrite为CREATE_ALWAYS，因此该UE flag不能作为独占/no-clobber保证。root裁定改Windows原生CREATE_NEW，成功后关闭handle再enqueue；其他平台async明确失败、旧同步路径不改。待producer最终冻结后只读审保留路径所有权/错误传播及reserved receipt/summary，不能先称修复通过。

## exact路径reservation候选只读复核

已读Screenshot cpp 17,399B / SHA `31cffc205a02b9abfbc72dbcfca753532ab5d7f36a487eeee1d1108519021cac`，header仍403B / `52171255cf31cdbef1d887896361a0d706298099d3827b93412c64978b0579ae`。修改限async分支：验证exact请求路径后，GT Windows CreateFileW(CREATE_NEW)建立0字节文件，成功CloseHandle后才设置FilenameReserved、计Reserved、深拷贝/入队。未另造名字、移动或删除文件。CREATE_NEW遇到现存文件直接失败，不截断它；create/close失败计reservation失败与拒绝，不进入正常worker。创建成功但后续enqueue失败也不删除占位，reserved/submitted不相等和Rejected会使flush/唯一完整文件门失败，保留现场。正常worker只保存带reservation标记的job。

已核WindowsPlatformFile.cpp1109–1116的FileExists仅看文件attributes而不看大小，故已关闭的0字节占位能被UE下一次名称搜索看到。WindowsHWrapper受PLATFORM_WINDOWS保护，其他平台async明确unsupported/fail；公开Flush签名、GT调用/封队列等待合同未改。旧SaveNativeProofPixels与v041再次逐字一致，预热仍调用此同步路径。

summary新增movie_reserved等于submitted/completed/saved/receipts，reservation_failed为0；每movie receipt记filename_reserved、真实Windows模式及reservation完成时刻。root verifier最终SHA `e83a63015073164f40a165a2710b6b1b6cdb56a982af06dc4ec5e5f325bc7721`已只读核：async metadata必须声明exact-engine-request-before-enqueue，reserved数量等于实际movie/offset数量且失败为0，每row reserved为真、模式匹配，并核capture≤reservation≤enqueue≤saveStart≤saveEnd。此前全部唯一/fullset/CRC/FIFO/flush门保留；旧sync分支没有新增reservation字段要求。Probe仍 `85fc31d5…b6eff6`、PS仍 `688da2c4…ab997`，没有动作、时钟、55秒/global2或像素门改变。

producer现已正式冻结确认，独立重新核cpp31cffc20/17,399B、header521712/403B匹配。当前未发现阻止root实际build83/新捕获的确定P1/P2。占位本身增加一次GT文件创建，改善后能否满足短窗与实际性能仍待实录，不能用静态根因修正替代运行证据。无新图像审看结论。

已独立读取 `evidence/async-filename-reservation-winapi-v001/result.json`，SHA `3fa903718ffd6087d3f6569e1c7dffac421fb1ec8bd92776b4bc52074a9a04b9`：真实Windows首次CREATE_NEW/CloseHandle成功，空文件再次创建和51B非空sentinel再次创建都拒绝error80，sentinel前后SHA同为 `55b728f0f43dbfc5634102360999ea3cac3820aae5134954c15087179591f028`。这是producer保留的实际独立WinAPI正负控制；本审查仅读取，没有重跑，也没有把它扩称UE命名/PNG/29运行通过。Source与旧失败来源保持冻结。
