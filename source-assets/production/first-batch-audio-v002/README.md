# 首批专用音频 v002：本地 CC0 派生候选

日期：2026-10-15（Asia/Shanghai）。状态：**5个WAV已制作并完成信号/来源/派生重放预检；待UE导入、真实事件绑定、试听与运行混音验收。** 没有设备播放、UE/UBT、外部API、付费供应商或图像生成。旧17个程序合成候选、旧导入器和既有Source均未修改。

## 实际交付

全部输出在 `wav/`，文件名为 `<ID>__v002.wav`，48kHz、单声道、PCM signed16、实际sample peak均为 **−4.500292425884415dBFS**，首尾样本均为0，0样本abs>=1。总计5个不同SHA的WAV，140,380字节。

| ID | 本地CC0原素材 | 输出长度s | RMS dBFS | 从剪切/包络后浮点的增益dB |
|---|---|---:|---:|---:|
| AUD-XBW-RELOAD-DRAW-01 | RPG Audio / creak3.ogg | 0.32 | −18.221896 | +3.303150 |
| AUD-XBW-RELOAD-INSERT-01 | RPG Audio / metalClick.ogg | 0.18 | −30.900369 | +3.607722 |
| AUD-XBW-RELOAD-COMPLETE-01 | RPG Audio / metalLatch.ogg | 0.24 | −26.170852 | −5.144809 |
| AUD-EQUIP-ARMOR-CLOTH-01 | RPG Audio / cloth2.ogg | 0.40 | −23.527698 | +5.920478 |
| AUD-EQUIP-ARMOR-METAL-01 | Impact Sounds / impactPlate_light_000.ogg | 0.32 | −25.625312 | −1.815046 |

上述用途为文件身份和材料推断下的专用候选，不是已试听确认的真实弩弦、插箭或甲片录音。统一采样峰值不等于响度一致；插箭候选RMS明显更低，实际可辨度、噪声与混音均待听后判断。数值是采样峰值/RMS，不是dBTP/LUFS，也不是设备输出电平。

## 来源与处理依据

`manifest.json` 冻结SHA256：`0ea6f59b5bbb8cf32d9c6d6fbe45579de016974df049d558004fc59fe3d70e93`。

其中逐条保留原OGG的绝对路径/SHA、本地原ZIP路径/SHA、官网来源记录URL、原许可与本次许可副本SHA、保留的原件、原采样率双声道浮点解码、mono48k浮点、完整argv/退出码/处理日志、裁切帧、fade帧、增益、量化公式、WAV SHA及实际指标。`originals/` 保留5个原OGG，`licenses/` 保留两份明确允许商业使用、署名可选的Kenney CC0原许可。没有联网重新核官网或扩大许可证范围。

处理源码 `prepare-local-audio-v002.py` 使用现有隔离运行时FFmpeg7.1：先在原采样率解码为双声道float32，随后显式0.5L+0.5R下混为48kHz单声道float32；从0帧裁切，5ms线性渐入、20ms线性渐出，在浮点域按包络后峰值归一到−4.5dBFS，最后按 `round(sample*gain*32767)` 写PCM16。无PCM中间截幅、限幅器、拉时长或音高改动。

metalLatch当前实际FFmpeg浮点解码峰值 **+1.6153259773502702dBFS**，abs>=1样本14个，与历史审计相符；完整浮点原件保留。先保留过冲后再做下混/包络/增益，最终PCM没有过载，不是先用PCM截幅再降低音量。该数值本身不证明原录音已削波。

首次处理因未建立输出目录退出，未产生WAV；失败解码日志和当时脚本在 `provenance/` 保留，修正后成功，原件未覆盖。源准备脚本在manifest已存在时拒绝重跑；复制作新版本时须保留本版，不能覆盖已冻结WAV。

## 普通Python验证

- `tests/red-v001.log` 是首个测试路径错误，保留但不当作有效RED。
- `tests/red-v002.log` 是真实功能RED：预检返回0项，对应断言 `0 != 5`，exit1。
- `tests/green-v001.log`：18 tests通过，另含10个manifest语义拒绝子例；覆盖实际5WAV、旧17基线、PCM格式/声道/采样率/峰值/淡出端点/长度/截断/尾随字节/浮点格式，以及占用目标、registry多余/重复/缺失、假验收状态/错误许可/NaN增益/旧包/外逃路径。
- `tests/preflight-v001.log`：实际 `--validate-only` exit0；5个WAV从保留浮点→裁切→包络→增益→量化逐样本重组一致；67来源引用、20个F/E WAV副本、旧17个uasset当前基线核验。预检只读取，没有UE API或设备播放。
- `tests/float-replay-verification-v001.json`：另运行15个实际FFmpeg重放检查，5个OGG→原采样率stereo float与5个stereo float→mono48k输出SHA逐字节相等，5个最终WAV独立完整解码的帧数/峰值/RMS一致；3个Python文件AST检查通过。

## 新UE包与绑定边界

新导入器：`F:/Ourgame/tools/scripts/ue-import-first-batch-audio-v002.py`。普通预检命令：

```powershell
& F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe -X utf8 -B F:/Ourgame/tools/scripts/ue-import-first-batch-audio-v002.py --validate-only
```

根线程唯一UE执行者可在当前唯一图形Editor控制台执行：

```text
py "F:/Ourgame/tools/scripts/ue-import-first-batch-audio-v002.py"
```

目标仅 `/Game/Production/FirstBatch/v024/AudioDedicated`，5个名称为 `SW_<ID下划线>_v002`，拒绝任何现有文件/registry对象/同名资产；SoundFactory导入实际对象必须唯一且为SoundWave。逐项验证实际源采样率48000、mono、时长；记录asset sample_rate但不称设备采样率。设置/回读looping=false、volume=1、pitch=1，逐项真实保存并核非零磁盘文件与exactset。导入前/后旧v001/Audio17个实际包须保持集合与SHA一致。

Receipt为 `UnrealGame/Saved/Bootstrap/first-batch-audio-v002-import-<UTC年月日-时分秒-微秒>.json`，需 expected=actual=saved=5、success/registry_exact_set_passed/old17_unchanged=true。预检失败发生在创建receipt之前，不能用旧receipt追认；中途失败会留失败receipt及可能部分新包，必须先审查，不能盲重试或放开覆盖。

引擎入口/属性依据由独立只读代理核本机UE5.5官方源码：AssetImportTask/SoundFactory、SoundWave/SoundBase、AssetTools与EditorAssetSubsystem。此脚本本轮未在UE执行，因此未宣称5个资产已导入。

绑定提示仅建议：拉弦/插箭按真实Active Reload时长相应阶段跨越、同Action去重并受取消作废；完成声必须有实际ReloadCompleted及同Action/Instance成功资源receipt，不能预约到旧deadline就响；换甲只能来自真实成功事务提交，不能E开菜单或取消时响。没有新增取消声、资源规则、声音journal或Actor/HUD接线，不改变动作时轴。

## F/E保全

新独立主题均为 `2026-10-15_猎弩装填与换甲专用音效_v002`：F在项目 `过程图稿与视频/`，E在 `E:/OurGame/Knight/过程图稿与视频/`。每份WAV已有原件/展示副本及SHA；最终交付的处理源码、清单、许可、原始OGG/float、失败与GREEN证据另存 `final-delivery/`，保留较早准备快照而不覆盖。两盘index与verification为保全证据，仍不能当试听、公开发布、设备播放或正式内容验收。
