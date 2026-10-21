# 猎弩walk统一0.96源候选修订

本轮生成0次，未使用上一制作任务剩2次；账本仍121、窗口6为1/24，完整字节与原F/E账本快照相同。未写UE/Source、未启动UE或UBT，BodySize160与移动速度未改。

新冻结入口（旧0.94身体7185、衣层35b3和失败neutral扩展5090保留）：

| 内容 | 新冻结合同 | SHA256 |
|---|---|---|
| 6姿势×3身体层＝18PNG | `manifests/import-XBW-common-walk-v002.json` | `901e9e307a0654ae8c6f8385af2a9b4be94b063e06bfde2ca77cf43db1d1deab` |
| 4甲×6姿势×far/near＝48PNG | `manifests/import-XBW-walk-four-armors-v002.json` | `c14a031fbd674dadb11f4a4d363f9e65e6bac2b724e39533625f2df24f59cac2` |
| 同新body的neutral=-1六套socket矩阵 | `manifests/XBW-walk-neutral-state-minus1-extension-v003.json` | `f7c0a4d77528b361208fd72185063ff64f0354a0ac222e27ebbac04bdf4678e1` |

身体从117原生1536×1024稿切格、按同一既有matte处理，直接一次共享0.96缩放与原sole/proxy刚体root对齐；未读取旧0.94交付身体作重采样输入。各帧原生手点完全保留，没有移动单个marker、重画手或拉伸肢体。

118..121四甲原生稿是在旧0.94身体坐标中生成的。衣装和旧语义选区使用同一个`T=NewBodyAffine096×inverse(OldBodyAffine094)`：围绕`[256,472]`、比例`1.021276595745`的统一变换，24姿势完全相同。衣装图直接从原生raw一次重采样，旧交付衣层只用作合同/选区来源，不作图像输入；选取的每个RGBA像素与记录的新一次变换后source完全一致，不能称与未重采样raw字节相同。额外28个选区mask像素因新实际原手安全边界被去掉，身体/手本身未改，衣层与原手alpha交叉为0。

全部为512RGBA、root`[256,472]`、0.6秒6×0.1循环。绘制顺序仍`body_far→armor_far→weapon→body_support→armor_near→body_near`；旧neutral=-1、empty0、loaded3分别读自己的真实原prop标记、旋转角与0.48矩阵，不复制一套angle/pivot，不偷换initial neutral为loaded3。

| 帧0-based | neutral残差px | state0/3残差px |
|---:|---:|---:|
| 0 | 0.366916435 | 1.866596091 |
| 1 | 0.592007211 | 2.825519737 |
| 2 | 2.233512526 | 0 |
| 3 | 0.592007211 | 2.825519737 |
| 4 | 2.284701135 | 0.051188609 |
| 5 | 1.325819417 | 0.907693109 |

18个pose×state的3.129px门全部通过，门槛、组件0.48和原prop marker未改。仅源数学门通过，不能写成掌心接触/运行枪口已验收；virtualEmit仍不是CombatHeight。

真实检查见`reviews/XBW-walk-profile096-source-verification-v001.json`及同名`.log`：66PNG CRC/hash/512RGBA/alpha/透明角，18身体层精确重组，30次从原生raw独立重放，90组逐格左右单镜像，全部通过。新body三组件双向实看；四甲24姿势隔离图、neutral双向与0/3右向实看，其余左向作像素单镜像验证。源审计时F/E共3464路径/362618848字节SHA及大小零差，报告后新增副本另核；保全主题仍为`2026-10-15_猎弩真实持握步行与四甲_v001`。

两处长跨步的toe/contact proxy不升级为真实支撑脚；footlock、无滑步、躯干bob仍未认证。棕色基础衣领、腰/裙摆裂口和部分肩/腕/胫甲边界仍可见，ROB虽然是真长袖，袖口完全封闭及完整四甲覆盖仍未验收。runtime握持、20装备搭配和fullunit全部false。

UE仅建议root后续按新合同导入`/Game/Production/FirstBatch/v022/XBWWalk`、`v023/XBWArmorWalk`，Texture后缀`v002`区别旧源。本轮没有实际导入；源components的`v003/v005`是处理版本，与生成窗口数或引擎版本无关。
