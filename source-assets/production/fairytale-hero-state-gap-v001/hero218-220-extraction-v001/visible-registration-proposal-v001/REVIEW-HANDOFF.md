# 218–220：可见像素审查与安全 registration 提案

事实：E394保全后的13张512×512 curated全部已独立逐张View；实际F/E源大小和SHA先
逐项核对零差。Root也独立View全部13帧并明确认可为source-pose候选；**registration、
装备、原生试样和最终美术均未接受**。持续琥珀眼符合当前hero规则。

动作成立于可见源层：Dodge有下潜/紧缩/起身/站稳，Hurt有收缩/后仰/回身/站稳，Death
是真关节倒地与最终侧头，不是旋转一张站姿。钟盔/琥珀眼/灰炭衣/棕手套棕鞋保持身份，
无裸人脸，也没有把武器或甲烘焙进共享身体。不是native输入/碰撞/无滑步证明。

## 真实测量与提案

`visible-crown-shoe-support-glove-proposals-v001.json`保存每帧PNG/SHA、可见body core
顶点的实际RGBA、鞋/支撑ROI、alpha128底部4行的加权中心/实际边缘RGBA，以及64/128/192
阈值复核。所有点都来自当前实际RGBA；ROI由本轮全帧审看选定，不借旧身体坐标。

“crown”在本表严格指最高**可见身体/盔/顶钮**core像素，不是头骨、隐藏骨点或解剖冠顶。
鞋采用image-left/image-right可见角色，不冒认near/far骨骼脚身份。鞋支撑中点是显示根
提案，不是COM、地面物理中心或脚锁；四行底部和阈值表保留，避免只交一个无依据数字。

| 行 | 可见双鞋中点显示根X提案 | 可见body crown core Y | 支撑边缘Y提案 |
|---|---|---|---|
| Dodge0–3 | 234,216,227,247 | 56,137,93,48 | 均464 |
| Hurt0–3 | 261,277,249,258 | 88,67,81,48 | 均464 |
| Death0 | 242 | 48 | 464 |
| Death1 | 223，只是当帧双鞋支撑诊断 | 105 | 464 |
| Death2–4 | **null：不能以尸体/pile中心冒充standing root** | 197,299,308 | 可见手/膝/盔/单鞋支撑区域的最低core边缘均支持464提案 |

Dodge/Hurt的逐帧中点变化包含原standard extractor以整体bbox居中造成的注册变化。
把可见鞋支撑提案映射到同一ground，可保留身体屈伸与重心表现，减少只用默认X256产生
的横向飘移；这仍须Root实际trial确认，不自动“足锁通过”。镜像时仍是512-X配负UV一次。

Death standing-root只在frame0有双鞋支持：[242,464]。frame1虽然能测两鞋，但不能证明
它相对原standing root应如何位移；因此`standing_root_px`从frame1起全部null。frame2–4
转为膝/掌/盔/单个旋转鞋的支撑，另一鞋与原根连续关系不明，不能改用尸体重心、掌中心
或某个接触边缘回填“根”。原raw仍在，下一步由art/Root在原图上显式作者化连续standing-
root位移合同，再另记其为作者提案并trial；无需重绘现有像素，但必须公开该决定不是骨点实测。

每帧可见棕手套表面候选点均带实际RGBA与±6px作者选择不确定性，**actual Grip/Axis、
腕骨、隐藏骨、hand replay mask及甲attachment全部null**。空握表面不能推出未来柄轴。
注册±2px也是作者保守范围，不是统计置信区间。

## 尺度与装备边界

保持既有名义canvas `72*512/416 = 88.6153846154`及每行固定源尺度。Death原alpha bbox
高依次416/360/267/165/156，按同一canvas绘制自然降为约72/62.3/46.2/28.6/27显示像素。
**绝不逐帧把矮corpse放回72高**，不拉大头盔或放大手掌；当前提取无逐帧归一化，三行
各自只有一个ratio。身体/头盔的跨行实际屏幕比例与切换连续性仍需运行审看。

模块适配需要真实新遮挡数据：Dodge低姿、Hurt回弹及Death屈倒改变near arm、hand、
helmet前景和胸/双肩之间的遮挡，不能复制Ready的LGT胸肩坐标或原hand mask。共享裸衣
身体可作后续基础，不代表LGT、更不代表5武器×4甲的20套都支持。

尤其Hurt1前景手展开、Death0手放松、Death2–4手掌撑/贴地；当前像素没有证明这些手能
继续闭合握剑。若装备需保持可见，必须由art选择真正匹配的手部/独立武器姿势与遮挡；
任何视觉释放/贴地剑方案另有明确合同，不能默默产生gameplay掉落或藏掉装备。Dodge
及其他闭合手套也只测得表面，不预填不可见柄中心和轴。

最小下一步：先由Root选取Dodge/Hurt的可见支撑注册trial，再补各帧真实手与LGT专层
mask；Death先补显式连续standing-root和持物处理合同。来源与这些数据齐备后才生成
runtime profile/导入/实际Shift、poise-break、death与保存恢复试样。不会为了绕过缺口
回退静态Ready或隐藏装备。本次只写文本与测量JSON，无新标注图、Source/Content、
UE、tools、ledger写入，也没有自动trial接受。
