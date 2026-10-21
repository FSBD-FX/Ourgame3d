# 猎弩持握步行与四甲源交付，2026-10-15

本批只完成可导入的源候选：6个新持弩身体姿势拆成18张身体层，四甲各6姿势×前后衣装2层，共48张衣层；合计66张新纹理，不能记成66个身体帧。UE、UBT、动作接线、正常输入试玩均未由本任务执行。

冻结入口：

- `manifests/import-XBW-common-walk-v001.json`，SHA256 `7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5`。
- `manifests/import-XBW-walk-four-armors-v001.json`，SHA256 `35b3a0cffc9fb731a40ff4a08cde7d5e89b5f7fceff67824feb08f31849e7ff4`。精确复用上述18张身体，不复制旧剑姿或对旧甲层拉伸。
- `manifests/XBW-walk-neutral-state-minus1-extension-v002.json`，SHA256 `50905d2632020cbc475ff6e262c9074b40afc6b6bdf818d05aac0bd4df9f54c0`。它保留旧v015原neutral组件、初始state=-1语义，不代换loaded3；其中3个支撑手拟合门失败，不能算握持验收。

统一512画布与名义root `[256,472]`；6×0.1秒、0.6秒循环只提供步态时间映射，不改游戏移动速度。新原生117身体采用一次共享`.94`缩放，再按每帧实测sole或明确的contact proxy作刚体平移。每帧完整2×3变换、原始手点、选区与来源哈希均在合同。没有逐帧bboxfit、缩放或手臂拉伸。116同侧腿重复失败稿保留。

身体绘制顺序为`body_far → weapon → body_support → body_near`；穿甲为`body_far → armor_far → weapon → body_support → armor_near → body_near`。衣层来自118..121真实同pose原生图像选区，公共原手/头/腕带与握点不动；ROB有真实长袖前臂像素，不把裸前臂孔当长期目标。仅可见背面归far，隐藏背层为null。左右统一由父级一次镜像，纹理与socket不得分别二次镜像。

state0/3组件保持`.48`，支撑手最大残差`2.113614px`。旧neutral stock/support间距与state0/3不同，按同身体、原手点和`.48`作最优刚体旋转后，六帧残差为`2.469296 / 1.530350 / 4.297005 / 1.530350 / 4.347127 / 3.408222px`；0-based第2/4/5帧超过既有`3.129px`门槛。extension明确false，未挪手点、改比例或放宽门。身体手点手测约±3原生px，统一缩放后约±2.82px；旧neutral合同未量化组件marker误差，保留null，不能借不确定性改写失败。renderer/producer以后必须读取同一实际组件state和矩阵；虚拟Emit仍是图像rail socket，不直接等于CombatHeight或ActorZ。

人工查看了公共身体两向、四甲24个pose的48个方向组装，以及衣层隔离图。衣装选区旧v001部分失败、v002误带靴像素、v003胸带误删均保留；最终v004修正了选区，纠错没有新生成。仍可见基础棕衣领口、腰/裙摆裂口、部分肩/腕安全边界；ROB袖口完整封闭、HVY胫甲全覆盖仍未验收。两个跨步帧为toe/contact proxy，不能认证footlock、无滑步或足够躯干bob。所有runtime、完整四甲覆盖、20搭配、fullweapon/fullunit门仍false。

真实源检查见`reviews/XBW-walk-source-verification-v001.json`和同名`.log`：66PNG CRC/hash/512RGBA/透明角通过；18身体层精确重建处理后源；衣层与原手alpha交集0且每个保留像素来自原生衣装图；9份旧冻结合同SHA未变；20份自有Python AST通过。审计时F/E索引内2480个保全路径、233059296字节，SHA/大小零差；这是源保全结果，不是引擎运行证明。

保全主题两处均为`2026-10-15_猎弩真实持握步行与四甲_v001`：F盘`F:/Ourgame/过程图稿与视频/`，E盘`E:/OurGame/Knight/过程图稿与视频/`，各保留原件、展示副本与index；所有新图均先双保全再查看。工具C盘原件保持不动。

本独立任务116..121请求共6/8，剩2次不使用；唯一账本累计121，窗口5在120完成24次源审计后才续窗口6，当前窗口6为1/24、pending0。外部API调用0，内置费用未知。实际窗口转换记录为`reviews/window005-request-source-audit-v001.json`与`generation-ledger-after-window005-before-request121-v001.json`；稍后生成的`generation-ledger-window005-closed-source-snapshot-v001.json`仅是含最终源审状态的关闭窗口投影，不当作原始pre121时间快照。旧Ready/Primary/Reload、armor128、Bat27、Scene2合同不覆写。
