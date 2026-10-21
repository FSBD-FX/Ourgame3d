# Native171第二段：独立剑拟合候选 v002

六张curated是171原512RGBA的完整PNG逐字节副本，没有重画、缩放、旋转、镜像、warp或移脚。nativePNG CRC/alpha/六帧唯一/最高416和来源SHA已预检；目前Production实际989包逐SHA前后不变。v009隔离磁盘路径未占用，UE registry须Root实际导入前核对；本候选没有导入/运行/编译。

导入manifest：`manifests/import-sword-primary2-v002.json`，schema `frozen-fairytale-sword-primary2-six-v2`。目标 `/Game/Production/ArtTrials/EV048/v009/HeroSwordPrimary2` 六名 `T_Fairytale_SwordPrimary2_000_v002`…`005_v002`。保留旧989包，实际registry/disk exactset、imported paths、Texture设置、save/readback均由Root执行。assets沿旧source/bytes/SHA/bbox/name/package/object格式，不把旧six-v1 importer原样调用到新manifest。

`data/DungeonFairytaleSwordPrimary2V003.inl`/同名namespace只是候选，不写Source。仅借旧FMarker类型，不借旧坐标。Find只支持sword_primary_2六相。256,464显示pivot、最高72px、Canvas72*512/416、独立剑.50及剑源Grip99,256不变。实际171棕掌候选207313/167333/281318/311253/280275/207313±3；近手polygon±4，不是完整AA ownership或已接受握柄/拇指。currentBody→独立Sword→同原UV近拳回绘仅为有限试装。

六轴原样采用Root新设计：(.94,-.341)/(.35,.937)/(.8,.6)/(.9,-.436)/(.95,-.312)/(.94,-.341)。它们不是测出的骨/柄/刃轴，不归一化偷改。相3较ArcB浅向前是避盔设计意图，未证明无重叠。相1下向轴可能把刀尖放到脚线下：沿旧约383源px前刃、.50估算tip约234,512，低于root464约48源px≈8.3展示px；这是旧tip近似的设计估算，必须实景检查，不擅自换轴。0/5与P1边界像素不同，不宣称连续fit。

75/75/60/60/135/135来自既有SWD001第二段内核；standard预览仍100×6=600ms，未重时/未通过timingQA。只有身体与独立剑的候选，本段无甲；连续动作、持剑、脚锁、音效和完整内容均未接受。所有新文件只在本family，没有新展示图或视频。
