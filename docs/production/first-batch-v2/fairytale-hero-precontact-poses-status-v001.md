# 暗黑童话主角前伸／推蹬姿势试样

2026-10-16，沿EV-045/046/047的卡通怪诞手绘试验，未收到新的人类需求编号。本次只是源资产推进，最新真实游戏画面仍为v054四帧待机造型试样；没有替换完整步行或宣告全套美术完成。

| 请求 | 原六相角色 | 实际审阅结果 | 后续状态 |
| --- | --- | --- | --- |
| 143 | phase2 near后趾推蹬／far前跟将落 | Root及独立实看，角色相容，前跟微小间隔 | 静态候选，未测足根／周期 |
| 144 | phase5 far后趾推蹬／near前跟将落 | 手腿角色相反，但前跟与后趾同低，过于接近接触相 | 原件保留，拒绝作为合格pre-contact |
| 145 | 定向编辑144的前跟高度 | Root及独立实看，前跟现在稍高于后支撑趾，支撑／摆臂未交换 | 静态phase5候选；全动作还需连续验证 |

145仅以144作为编辑目标、131作为唯一身份参考。使用内置image_gen；原始输出1254×1254 RGB，SHA ff0cac8f31163e32f07832422e612545ed7a9b3734b539e2dfb51cc58a1422f7。完整提示词与参考角色位于[145输入](../../../source-assets/production/fairytale-hero-v001/walk-precontact-heel-edit-inputs-v001/generation-request.json)及[prompt.txt](../../../source-assets/production/fairytale-hero-v001/walk-precontact-heel-edit-inputs-v001/prompt.txt)，131不是待输出的闲置姿态。

145经过sprite-gen自身venv、明确131 base及绿色色键、原组件提取器、项目共享fit、atlas和curated导出。源组件631×1035，统一比例0.40193236714975844，成品254×416位于512RGBA画布(129,48)，numeric QA零错误／警告。Root保全后实看[透明帧](../../../source-assets/production/fairytale-hero-v001/sprite-run-precontact-far-push-v002/curated/frame-0.png)。未本地重绘姿势、镜像伪造另一相、重排／重定时失败六帧或导入UE。静态轮廓相容不等于跨帧刚性或足滑验证，未来仍以完整连续动作与实际游戏为准。

[143/144独立审阅](fairytale-hero-precontact-143-144-independent-v001.md)与[144→145独立审阅](fairytale-hero-precontact-145-independent-v001.md)分别保留，不覆盖旧结论。首批完整内容仍0/15，20搭配及全部适用状态／反馈／正式获取／续档范围保留。

本轮输入／原稿／提取全部先F、后E保全再展示：E v080–085合计134项、28,435,756字节，源／目标大小与SHA两遍核对零差，E根README未改。原生143/144累计到window006共24次后审计冻结：121–144的23原图SHA核对，133连接失败计入请求、无伪造原图。145沿既有自动授权开window007第1/24，剩23；权威ledger145，既定累计口径169。内置费用未知，外部API调用0。
