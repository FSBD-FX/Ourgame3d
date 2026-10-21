# 首批独立武器组件候选 v001

2026-10-15。唯一视觉writer `/root/assets_prepare`，同一master ledger `F:/Ourgame/source-assets/production/first-unit-animation-v003/generation-ledger.json`，当前累计80请求，窗口4为8/24、余16；此前EV038另24，历史累计104。没有另开累计账。外部API0，内置费用未知。

源预检见 `weapon-source-audit-v002.md`：可直接沿用的旧组件仅军剑；Kenney CC0短枪PNG为64×64三维预览，不是现圆盔手绘可组装prop；保留FBX/OBJ作结构或未来转绘参考，未启动Blender。v001审计误写64×128，旧文保留，v002以PIL实际64×64/modeP读数更正。

原生77–80各制作单独一个完整prop，生成后C工具原件保留，立即F/E原件和展示副本留存，再view审阅。工具真实输出均1254×1254，非prompt的1024；实际尺寸记录在manifest。用generate2dsprite真实processor `remove_bg_magenta(90,140)+clean_edges(3)`，随后整个方画布统一等比到512，不bbox-fit、不裁切或局部拉伸。首版alpha仍见洋红AA边，失败v001保留；v002额外删除`R>G+30且B>G+30`色键污染像素并规范透明RGB，未绘制任何可见武器像素。4张新RGBA512真alpha、角点、16F/E副本SHA、非chroma误删0、opaque洋红0通过；这不保证任何实机动画通过。

冻结合同 `manifests/import-weapon-components-v001.json`，SHA256：

`275794953add2f130f0b7912fa9e01a16c21e4e017957af4c4d9c7793c240d68`

新增4张 `components/{XBW/STF/SPR/GSW}001-neutral-component-v002.png`，表内另引用原SWD1张，五SHA互异。四件分别为可见弓臂/弦/拉栓木机弩、灯笼杖头余烬杖、细直杆叶形短枪、宽厚平齐刃尖长柄重剑。不是把同一军剑换ID。

| 武器 | primary grip | support grip | emit或tip |
|---|---|---|---|
| XBW | 128,253 | 337,282 | emit489,224；实物slot lip475,224 |
| STF | 181,251 | 282,251 | emit499,251；实物前镜492,251 |
| SPR | 137,253 | 326,253 | tip488,253 |
| GSW | 169,256 | 101,256 | tip494,256 |

坐标均手工按实际512像素测量。primary/support均落在opaque真实握柄或木杆，不能据此宣称角色第二只手已对齐。XBW/STF emit刻意在可见出口前自由空气，alpha0是正确的出口空间，不是缺图；另有opaque实体出口/镜片标记。所有prop canonical +X，图像Y向下。marker与prop必须用同一缩放/旋转/平移到演员实际手与高度，再整体镜像一次；不得默认为地面发射口或重复镜像。SPR/GSW tip仅美术几何，不改战斗射程/弱区/伤害/窗口。

静态原件、透明图、四张socket诊断图已逐张实看。第二版诊断图与已审第一版四张图SHA相同；测量JSON仅把XBW实体slot lip从透明空隙点更正到真实opaque475,224。旧版本全部保留。合同明确没有认证通用Sword body动作适配其余四件，没有自动套用同一Sword scale；长杆与灯杖可能需要更大的独立draw bounds。

当前未交付：猎弩水平提弩/放弦/收弩/1.1秒拉栓动作及weapon状态帧；法杖火球与下压火线两套动作；枪的双手直刺/三刺动作；重剑双手三段重劈与技能、重量回收。组件只解决distinct中立prop与合法物体握点，尚未构成这些武器完整制作。下一优先XBW持弩姿势、射击和拉栓，之后其他家族对应动作。

本writer未启动UE/UBT、未改Actor/HUD/碰撞/数值。运行导入与验收由root负责，当前合同为 `runtime_verified=false`、`full_weapon_actions_complete=false`。F/E保留主题分别为 `F:/Ourgame/过程图稿与视频/2026-10-15_首批独立武器组件_v001` 与 `E:/OurGame/Knight/过程图稿与视频/2026-10-15_首批独立武器组件_v001`。
