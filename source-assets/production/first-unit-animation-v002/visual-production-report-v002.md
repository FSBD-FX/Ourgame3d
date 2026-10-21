# 军剑动作纠错与四甲候选 v002

2026-10-15，EV039/040/041自动授权。单一视觉writer /root/assets_prepare。内置imagegen每批24次记账，当前0/24；host费用未知，不记免费，外部API0。v001全量冻结。

制作次序：先逐张纠正primary1/2/3为刀斩身体动作（6帧2rows×3cols，phase2/2/2），审阅/处理后再四甲基准及最需动作；甲优先完整body-atlas variants、独立武器。另抽一个独立甲overlay小样验证是否可靠。不得冒称全分层或完整换甲已完成。

双盘归档：F项目日期topic/v002 + E:/OurGame/Knight/过程图稿与视频同名目录，均原件/展示副本/索引，生成返回即保存；不覆盖旧版。

## 首个冻结军剑纠错子集

4/24调用：3个动作、18独特body PNG；另18原帧ROI像素重放patch为辅助，不算新动画帧。第2次raw有握柄残片失败，保留；第3次原生image edit去除，未用代码抹图。所有raw/processed/preview已F/E双保存。

最新冻结 import-subset-v002.json（v001保留）+assembly-markers-import-v002.json，含每帧真实PNG SHA/canvas/alpha/corners/root、实际手grip和RGBA样本、weapon角度/.40scale、原像素hand ROI patch、phase绝对时轴2/2/2。军剑3段逻辑.17/.12/.31、.15/.12/.27、.22/.12/.32原样保留。GIF仅10ms量化预览，根应读JSON，不能据GIF猜碰撞窗。P2收势剑角在独立v002由-30/-55调为-75/-80避免遮脸，源PNG不改。

P1 Root已审组装图允许候选导入；P2/P3作者逐张审图/组装候选通过，仍待Root与实机。严格processor三个动作均pass；均同.853333 source-to-output，非bbox fit。P3平均bbox高度330.3因深蹲，不把自然压身拉回354；头/肢尺度保持，面积profile drift.0263。尚无甲atlas或完全near/far分层，不标正式内容atlas通过。

冻结SHA：import-v002 0dd1b0d0579628c8c7b84d3d2ccd99d8d695faa398abc5664bc6011b3fa54748；markers-v002 78bdd628feebcf991b92c0032e69dc51050306680a31b033f0e64ec831a7e81f。

## Armor checkpoint 8/24 (2026-10-15)

LGT001 whole-body idle variant: six frames, static QC and visual candidate pass. MED001 source6 and edits7/8 retain a small gray hilt cap in every near fist. Numerical transparency/scale checks do not certify weapon-free pixels. Both bounded edits failed and all raw/processed evidence is retained; stop this correction chain and rebuild from a clean empty-hand pose. Frozen sword import-subset-v002 and assembly markers remain unchanged. Remaining requests16; external API0, host billing unknown.

## EV042 supersedes bare-face visual identity (2026-10-15)

At request18, user explicitly changed hero direction to an original enclosed round-helmet smallknight. No more naked-face armor atlases will be generated. All v002 candidates and failures are retained as technical/action references, not the new visual baseline. Frozen18 swordframes/manifests remain byte-identical; prior successful engine display remains historical technical proof only. Current24-call accounting window carries18 consumed/6 remaining into first-unit-animation-v003; no quota reset.
