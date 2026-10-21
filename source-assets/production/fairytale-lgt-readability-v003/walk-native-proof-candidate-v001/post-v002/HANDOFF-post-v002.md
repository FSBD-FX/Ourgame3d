# POST v002：依赖新正常开局oracle核验工具

只将旧POST的tooling-freeze依赖改为tooling-freeze-v002.json、可选renderer改为tooling-v002同目录版本；其他48原比例crop/原帧CRC/8层3甲/来源映射/失败保留逻辑字节不变。旧post-v001与原freeze保持。此POST仍要求先用tooling-v002/verify-walk-native-proof-v001.py在同一原始实录成功重核并新建independent-walk-proof-verification-v001.json，不自行把native报告passed当独立通过，也不改首版失败日志/index。

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\fairytale-lgt-readability-v003\walk-native-proof-candidate-v001\post-v002\prepare-walk-proof-post-v001.py --archive 'F:/Ourgame/过程图稿与视频/2026-10-18_棕皮军剑双向行走与三连斩实录_v001' --version v002 --encode-video
```

若已生成v001静音MP4，请省略--encode-video，避免任何覆盖。原件/展示版/E盘保全/实际审看边界同旧POST：不调整真实帧、时间、装备或源报告；crop48张12Walk+36三刀，不缩放；导出后仍需E留存核SHA再展示，actually_viewed/墙停视觉/正式内容接受均保持false。
