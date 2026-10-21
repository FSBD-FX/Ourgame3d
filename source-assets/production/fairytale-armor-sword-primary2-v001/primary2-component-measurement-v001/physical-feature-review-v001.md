2026-10-16 — Native172/173/174 第二段三甲：实际物理特征测量

事实：E221开放后，实际查看Chest、NearShoulder、FarShoulder全部18张原RGBA无重采样检视crop。124对F/E221文件共5,368,707B逐字节、大小、SHA全部一致；18个curated源均为独立512×512 RGBA，源/crop描述符全部匹配，crop逐像素等于原512对应ROI并覆盖该组件完整alpha。实际查看文件及ROI写入actual-view-log-v001.json，没有另造图或播放预览。未直接展示18张空白边较大的512文件，所见是每张源的完整可见组件原像素ROI。

事实：Chest量中央凸起圆boss的轮廓中心，避开偏右上高光；Near量中央washer内的暗孔，不拿整个肩帽中心；Far量顶皮带沿面延到右侧端的小圆铆钉。手工识别后用源RGBA的十字邻点、四侧feature rim读回确认，未从整个组件bbox推A。Chest允许±2源px，Near暗孔±1，极小且连皮带墨线的Far±2。18个孤立组件源中的指定特征均可见，故本次18项非null；这不代表171身体被遮挡的衣面附件点变得可见。

| 组件 | phase0 | phase1 | phase2 | phase3 | phase4 | phase5 |
|---|---|---|---|---|---|---|
| Chest boss ±2 | 264,260 | 266,260 | 267,260 | 270,260 | 264,260 | 264,260 |
| Near washer暗孔 ±1 | 256,261 | 257,262 | 257,260 | 254,262 | 254,261 | 256,261 |
| Far strap侧端rivet ±2 | 267,261 | 267,261 | 266,261 | 266,260 | 266,261 | 267,261 |

推理：三件有各自的构造：宽弧胸板/两顶带/中央boss，近肩圆帽与翻边/中央washer，短且压缩的远肩端面/侧端rivet。棕皮带、偏暖灰铜金属和粗墨边在行内延续。Chest相3面较窄且boss右移，Near相3/4的帽沿/面倾斜较明显；Far姿态差异更克制，主要是高度和端面压缩。相0/5接近收势视角，不能用18文件唯一或高光变化宣称六个姿势物理完全正确。

事实与边界：另实际看了已保全的Ready163 frame0及其既有crop；旧件的rivet靠画面左上顶带，新174的顶带连接到画面右侧端rivet。二者支持延续同一topstrap-rivet构造家族的候选，屏幕侧与细节位置不同，不能复制旧坐标或追认163原中央front boss要求已满足。旧失败状态保持false。Far不是新的中央face boss。

风险：这些是源组件上的可见金属feature估计，尚未平移套甲、检查盔/领/袖口/拳/剑遮挡或证明72px实际可读性。Chest3/4和Far3在171身体测量中的可见衣面A仍null；Root的三个hidden TRIAL独立保留为设计，未写回measurement-v003，也没有从这些孤立甲片推骨点或隐藏关节。feature-rim点也不构成语义分区蒙版。

标准shared-row scale保持Chest0.273224043715847、Near0.20853080568720378、Far0.13559322033898305，没有逐帧归一、缩放、重画、warp、像素修补或调整bodyTarget。标准预览600ms仍不同于内核540ms，timing_contract_passed=false。无Source、raw、frames、curated、媒体、ledger修改，无UE/UBT/import或付费生成；此目录只新增JSON、文字和freeze。穿戴适配、完整动作、连击、声音、命中/特效和完整单元均未接受。
