# 猎弩四甲固定姿态衣装层候选 v001

2026-10-15，Asia/Shanghai。唯一美术写入者 `/root/assets_prepare`。本批12/12次内置生成已停止，没有额外重抽；外部API调用0，内置费用未知。此报告交付源资产与复核边界，不代替运行验收。

初始总账103/window5使用7/24、余17、pending0；本次请求104..115各先登记后调用，现总账115/window5使用19/24、余5、pending0。后续窗口的自动授权不用于突破本任务12次上限。

| 冻结候选 | 新衣装PNG | 原身体文件引用复用 | 合同SHA256 |
| --- | ---: | ---: | --- |
| Primary6 × LGT/MED/HVY/ROB | 48 | 18 | `0acc811b8633f8d3b165ea588ad38c8f95372f4bd13ab37ec7ece7174ecc0a82` |
| Reload4 × LGT/MED/HVY/ROB | 32 | 12 | `963d74e304894088492b205fb9b113b0e5b6d9acf52785724c6d400271722002` |
| ReadyIdle6 × LGT/MED/HVY/ROB | 48 | 18 | `093d6b15a44dadc485b28584784c888b2df7f1a88261891632ef836e128925a1` |

合同均在 `F:/Ourgame/source-assets/production/first-batch-XBW-armor-layers-v001/manifests/`：`import-XBW-primary-four-armors-v001.json`、`import-XBW-reload-four-armors-v001.json`、`import-XBW-ready_idle-four-armors-v001.json`。Schema=`frozen-XBW-pose-armor-layer-subset-v1`，均 `frozen:true`，`runtime_verified:false`，完整护甲覆盖验收仍为false。128是衣装层PNG数量，64是四甲×16源姿态的组合数；不是128新身体帧、128动作或64独立角色。身体文件内容去重数另见实际审计。

来源路线：以已冻结猎弩Ready21c8…、Primary79fd…、Reload9a0f…的真实身体像素制作同坐标参考版；每甲/每clip单独原生衣装编辑，未变形旧Sword衣层代替。生成原图保留完整身体，交付层仅取人工可审的现有衣装像素。没有代码绘制衣装、手、头或隐藏背面；RGB仍来自处理后原稿，二值mask只作取舍。不可将全身生成原图直接当可换甲交付。

实际绘制顺序固定为 `body_far → armor_far → independent_weapon → body_support → armor_near → body_near`。`armor_far`包含实际可见胸/远肩袖/后摆/甲胫；`armor_near`是实际近肩和衣袖，位于武器之后、冻结原近手之前。原头、近手、支持手、短腕、腰带和包通过保护选区排除；不存在“整条裸臂在body_near最后重盖全部长袖”的交付方式。隐藏背面明确null，不伪造非空图层。原手点、Root `[256,472]`、武器矩阵、实际时轴保持原合同。

Primary104..107和ReadyIdle112..115实际原图1536×1024，原生512格切分。Reload108..111实际原图1254方图，第一次严格1024预检真实失败并保留报错；随后只做整张图统一 `1024/1254` 归一，未逐帧平移、缩放或bbox-fit。处理使用generate2dsprite现成色键/边缘函数；全部12份原稿非chroma误删像素为0。局部chroma残边和蓝护腕误选通过新版本选区处理，原候选保留，无额外生成。

最终选区：Primary用v003；Reload短袖三甲用v003，ROB用v002的真实长袖，避免v003过宽护腕保护把真实长袖挖掉；ReadyIdle用v001。每份最终组合均实际查看isolated、右向和逐格单次镜像左向图，F/E保全后才查看。静态预览仍使用各自原冻结独立武器配置，运行端切换新weapon-state时必须显式使用新矩阵，不能以预览代替状态交接测试。

尚未通过的视觉部分：共享身体仍烘焙旧褐内衣，并非裸base；旧领口、腰边、开片和肩/腕边部分仍可露出。ROB源稿有真正长袖和长开片，但保护原腕/手的安全边距仍留下少量旧肌肤或内袖楔形，不能称完全封闭袖口。短袖三甲有意复用原裸前臂，不把该策略套给ROB。LGT与基础皮衣近色、环甲肩袖局部过渡、板甲肩和旧内衣交界仍需真实显示比例审阅。没有声称护甲全状态、20搭配、左右接地/遮挡、武器机械释放或动作衔接已完成。

追加零生成复用合同：`F:/Ourgame/source-assets/production/first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json`，SHA `94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe`。4原武器PNG不改：state0/1 stock `[138,308]`，state2/3 `[138,274]`；共同stock→support `[206,12]`、stock→虚拟Emit `[368,-45]`。固定.48、stock精确对齐原手后，support仍有约1.972..3.129源身体像素残差，不能拉伸身体消除。旧neutral `[128,253]`不能用在新状态。虚拟Emit原像素alpha分别255/2/13/0；state3可见箭尖约 `[483,205]`，与虚拟轨出口Y229存在24源像素高度差，未宣称机械直线或世界枪口已证。实际Ammo、发射、ReloadComplete仍唯一由Actor/kernel提交，renderer与producer须读同一state/矩阵。

留存：F/E均为 `2026-10-15_猎弩四甲分层动作适配_v001`，有原件、展示副本、index及总账快照；交付128层对应512份副本，12次请求C工具原件/规范raw/F-E共72路径。源稿、处理版本、失败选区、mask、提示词与脚本均保留。生成素材不标CC0，也不把工具MIT许可当作作品许可。

本任务没有UE/UBT/Blender运行、导入、Source/HUD/README/progress/台账变更。原猎弩三份合同、Reload16、石蝠27-v002与Scene2合同保持冻结；主线程独立导入和实际穿戴证明才可追加运行结论。
