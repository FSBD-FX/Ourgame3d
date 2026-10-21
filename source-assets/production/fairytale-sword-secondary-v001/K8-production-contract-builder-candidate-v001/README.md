# K8 真实生产合同 builder v001

此 NEW 目录只生产 source 数据与 runtime 整值投影，未修改实际 Source/Content/tools/E/status/ledger，未 View/生图/启动 UE。Root 已明确给出 K5 A 与八帧 marker，并授权生成这里的实际候选包；**不是素材自动选择器，也不导入 Texture。**

## 实际产物

`output/source-contract-package-v001/` 包含：

- `source-contract-v001.json`：56 行已核真实 source PNG/pins/完整 RGBA SHA、alpha bounds/Root、owner masks/canonical body 重构、八帧 Root/Grip/Axis、冻结父来源与明确 provenance。
- `texture-import-manifest-v001.json`：真实56个新 phase Texture2D 目标及完整 source pins，`replace_existing=false`；固定 settings 为 **TC_EDITOR_ICON / TMGS_NO_MIPMAPS / TEXTUREGROUP_UI / TF_BILINEAR / never_stream=true / srgb=true**。沿既有实际纹理导入约定，绝不使用 srgb=false。
- `profile-whole-value-v001.inl` 与 `projected/.../DungeonFairytaleSwordSecondaryPresentationV001.cpp`：按原真实 FProfile/FFrame/FLayer/FSourcePin 类型填满整个 Profile 值；投影只替换原 Profile() 整函数，逆变换证明其余 runtime 字节不变。**RuntimeReady=false**，metadata complete 不等于 source 已准入或 Content 已导入。
- `package-receipt-v001.json`：上述有限结果、真实 baseline pins 和 false admission/native/final 边界。

SourceContract 先按 UTF-8、sort_keys、indent2、末尾 LF 生成实际 bytes，再计算 SHA256；之后仅 manifest、Profile 和 receipt 引用该 digest。SourceContract 内不纳入自己的 hash，也不把 CPP/manifest 反向放入父闭包，避免自循环。

56 个新目标统一为 `/Game/Production/ArtTrials/SWDSecondary/v001/T_SWD001_K_{Owner}_{Frame:02d}_v001`，object path 为 package+`.`+同名 asset。owner 次序：BodyRest、ShoulderFar、Chest、NearArmWithoutHand、ShoulderNear、HelmetForeground、NearHand。独立剑是已有军剑 object/source，pivot99,256 / scale.50，不在 textures 导入队列。

**K6 只复用 K0 source，不复用目标 uasset。** K6 每个 phase06 包都独立；K7 canonical Ready 源也有独立 phase07 包。故 K logical 57 = distinct UE object paths57；distinct PNG sources 是50（56条中49个源，加剑1）。不要按 PNG 源去重成50个 UE assets。若 retained Ready24 仍用旧对象路径，真实 K57+Ready24 union 为81个对象；实际原生观察器仍应按 object path 核清。

## 固定来源与 Root 输入

`source-locks-v001.json` 锁定 body0..3=821b2526 / armor0..3=42454985；body4/7=f149cd1f / armor4/5/7=a686aaec；body5=08185a5d；K5近肩仅可来自 NEW整数fit v003 A/B（父3e341eda），实际 Root选择A；K6明确source alias0。K5 Far/Chest保持a686的K5文件，只有 NearShoulder 从 Root choice 选入。

参数必须包含真实 markers JSON、choice JSON、chosen shoulder PNG 各自的 path/bytes/SHA256；Root marker schema为 `Root-K8-source-fit-markers-approved-for-first-native-trial-v001`，frames0..7每行有 Root/Grip/Axis/source_body/source_near_hand/body_owner_freeze。Root choice schema为 `Root-K5-integer-near-shoulder-choice-v001`。逐项核 Root审批字段、全部八帧、真实手部 alpha>=128 的 Grip、有限归一化 Axis、Root256/464、512 RGBA/footline464、每帧四 body owners 全 RGBA+onehot mask 重构及源冻结 membership；不静默归一化/平移/重画任何图片。

Root已提供 markers10982B/b037b961...、choice1611B/d068f1c3...、A PNG6569B/c5f42b2c...。Root后续全部 LGT 试装决定为 `Root-K8-binding-decisions-v001/Root-LGT8-native-trial-assembly-choice-v001.json`，1174B/SHA af7dfe043b2ed3a1b5dbfdd56faa83ed116b152a45aefa8fc4fc1ead49323d95；来源未变，因此只在这里记录，不给已生成合同增加循环或额外依赖。

## 运行

工作目录 F:/Ourgame。完整真实 argv 已保存在 `reports/actual-builder-argv-v001.json`，可在其末尾加 `--validate-only` 原样复验现有包；该模式只读，也逐文件核已存在的包，不会重写它。

```powershell
./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 source-assets/production/fairytale-sword-secondary-v001/K8-production-contract-builder-candidate-v001/build-K8-production-contract-v001.py --help
```

所有参数均必需：`--markers --markers-bytes --markers-sha256 --k5-choice --k5-choice-bytes --k5-choice-sha256 --chosen-k5-near-shoulder --chosen-k5-near-shoulder-bytes --chosen-k5-near-shoulder-sha256 --output`。`--output` 必须位于本 NEW 目录内；非 validate 模式必须尚不存在。输出前完成全部输入、来源/层/marker/pin 检查；缺任何一项、pin不符、缺层/错尺寸/错源、旧包碰撞即失败，不创建最终包。写入使用同父目录 pending staging、完整文件 flush 后 Windows rename；失败 staging保留，绝不覆盖旧包。

## 验证与边界

仅五项必要 schema/pin 检查：真实Root输入得到56目标/K6语义、缺chosen、chosen错SHA、markers错SHA、缺K7marker；初始stub RED0/5，完成后 GREEN5/0。一次真实 MSVC /std:c++17 /W4 /WX 编译生成的整值，使用原 runtime Plan 与实际 WA 类型：56条layer+1剑完整，RuntimeReady=false、ProfileValid=false（该运行门按设计未开启）。这不是 UE/UHT 或 native 编译/运行。冻结后可执行已 pin 的 host exe；如需重编译应在 NEW 输出目录，不能覆盖冻结的 obj/exe。初次 compiler 环境入口路径失败和改正保留在 reports，未掩盖为游戏结果。

真实命令先 `--validate-only` exit0，再生成实际包 exit0；原 SourceContract和manifest pins已独立重读，全部56 source pins、56目标名、SRGB true/K6 alias/剑不导入已核对。导入前 current CM 锁为 v147-SWDStepAudio303-1439-203GREEN-v001（ae00569b...），当前 Source303 / Content1439 /203GREEN。预期仅此56资源导入后 Content1495，必须以 Root真实import receipt与实际核计为准，工具从不篡改旧1439。

接下来由独立 reviewer 审阅此实际包与 importer，Root真实导入并取得56 Texture2D、class512、settings/source/uasset原件 receipts。只有真实 ContentReceipt及后续源码准入时才可另行生成/冻结 RuntimeReady=true 的实际整值版本，并验证 AllResident57、真正 K8 draw/pixels/左右/原Endjoin/音画；当前 false 门不能单独翻 true 冒充已导入。首次 source-fit批准不等于握柄解剖、动画、运行镜像、听感或正式首单元验收。
