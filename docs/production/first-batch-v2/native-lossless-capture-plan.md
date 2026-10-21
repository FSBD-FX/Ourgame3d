# 原生无损快速实录候选

2026-10-15。仅 `-FastLosslessCapture` 显式开启的独立QA进程使用，默认试玩及旧录制方式不变；尚未构建/实跑，不预先称观测改善。

事实：Explore-v003真实三段普攻检查通过，技能单次伤害/完整收势通过。K技能Start10.600314610、Lock10.680314610；首次实测动作帧在10.690732710，已越过80ms未锁定段，因此原Timeline检查正确FAIL。不得凭正确截止数值伪造“观察到未锁定”。该次121原帧/11.448613301秒，Source及DLL已冻结并F/E留存。

本地UE5.5源码：GameViewportClient.cpp默认同步SaveImageByExtension后才广播processed；PngImageWrapper.cpp默认zlib3，Uncompressed为zlib0并使用快速UP过滤。截图保存是本轮采样延迟的可核实环节，但尚未独立量化它占全部帧耗时的比例。

候选：使用UE原生OnScreenshotCaptured提供的同一BGRA8视口缓冲，原样同步保存为zlib0 PNG；不裁切、缩放、重画、替换帧或改模拟速度。保留原processed时戳与所有六个音频函数，不用固定步长、离线音轨或时间伸缩；26条业务门/100ms首帧/150ms音画门原样。默认全图1280×720。

逐帧记录原生buffer CRC32、文件名、尺寸和保存耗时，独立Python完整解码每张PNG转回BGRA8核对CRC；包括单独预热帧，且不得漏帧/多帧/重复命名。该核查只证明像素一致，不代替实际动作、音效与同步检查。

成本边界：zlib0源帧约3.69MB，45秒×30fps上限约5GB；F/E完整保留最多约10GB/次，另有很小的快照和MP4。当前核实E剩余约176.6GB、F约214.0GB，足够本次实验；为避免长期无谓膨胀，该模式保持显式选择，后续再依实测决定更高效的无损方案。不得删除旧失败证据换空间。

实跑后必须记录实际帧间隔、首次Skill未锁定观测、源PNG全量像素核验、WAV/MP4门与F/E保留；若实验失败保留新版本，不放宽原检查或冒称已通过。

独立代码审查修正：原生delegate绕过ProcessScreenshotData的电影命名，因此在GIsDumpingMovie且文件名为空时原样使用引擎RequestScreenshot路径生成文件名；不自编帧序。只读InspectArchive也必须重新核对全部源PNG像素，不能只信旧receipt；原生核验失败仍先保留已算出的业务/音频/同步诊断。FrameWallOffsets为保存后processed完成戳，native save_wall_s不包含后续JSONL追加，因此不能把全长音画差门称作每一帧的精确采样同步。

实际构建exit0（045217）、完整UE29/29（045327），389文件40723553字节Source/Config/DLL/素材及工具冻结v011；当前首次native Explore-v004实录执行中，尚无通过结论。
