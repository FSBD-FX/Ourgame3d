# Death media v001（仅候选；未编码/View）

严格接收Death observer/tooling v006 freeze `0b8db789657b07945dd4abd8777218f0ec29a21b9a1da41186550b9d8056701b`；native/session及independent receipt仍v005。session必须exit0/nativePASS/independentPASS；报告SHA、PID/run、Died事件、Mask63、原1秒/100ms余辉和真实coin9 receipt一致，不能拿在跑的index或失败报告生成PASS展示。

Death0..5六原幅1280×720 PNG都来自同一原Died且原 `[death_at,death_at+1)` 的独立coverage_witnesses，保留真实DrawId/SourceEventId/原clock/source/位置。原1秒后的保持末帧不能补相。五个phase边界0→1→2→3→4→5各必须有且仅有原连续callback i→i+1合格对，缺任何相邻对即validate-only失败，绝不借非相邻、后续保持帧或插值假造。copy十张join原幅PNG，不做裁剪/缩放/像素修改。

真实自动coin额外copy三张原幅：首次consumed之前紧邻一帧、首次consumed、最终complete；记录各实际sim/HP/ground/wallet与Rewards原文。coin9、operation/source/owner、before→after+9和真实拾取位置均核同一independent自动拾取见证；最终钱包照原件，不硬写29。金额只写metadata，不在无UI原图上补伪数字。同一帧若顺序收多币，核前后callback钱包与全部新增ledger连续链；Guard.Before可能是中间ledger状态，绝不伪造一张该钱包的PNG。首实际原件即前callback20→同帧Bat+4至24→Guard+9至33，所选图保留真实20/33；初草案把前callback误当24的失败与原草案已在diagnostics保留。只正常J Guard，Knight/Bat仍诊断，不能据此称三敌正常全战。

完整视频沿已实际用过的StunIR/v011 VFR原时基，微秒PTS、原总duration、frames:v原数cap、framemd5数量/PTS舍入上界、解码末帧1280×720全保留。仅输出文件命名从StunIR换Death。MP4是静音有损展示副本，原PNG不改。全部展示输出与archive README/source-version-status-index必须先不存在，拒绝覆盖。生成后Root先E保全，再实际View；此候选没有启动UE/UBT/ffmpeg/View。

Root命令：项目Python `-B -X utf8` 执行本目录 `tooling/prepare-Death-native-media-v001.py --archive '<absolute completed native archive>' --validate-only`。通过后去掉validate-only才编码/复制。Root当前native_left_v001尚在跑时仅能确认session协议与freeze pin，不能预报native或独立PASS。实际终局后再作只读host核对。
