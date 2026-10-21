# Native169第二段：Root导入/独立剑拟合候选

六张curated是原169标准512RGBA的逐字节副本；未重画、缩放、移脚、镜像或warp。真实PNG CRC/alpha/六帧唯一/最高416及来源SHA均已只读预检。只检查了新namespace磁盘未占用，**UE registry仍须Root实际核对**；没有导入、运行、编译或验收。

导入入口数据为`manifests/import-sword-primary2-v001.json`，沿现有body-v002的assets格式：source/source_bytes/source_sha256/source_bbox/name/package_path/object_path。Root新checks应固定schema、namespace、六项顺序和manifest SHA，复用原nativePNG decoder，保留旧983包、registry/disk exactset、save/readback和Texture设置门；不得调用原ten-v2 importer硬套六项。导入工具可接受`--manifest <绝对manifest路径> --expected-manifest-sha256 <本次SHA> --require-unused --validate-only`方案，实际入口由Root另写；这些参数不是已存在的CLI。

`data/DungeonFairytaleSwordPrimary2V001.inl`只是静态候选，尚未写入Source。仅借V001的FMarker类型，不借旧人类/旧姿势坐标；Find仅支持sword_primary_2六相。Root/pivot256464、Canvas72*512/416、SwordScale.50、剑源Grip99256不变。近掌六候选224318/252274/358277/345277/250301/224318来自实测可见手套，±3–4px；手轮廓±4px不是完整ownership或thumb mask。六刃轴来自原v002输入设计，p2明确[.98,.20]，不采用measurement另提[1,0]；实际刃轴/握柄/拇指仍null、未接受。

75/75/60/60/135/135ms来自现有SWD001 Stage1内核；原standard atlas/GIF仍100×6ms，timing QA没有通过，也没有改图或retime。未来须用真实J连击触发第二段及GetPrimaryPoseFrame，不改变内核/输入/clock；当前只为独立剑拟合，不适配Ready或Primary1甲、不宣称连续运动、足锁、音效或完整内容。
