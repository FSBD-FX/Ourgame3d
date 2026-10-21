# EV048近护腕／近护胫输入合同 v001

2026-10-16。本轮目标是保持怪诞手绘方向，在72px身体上增加灰铁块面和轮廓辨识。只准备两个真实独立组件row，不改131身体、既有147/149/150、Source或账本。root负责原生生成、E保全、提取后展示及实际UE观察；本作者没有调用图像工具或UE。

事实：root确认131四idle沿用E048，已有全套147/149/150 composite沿用E105。本作者实际查看131四张512RGBA原帧及该composite0。近手棕色腕口上缘约y298–302；近靴口斜边约y394–400。灰衣前臂和裤腿下段可用面积有限，不能为了“护腕／护胫”名称覆盖手套或靴足。

| 组件 | 独立设计窗口 | A主挂点，四帧一致 | 72px身体时窗口上限 | 本轮状态 |
| --- | --- | --- | --- | --- |
| NearBracer |34×28|[187,283]|约5.88×4.85px|已标准prepare，优先生成 |
| NearShin |36×34|[219,367]|约6.23×5.88px|已标准prepare，第一件实际贴合审后推进 |
| FarBracer |22×24|[315,296]|约3.81×4.15px|只保设计建议，未prepare、未请求生成 |
| FarShin |28×30|[288,370]|约4.85×5.19px|只保设计建议，未prepare、未请求生成 |

A是原衣服可见灰布上的独立设计挂点；每帧原RGBA采样记录在handoff，不是骨骼追踪。手足几乎静止，四帧使用同设计坐标，不捏造测得的运动根。约±2–3px语义边界歧义保留。生成件对应feature只能是**实际连接铆钉中心**，后续保全alpha后测量，再以整数平移对齐A；不能换成bbox中心、脚根或为了过门改点。没有第二个硬B挂点。

近护腕为朝下左的短宽不规则铁片，末端在棕手套腕口之前；近护胫为裤腿下段的短锥形铁片，末端在斜靴口之前。广灰面、深外沿和单个可测铆钉优先，不依赖小刻纹。窗口是生成设计上限，不能宣称实际fit已经通过，也不承诺运行时能读出铆钉。

每row4帧×167ms，512画布，standard prepare经skill ownvenv实际exit0。显式components/shared_row_scale、Lanczos、bbox-center/bottom；每条row一个共同ratio，禁止每帧重fit、warp、重画或复制四次假装动画。生成不同near/far透视不得用镜像／crop冒充；镜像只在未来运行整装围绕同pivot一次完成。

每次恰五张引用：131idle0唯一身份；131四idle contact只定姿势顺序；147/149/150实际composite只定灰铁/墨线/构造；standard4slot计数guide；新原创部位guide。146、旧失败步态或新body不加入引用。最终原稿只能四个互不连接的单侧甲片，不能包含人体、手套、靴、假连接桥或游离计数点。

新guide为原创技术块图，红A唯一主挂点，蓝轴只是方向，棕区只是保护提示，**不是131语义mask**。新图未在rootE保全前查看。当前whole131无near-arm/hand分区，只能把idle有限overlay叠合逐帧检查；不能称零碰撞或武器握持遮挡完成。后续真实分区须使用131原像素并精确重构，旧画风mask不可迁移。

最小顺序：NearBracer原生row→保全原稿→标准shared提取→保全alpha→测实际A／整数挂接→保全叠合后审四帧手套边界→固定72px左右运行观察；NearShin同样逐帧审靴口。远侧先留建议，避免3–4px细件无效调用。局部静帧适配不等于完整4甲、walk、攻击、受击、死亡、完整循环或goal验收；formal仍0/15。

实际准备路径：

- [NearBracer handoff](F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v002/handoffs/near-bracer-native-input-v001.json)，SHA3cc78d28be968f7e98e37f7df3c5b174dc9beb6faf3d27baabee4f1a067d0da0。
- [NearShin handoff](F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v002/handoffs/near-shin-native-input-v001.json)，SHA7afa52a3caa2f232e33e70bc576b10b17f29ef3b8e91f176818d084bdfc3f19b。
- 两份preparation-freeze分别列本行输入；原第一行freeze不覆盖。初版README通用“四条已prepare”句过早，已用新增preparation-status-v001.md明确纠正，实际仅两个run存在。
