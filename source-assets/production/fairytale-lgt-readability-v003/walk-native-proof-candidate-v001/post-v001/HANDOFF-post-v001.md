# 独立POST候选

只对已经通过独立native Walk技术核验的原件工作。不启动UE，不触碰已freeze工具或Source，不改/重采样原始PNG。

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-lgt-readability-v003\walk-native-proof-candidate-v001\post-v001\prepare-walk-proof-post-v001.py --archive '<含原件/展示副本的绝对根目录>' --version v001 --encode-video
```

`--encode-video` 可省略；若此前已生成冻结工具的v001静音MP4，请省略，避免覆盖。裁图也要求新版本目录，失败保持现场。

输出：左右六相Walk共12张＋左右三段各六相共36张240×160原比例裁图，48项原帧SHA/原生CRC/实际8层与3甲/实例/attack/时间/矩形映射，一页可选原图核对HTML。实际整帧必须1280×720，因此UIScale为1；crop边界与原像素roundtrip核验，不重新放大/生成身体。

可选调用已经冻结的真实frames+offsets静音VFR MP4编码/完整解码助手。展示前Root须E盘保全所有原件、展示副本、来源/版本/状态索引并核SHA，再实际播放/逐帧审看。衍生图页默认actually_viewed=false；不以技术核验或导出代替美术/全状态验收，停墙视觉仍未录。
