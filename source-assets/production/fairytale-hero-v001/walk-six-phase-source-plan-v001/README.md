# 原六相步态来源计划 v001

仅冻结来源与数字计划，没有拼接、修改或生成任何像素，没有创建新 sprite-gen run、导入 UE 或变更 Source/ledger。新目录只含四个文本元数据文件，root 决定是否进入完整运动试验。

唯一身份：131 idle-v002 curated/frame-0.png。其他图仅提供各自的静态运动姿势。依原 numeric-walk-request-v002.json，顺序固定为：

| 原 phase | 语义 | 来源 request | 使用透明提取版本 |
| --- | --- | --- | --- |
| 0 | near_contact | 138 | sprite-run-contact-near-v001 |
| 1 | near_support_far_pass | 142 | sprite-run-passing-far-leg-edit-v002 |
| 2 | near_push_far_reach | 143 | sprite-run-precontact-near-push-v001 |
| 3 | far_contact | 137 | sprite-run-contact-far-v001 |
| 4 | far_support_near_pass | 141 | sprite-run-passing-far-support-v001 |
| 5 | far_push_near_reach | 145 | sprite-run-precontact-far-push-v002 |

source-plan.json 保存原稿、curated、各自 request/manifest/alpha report/frames manifest 的真实路径、长度、SHA；numeric-walk-request-plan-v001.json 保留原六相语义及83ms×6=498ms设计。单姿势原有1000ms/non-loop metadata没有被改写，提案也不是已经成立的运行时动画。没有加入第七/八相、重排、插值、静态平移替代或重定时。

这些单图已分别有静态候选意见，但它们没有同一次连续生成的几何约束。独立fit令当前六幅alpha高度均为416，这只说明规范化结果，不证明原始比例一致；不能把shared_row_scale标志解释为跨六个独立run共享一次scale。未来若建行，需要在新run明确记录实际像素来源/变换、逐帧身体根和足接触；bbox-center及底边464仅是放置规则，不是身体/双足根的测量结论。

主要待验：盔体刚性与上身微漂、近远髋遮挡、支撑脚滑动、143/145小尺度前跟间隙、0→1及2→3/5→0衔接、真实循环观感、左右显示和未来实际地面距离时钟。静态候选、PNG数、alpha无警告、GIF文件存在均不能单独通过这些门。root若开始试验，先保全新结果，再真实播放/录制与审查；本准备不声称完整walk或用户终批。

失败源135/136/139、140、144以及142错误色键v001不进入此来源表。129不再作为新身份输入。完整内容目标仍0/15。
