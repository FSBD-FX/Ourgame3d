# 六相 v008 原画布横向登记独立短审

2026-10-16。E088保全确认后，实际逐张view六张 `sprite-run-walk-v008/curated/frame-0..5.png`，与已看v005比较。仅新增本报告，没有改图/Source/脚本/ledger、生成、提取或UE导入；没有播放GIF/IAB动画，不判motion通过。

结论：**本次机械X登记达到预定对照目的，可保留v008进入真实循环观察。** 钟盔/上身静态横向位置比v005一致，2/3不再被bbox-center额外拉向左侧，5→0的横向回跳也明显减小。原腿角色、近手轨迹、靴形和纵向位置保留，未用改姿势或缩放制造稳定。

## 独立数值核对

读取现有两版curated的alpha bbox，分别取其内部RGBA字节比较：**6/6完整cropped RGBA逐字相等**，包括半透明边缘RGB和alpha；Y上下界6/6相同。manifest保存的原native component SHA也6/6对应v005，本审没有重新运行key/extract。

| frame | v005→v008 X整数位移 | v008实际alpha bbox | 实际盔tan-core中心X |
| --- | ---: | --- | ---: |
| 0 | −3 | [122,48,384,464] | 257.5 |
| 1 | 0 | [149,57,362,464] | 257.5 |
| 2 | +9 | [137,53,393,464] | 257 |
| 3 | +5 | [138,54,384,464] | 257 |
| 4 | +5 | [157,56,364,464] | 257 |
| 5 | +4 | [134,51,386,464] | 256 |

同v005报告的只读色域/alpha方法，实际中心跨度从12.5变为**1.5px/512**，不是再沿头部逐帧追踪对齐。它是原1254-cell统一映射的结果，仍保留原稿与整数round的小差异；不能把cell中心256宣布为身体/脚的真root。

实际shared ratio仍416/1043，六幅高度仍416/407/411/410/408/413，时序仍83ms×6。native frames/atlas QA均0错0警告。request明确opt-in `project_horizontal_registration=native_source_cell_x`，manifest对应 `horizontal_registration=native_source_cell`，并保存每帧native source bbox/cell size/placement；基础native `fit.align_x=bbox-center`是默认合同字段，实际项目覆写已单独记录，没有隐去policy变化。

## 原动作问题仍待播放

原RGBA内容完全相同，意味着v005已指出的passing下沉、两侧抬靴差、1→2/3→4大手快速换位、5→0鞋头/袖口/盔面微漂也完整保留。当前六帧静态的near/far身份继续可追踪，无新增缺肢或衣物变化，但这不证明脚接触稳定、连贯走路、loop seam或小尺度/左右显示已经通过。原83ms引擎节奏与GIF量化节奏也不能混为一谈。

失败v006/v007与v005基线保持原件，v008没有经post-affine composer再次采样边缘；cropped RGBA相同是本审实际读像素的证据。下一步应在已保全的v008真正播放多圈并检查小角色显示；root打开HTTP/IAB页面本身不构成本审的实际播放记录。

## 冻结依据

目录：`F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-walk-v008`。

- request SHA：`d541f7c2738d444ec3599de9d1ef6de8b5b214a670bfdbc2ef9f5353fd467309`
- frames manifest SHA：`d9ff79d283cee80608aa33989cf4433b481882f55995c9b812144d2d3cf41f85`
- atlas manifest SHA：`3bba330b18f6a588290f7a78a0e4babea110c55f2f18d2771d1e749b4f5099ae`
- contact SHA：`a324d132aa567f432ebfb3e00b8148d1df6952596386fbbb5445144115818e21`（本轮未打开此contact，实际看六curated）
- GIF SHA：`d42df59955e276fae2c0d0f053ec11ce76bf74273d53a7bc07910a76b23ddb9c`（未播放）

本审只认证机械登记对照与静态观察的上述事实；没有正式sprite/完整walk/UE运行/用户终批或内容单元完成。目标仍0/15。
