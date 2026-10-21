# 主角两种经过姿态试验 v002

2026-10-16，内置图像工具，沿EV045／046暗黑童话、卡通怪诞手绘与EV047“先试试呢”推进。EV040／041自动授权持续有效，外部供应商API调用0，内置费用未知。以下是静态动作候选，没有新增完整动画或UE接入。

| 请求 | 实际来源／输出 | 实看结论 |
| --- | --- | --- |
| 140 | 原单张near支撑／far经过试验，1254RGB，提取1张512RGBA | 低前抬改善，但近侧股部仍跨在前景连到抬靴，失败；保留原稿，不重新标为通过。 |
| 141 | 相反单张far支撑／near经过试验，1254RGB，提取1张512RGBA | 近侧大腿在前景向前膝／抬靴，后层腿支撑，静态角色相容。 |
| 142 | **编辑140**，131为唯一身份，附原创厚填充遮挡guide，1254RGB；v002提取1张512RGBA | 近侧前景大腿下垂站稳，后侧股根从其后、右侧向低前膝／悬空靴显露。与141可辨交换支撑／摆腿角色。上身及靴仍有生成微漂，抬靴略高于140，不能称逐像素锁定。 |

root与独立审查均实际看了142／141原图；root另看141及142最终透明帧。独立范围见 [140／141](fairytale-hero-passing-140-141-independent-v001.md)、[142](fairytale-hero-far-passing-142-independent-v001.md)。不能从两张静态图证明动作方向、速度、足锁、循环连续性或缩小后的游戏可读性。

141最终静态帧：`source-assets/production/fairytale-hero-v001/sprite-run-passing-far-support-v001/curated/frame-0.png`。142最终静态帧：`source-assets/production/fairytale-hero-v001/sprite-run-passing-far-leg-edit-v002/curated/frame-0.png`。均512×512 RGBA，未来人物可见高仍72px，当前未导入；131待机试样仍是最新真实新画风游戏画面。

142的原生完整提示词在 `passing-far-leg-edit-inputs-v001/prompts/edit-passing-far-leg.txt`，SHA `20527c33c22e32297cefcf22705da83b6bc05f436929befc4f206a6ac3e97816`。原图SHA `7bcec84667e8d4be54696af9da8c33c9ecf81a4c5ccc47aadae2e76bd56113d0`。输出采用正式sprite-gen自身venv的component去键／分离、项目共享行缩放、atlas及curated导出；installed extractor未改，未重绘／重排／重定时。533×1020组件以0.4078431373适配到217×416、位置147,48，48px安全边，数字QA零错误／警告。

第一次提取run-v001漏传显式底图与色键参数，prepare忽略JSON里对应来源而使用magenta默认键，错误地把完整1254绿色画布当成一个组件。它的数字QA虽通过，却不符合人物去键结果，已标记失败保留。另建v002明确传入131与#00FF00、恢复chroma参数后提取；没有追加图像生成。禁止把v001当成功资源。

展示前F/E六个独立批次v074–079保留原件、展示副本、提示词、状态索引及失败提取，共131文件／19,996,603字节，两遍大小与SHA零差，E根README未改。归档初始待审状态保持原样，后续判断在本报告和独立报告追加。

权威ledger142／window00622of24、剩2、累计166；下一native143。首批完整目标active、正式0/15。后续需完整同身份步态及过渡，再做实际72px双向运行检查；不能把135／136／139失败整行或137／138静态contacts重标／拼时长凑成接受。
