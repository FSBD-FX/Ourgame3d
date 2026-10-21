# 两张相反passing单姿势输入 v001

日期：2026-10-16。仅执行2026-10-15-bound-run-capture-restore计划的Separate art task；运行时快照由其他协作者负责。本目录仅准备两单姿势，未生成最终角色像素、未提取/导入/播放/运行UE，未改Source、旧素材、ledger、进度或保全索引。

唯一身份：131 idle-v002/curated/frame-0.png，两个输入均为严格字节副本，SHA f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718。canonical此前已实际查看/留档：闭钟盔、双琥珀眼、灰黑内衣、棕手套靴、空手、固定朝右三分之四深度。技术身份锚点不等于最终用户画风/运动批准。

## 两个独立入口

- near_support_far_pass/anchor-request.json 与 prompts/passing-pose.txt：近脚掌在骨盆下支撑，远膝向右前越过支撑腿；远靴在骨盆下/略前低抬，不后踢。
- far_support_near_pass/anchor-request.json 与 prompts/passing-pose.txt：远脚掌支撑，近膝前移；近大腿在交叉处覆盖远支撑腿，近靴低抬到骨盆前/下方。

每个入口仅附本相canonical副本＋原创单相骨架guide，137/138仅为已知接触角色对照，不默认附，139及135/136失败行均不附。近/远按相机深度，不随屏幕左右改名；引导中的红近蓝远不得进入角色配色。轻微躯干/肩髋反扭可帮助看到连接，但不得改相机、钟盔体积或整体镜像。

neutral臂可以经过相同角度、未来速度方向相反；本次不会以同角度手位判错或强画拳击来制造两帧差别。两个支撑/摆腿身份必须实际相反，不能仅换标签。靴子抬到骨盆后或抬膝至腰以上都不满足本低passing题。

## 技术设计与未知实测

两个guide都从白纸原创绘制，非现有角色图的描改/裁切/调色。SVG保留设计几何，PNG是同几何的技术参考。设计站立sole基线464、摆sole442，22px低抬仅用于讲解；所有髋膝点与颜色层次都是技术设计，不能当新原稿足根、真实脚底、步幅或速度。实际生成/alpha/头盔bbox/足根字段保持null。

新guide本准备者没有view；须root按v074 F/E保全后实际查看，再独占原生生成140/141。未来原稿保存到各相raw/passing-pose.png，实际request/尺寸/SHA生成后再记录，保全后再审；不预写不存在的PNG哈希。费用/供应商调用由root，准备者不调用图像工具。

静态审查须沿两髋→膝→靴检查深度和身份，确认唯一支撑靴全掌接地、另一靴向前低抬，保持canonical身体体积、钟盔与解剖。技术文件/结构通过不是视觉通过。两相都接受后才考虑多姿势运动参考和完整六相；不能拼接/重标/重排/重定时失败139成合格动作，不能将任何单峰姿势作为完整walk唯一锚点。之后仍须实际循环、接缝、落足/步幅、镜像和UE小尺度验证。formal complete units仍0/15。

## 可复核输入

每相prep-receipt绑定其6个输入；本目录prep-receipt绑定全部14个相文件、此README与原始build-inputs.py。脚本使用sprite-gen自带venv，只字节复制canonical并从空白画技术guide，拒绝覆盖本版输出。无installed skill修改。root收到freeze后负责保全/看guide/生成，准备者至此停止视觉写入。
