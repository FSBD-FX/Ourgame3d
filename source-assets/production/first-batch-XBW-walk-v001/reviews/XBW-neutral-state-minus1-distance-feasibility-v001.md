# 固定0.48的猎弩握点可行性诊断

结论：**长度约束存在共同解，当前冻结walk第2/4/5帧不在共同区间内。** 这不能证明旧neutral marker画错，也不能靠放宽门槛或挪marker修复。若额外要求neutral与state0/3使用完全相同的原图旋转角，则在当前标记下无共同解；组件自己的握点方向必须进入各自矩阵。

本次只读原图/冻结合同并计算，新增本md和同名json。未生成图、未改7185身体/35b3衣层、原prop、生命周期、账本或UE/Source。

## 事实与来源

所有组件画布512RGBA，以下原图握点均采到alpha255。坐标和SHA来自原冻结合同，不从prompt猜测。

| 组件 | Stock | Support | 向量 | 原图长度 | 原图握点方向 | 乘0.48后的长度 |
|---|---|---|---|---:|---:|---:|
| initial neutral -1 | [128,253] | [337,282] | [209,29] | 211.002369655 | 7.899691614° | 101.281137434 |
| state0 | [138,308] | [344,320] | [206,12] | 206.349218559 | 3.333850662° | 99.047624908 |
| state3 | [138,274] | [344,286] | [206,12] | 206.349218559 | 3.333850662° | 99.047624908 |

- 旧neutral：[import-weapon-components-v001.json](F:/Ourgame/source-assets/production/first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json)，SHA `275794953add2f130f0b7912fa9e01a16c21e4e017957af4c4d9c7793c240d68`；实际PNG `4cc4386d51df9e4c12c8db23155c1ebb3c318a087fcc8c68e9c2ed72898e3109`。
- state0/3：[weapon-state-lifecycle-v001.json](F:/Ourgame/source-assets/production/first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json)，SHA `94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe`。两个PNG SHA和采样RGBA完整列在同名json。
- 当前walk：[import-XBW-common-walk-v001.json](F:/Ourgame/source-assets/production/first-batch-XBW-walk-v001/manifests/import-XBW-common-walk-v001.json)，SHA `7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5`，共享身体比例0.94。
- 失败扩展：[neutral extension v002](F:/Ourgame/source-assets/production/first-batch-XBW-walk-v001/manifests/XBW-walk-neutral-state-minus1-extension-v002.json)，SHA `50905d2632020cbc475ff6e262c9074b40afc6b6bdf818d05aac0bd4df9f54c0`，固定组件0.48、原门3.129px，均未修改。

## 推理与复算

沿用现有合同：stock精确落到body主手点，主手误差0；各组件用自己的stock→support方向对齐同一个body手点方向；组件只能刚体旋转/平移且比例固定0.48。设body手距为`D`，组件原握点距为`L`，最小支撑手残差为`abs(D - 0.48*L)`。不能把主手和支撑手的误差平摊，借此换成另一种更宽松的合同。

- neutral允许手距：`[98.152137434,104.410137434]px`。
- state0/3允许手距：`[95.918624908,102.176624908]px`。
- 共同区间：**`[98.152137434,102.176624908]px`**，宽`4.024487474px`，非空。
- 例如共同手距`100.164381171px`时，两种长度的最优残差各`1.116756263px`。因此不能说“0.48下两组件长度必然不兼容”。

| 帧（0-based） | 当前冻结手距 | neutral残差 | state0/3残差 | 共同区间 | 到区间下限短缺 |
|---:|---:|---:|---:|---|---:|
| 0 | 98.811841 | 2.469296 | 0.235784 | 内 | 0 |
| 1 | 99.750787 | 1.530350 | 0.703163 | 内 | 0 |
| 2 | 96.984133 | **4.297005** | 2.063492 | 外 | 1.168005 |
| 3 | 99.750787 | 1.530350 | 0.703163 | 内 | 0 |
| 4 | 96.934011 | **4.347127** | 2.113614 | 外 | 1.218127 |
| 5 | 97.872916 | **3.408222** | 1.174709 | 外 | 0.279222 |

第三种容易混淆的前提是“所有组件用完全相同原图angle”。neutral与state0/3原向量差`[3,17]`，乘0.48后为`[1.44,8.16]`，两个support端点相距`8.286084721px`，大于两个3.129误差圆相交所需的`6.258px`。所以同stock+同原图angle无法通过；正确的独立旋转差为`4.565840953°`，这来自源组件握点方向差，不能复用一套pivot/angle冒充相同组件。

另一个未执行的纯算术结果：以原生117六帧手距为输入，若未来另建一个统一身体比例，所有6帧共同可行的比例区间是`[0.951812565,0.962859842]`，中点约`0.957336203`。当前0.94在区间外。这仅证明新共享profile有算术路径；改变身体比例会牵动整套衣层、root、markers与运行呈现，不能局部放大手臂，也不是本任务授权修改冻结稿的依据。

## 语义与风险边界

已实看neutral原PNG及其已保全标记图、state0/3原标记图。neutral stock点在皮革包裹的枪托颈部，support点在下方独立前握把；它们不是水平弩身/rail中线。state0和3的34px画布偏移被各自stock/socket吸收，二者向量确实相同；旧neutral是另一张独立生成的设计，接触向量的长度和原图角度均不同。

body点是侧向闭拳可见部分的手测中心/握持proxy，不能从alpha或皮肤色块证明被遮住的掌心到木柄内部接触轴。原手点手测约±3原生px（0.94后约±2.82px），并非统计置信边界。旧neutral合同没有数值化marker误差，继续为null。原点不透明只证明落在真实木材像素内，不证明选中了唯一正确的掌心接触中心；目前没有证据判定旧marker错误，也没有证据允许按过门需要搬它。

建议先独立核Ready/Primary/Walk中“可见拳中心”与“实际木柄接触轴”的同一语义。如果原接触位仍合理，再由root选择明确新共享profile或同一结构武器状态修订；保持当前身体/甲/prop/门槛冻结。无论选哪条，需重新验证组件状态矩阵、双向遮挡及运行握持。此次`neutral_grip_accepted/runtime/fullweapon/footlock`均不改变，生成0次，外部API0。
