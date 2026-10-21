# StunIR media v001（候选，尚未执行）

只接收已冻 StunIR observer/source/tooling v004（freeze SHA e3507a82b417883fe1dff70423c8035b72fa44cbd3c399f0d879f04923a4bf15）实际成功 session，以及同原件成功 independent-StunIR-v003.json。native/session 协议仍为 v003，不因目录版本改名。额外核实际报告 SHA、PID、run、同一 break_event_id/interrupted_attack_id、Stun15/IR15、原占用窗、正常 J/玩家实际损伤和 CRC/FIFO；错误 schema/hash/失败状态拒绝。

输出完整静音 VFR 与 Stun4/IR4 共8张1280×720原幅PNG。每相仅来自独立 coverage_witnesses 与同 DrawId/原时钟/实际位置/单整身斧 source；不重新计数、更不补帧。IR duration 读取原 [stun_end,original_occupied_until)，不固定400ms。相邻 join 仅同 break 的原连续 Stun3→IR0 两回调；无合格连续对则明确 missing，不借后续帧或后续break。此版不额外声称 Stun0前普通受击/IR3后Idle的完整视觉覆盖。

VFR 编码沿用 v011 全部微秒 PTS、-frames:v cap、解码 framemd5 数量和舍入上界、decoded-last1280×720验证；仅输出命名不同。完整源录像时长不裁剪或慢放。MP4是有损展示副本且静音；原PNG原件不改。全部展示副本/index须先不存在，避免覆盖已生成媒体；Root编码后按项目规范保全E，再实际View。

Root命令（绝对 archive 路径，先 validate-only）：

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 source-assets/production/fairytale-guard-v001/presentation-full-known44-StunIR-media-candidate-v001/tooling/prepare-StunIR-native-media-v001.py --archive '<actual fresh StunIR archive>' --validate-only
```

去掉 --validate-only 才编码/复制。此候选仅 Python AST、代码时基等价和选择边界检查；没有运行UE/ffmpeg/View，没有生成新媒体或声称原生通过。Death草案、Hurt4和Root准入不在本工具范围。
