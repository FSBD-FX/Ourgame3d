# LGT 软皮待机三行准备（候选，未生成）

2026-10-16，scale_tests。仅在本目录写入；ActualSource、工具根、原素材、账本及媒体目录未修改。

事实：正式 ARM-LGT-001“行路短衣”设计为褐色腰长皮衣、软肩、小布包（03-防具.md:41）。已留档 native179 只提供新的衣物身份/材质，不替换131共同身体。姿态仍是158四张Ready原512源；当前72px、Root256464、单父镜像不变。旧161/162/163及后九行的灰金属组件仅作透视/动作形变来源，禁止当皮甲身份。

三个新标准 component-row run 已分别 prepare exit0。每行四帧，request 显式4×167ms，共用行缩比；没有raw生成、提取、导入或UE运行。每份精简提示词少于800英文词、准确五参考，来源与SHA见 handoff。标准生成的14KB通用模板仍完整保留，实际候选使用prompts目录的精简 isolated-component 文本。

| 行 | 提取设计上限（source px） | 本次设计约束 |
| --- | --- | --- |
| Chest | 90×90 | 腰长软皮短衣与单小包连接为同层；衣领低于盔，衣摆到腰带／上胯附近，不压膝；完整近袖与手套在前 |
| NearShoulder | 60×44 | 短软肩外扩轮廓，上限不是必须填满；不延伸到肘、护腕或手，不变硬方肩 |
| FarShoulder | 30×28 | 真正更短、更压缩的远侧片，不镜像近肩；保持暗关节及颈／远手间隙 |

90×90不是已测皮衣尺寸。Ready衣面设计候选沿既有实际可见灰布位置；Chest窗口中心仅在旧衣面候选下移7 sourcepx，使窗口覆盖领口下至腰附近。窗口矩形不是轮廓mask或允许盖住身体的区域。90px约15.6屏幕px，仅说明同72px比例下的设计上限，不证明整景可读性。肩窗沿旧上限保守保留，实际新皮片需比旧金属更软短。未来front clasp／肩缝feature A全部null，现有布面点是附件设计±3–5px，不是骨点、新部件实测A或隐藏关节。

完整十二行索引逐项绑定旧raw/request/shared-row比例、fittedcurated、实际registered当前纹理及对应Ready/P1/P2/P3身体。后九行只有索引，未建新run。旧金属70×50胸窗不能沿用为新腰长皮衣的形状标准。

准备验证：实际3次SG exit0，独立重读210个pin无size/SHA差；3份新request、五参考、4×167ms、单行共享比例和empty raw均已核。SG实际venv Python3.14.6/Pillow12.3.0/NumPy2.5.2；技能版本与所有工具源码SHA另有 toolchain-provenance。准备脚本先前的本机工具文件名及state durations遗漏、watcher dict alias诊断均保存在logs；前者发生在SG调用前，durations/chroma为标准输出后显式项目字段，standard before原件与字段差异保留，最后source假差异已独立按文件三字段核清。不据一次总脚本退出码掩盖这些过程。

风险／下一步：新guide和standardlayout尚未显式查看，须Root先F/E留档再审。胸衣较大，领口／腰带／前臂交界和皮包归属要靠真实输出及分层试装确认；当前BodyRest包含躯干头腿、NearArm跨肘，三行准备不会解决完整hidden关节cutout、locomotion或20搭配。future feature A实测后才可整数注册，不能bboxcenter替A。原preview按fps且GIF量化，不能证明精确167ms；未播放或重定时。generation_ready=false／Root审批必需；正式完整0/15，无动作／装备／运动接受。
