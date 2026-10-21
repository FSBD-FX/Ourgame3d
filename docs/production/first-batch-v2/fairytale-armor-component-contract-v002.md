# EV048独立肩甲组件合同 v002（输入准备）

2026-10-16。继147四帧胸片之后，准备近肩四帧、远肩四帧；仅创建新`source-assets/production/fairytale-armor-v001/independent-limb-components-v001/`。未改147/131/146、旧素材、Source或ledger，未生成、提取、导入或运行UE。本稿不覆盖旧component-contract-v001，正式完整单元仍0/15。

## 最少可靠调用与输入角色

需要两次原生调用：near4在先，far4在后。root可用148作near，far编号由root实际执行时确定；此准备不预留ledger编号。每行只有同侧四件独立连通肩甲，与sprite-gen四frame组件提取一一对应。每pose的近/远肩互不连接，合起来实有8个组件，不能把它标签成4或用假桥连接；一张混合8件又增加两侧角色/pose索引混淆。两侧生成必须真实不同深度，不把near镜像复制成far。

引用按严格角色区分：

1. canonical131 `sprite-run-idle-v002/curated/frame-0.png`：唯一角色和风格身份。
2. 原131四pose contact：姿态/顺序0–3；不得输出body像素。
3.146整身图：仅肩甲的紧凑弧面、翻边construction；不得借其身体或暖甲色替换131/147。
4.147已保全的实际`composite-preview/frame-0.png`：仅当前胸甲灰色、墨线与已占胸口区域；其身体不成为第二身份来源。
5.标准prepare四slot guide：组件数与布局。
6.每侧原创肩甲挂点guide：深度方向及具体feature；技术蓝/紫/红/绿、标签和臂轴不得进入成品。

完整路径/真实SHA均在`native-shoulders-input-plan-v001.json`；两个完整prompt位于`prompts/near-four-idle-shoulder-v001.txt`、`prompts/far-four-idle-shoulder-v001.txt`。没有重附129或失败walk身份。

## 数值与身体挂点

两个run都用sprite-gen自己venv执行实际标准prepare，exit0；标准原输出保存在requests目录。再显式补4×167ms、components/shared_row_scale与RGB chroma字段。512cell、nativeFacing+1、loop=true；非pixel-art、Lanczos、bbox-center/bottom、ground_frames=false、绿色#00FF00，沿用默认RGB阈值及unmix4/spill.005。没有提前生成raw、atlas、curated或raw hash。

| 部位 | 组件最大窗口 | 每帧衣服mount A | 每帧lower-rim support B |
|---|---|---|---|
| near图左较宽肩 | 56×44 | 0[215,248]；1[215,246]；2[215,249]；3[215,248] | 0[202,271]；1[202,270]；2[202,272]；3[202,271] |
| far图右压缩远肩 | 32×40 | 0[296,255]；1[296,253]；2[296,256]；3[296,255] | 0[302,275]；1[302,273]；2[302,276]；3[302,275] |

这些是作者实际查看131四PNG后选择的**衣服设计挂点**；两点的真实源RGBA采样在`shoulder-component-contract-v002.json`，均alpha≥128。它们不是骨骼跟踪结果、脚根或生成件已测landmark。near约±2–3px墨线选择歧义，far被头盔/躯干遮挡，约±3px且置信度更低。窗口也是设计上限，不是已实测fit。

生成件A固定指连接于甲面内的真实圆形mount rivet中心，B固定指沿上臂方向的真实下翻边中心。生成后先量这两个同名feature；整数平移A到body A，再独立看B残差和轮廓。3px是预设审查误差界，不是当前测量通过值。不能像collar/U槽那样混同不同feature，更不能为过门更换定义。

每侧行只有一个共享比例`min(fitW/maxRawW,fitH/maxRawH,1)`；不逐帧fit。near/far两个不同窗口是透视大小合同，不假称8件共用同一scalar。只允许后续可审的整数平移、保持cropped RGBA字节；不旋转/重采样/拉伸每帧。身体显示canvas88.61538461538461、pivot[256,464]继续作为观察参数，不认证feetroot。

## 真实可见形状与遮挡

near为图左外下方向的宽圆肩，far为图右下方向的窄压缩肩。far只应露出头盔下缘以下、与实际上臂方向相容的部分，不能画完整对称肩球、头盔顶盖或跨胸横梁；完整条件另存`far-visibility-addendum-v001.md`。

当前whole131仍是一层。只有实际cap alpha完全避开头盔/颈/手时，才能空手idle叠在wholebody上观察。放在body下面全被遮住不能称“肩甲已显示”；放在上面盖住头盔也不合格。若交叉，须同131真实binary partition/源像素occluder，保原RGBA、无重复alpha并精确重构；不得移用旧body_near/armor_near mask或改旧HUD合同来迁就错误件。

未来weapon接线仍需body_far/near_arm/near_hand真实分区，weapon→nearArm→nearArmor→nearHand的关系必须按具体动作看图证明。肩甲4idle不替代护腕、护胫、walk6×83或攻击/受击/死亡/武器状态；护腕/胫也必须各自真实近远件和肢体挂点。左右显示只对整装与身体绕同pivot镜像一次，不交换near/far身份，也不以镜像制造另一件原图。

## 冻结和下一步

原26文件准备集由`preparation-freeze-v001.json`记录并保留；补充上述遮挡要求后，新`preparation-freeze-v002.json`统一列当前输入集及本合同。所有新guide/draft尚未view，等root F/E保全后审阅再由root唯一生成。后续实际QA必须检查四件真实来源、材质色保留、每帧mount/lip、遮挡、72px有无甲辨识及4→0循环；不能用component-count或0warning代替这些门。
