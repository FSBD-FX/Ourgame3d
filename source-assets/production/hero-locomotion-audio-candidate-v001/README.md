# 钟盔轻甲：6 条移动音效本地候选

状态：已生成并通过完整解码、来源闭合和结构检查，**未试听、未导入、未绑定事件、未获 Root 接受**。

- [音色与来源计划](音色与来源计划-v001.md)
- [交接报告](交接报告-v001.md)
- `wav/`：2 脚步、1 起跳、1 轻落地、1 较重落地、1 短闪避，48 kHz mono PCM16。
- `originals/`、`licenses/`：原 OGG、原 ZIP 和 CC0 许可逐字节副本。
- `recipes-v001.json`：逐层帧级裁切、播放速度、滤波系数、延迟、增益和包络。
- `manifest.json`：全部来源、精确参数、工具版本、WAV／PCM 哈希及 false 验收边界。
- `standalone-verification-v001.json`：检查器 v002 的实际通过结果；历史 v001 失败保留。

Root 留档后才试听或展示；本目录不包含试听播放入口。以下只读检查不会播放声音（在 F:/Ourgame，使用已有 Python）：

```powershell
& ./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 ./source-assets/production/hero-locomotion-audio-candidate-v001/verify-local-locomotion-audio-v002.py
& ./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 ./source-assets/production/hero-locomotion-audio-candidate-v001/freeze-local-locomotion-audio-v001.py --verify-only
```

冻结后不重跑准备脚本，不覆盖任何成员。处理配方与脚本保留供新版本复现；本次已进行了第二次内存重渲染的全字节核对。
