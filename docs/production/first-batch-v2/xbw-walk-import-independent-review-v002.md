# XBW walk v002 独立导入审查

审查日期：2026-10-15（Asia/Shanghai）。审查者：assets_prepare。结论：**两组新导入来源、引擎回执与磁盘集合一致，66/66 通过本次只读检查；Actor/HUD 行走接线及运行外观未验收。**

## 事实与来源

本次只运行普通 Python 标准库只读检查，实际 exit0、耗时约1.3秒。读取两份 receipt、冻结 manifest、66张源 PNG 共1,588,166字节，以及 uasset 文件属性和各文件头4字节；未启动 UE/UBT，未重导、重保存或改写 Source、脚本、manifest、receipt、索引及资产。仅新增本审查文档。

| 组 | 实际回执路径（项目根相对） | expected / actual / saved | success / registry_exact_set_passed | 实际 uasset 字节 |
|---|---|---:|---|---:|
| 身体18 | `UnrealGame/Saved/Bootstrap/xbw-walk-v002-import-20261015-081700-258216.json` | 18 / 18 / 18 | true / true | 945,650 |
| 四甲48 | `UnrealGame/Saved/Bootstrap/xbw-armor-walk-v002-import-20261015-081825-243347.json` | 48 / 48 / 48 | true / true | 1,513,165 |

Receipt SHA256：

- 身体：`fb1bcbbd008e319e12d2823621e6f9af6e3c0492a781fdd2d8696fc264d14223`。
- 四甲：`99da194e1a9b807cd2f4160bde2560339182f1a911158e353cd6233ae5be9039`。

三份本次冻结来源 manifest 位于 `source-assets/production/first-batch-XBW-walk-v001/manifests/`，实际文件 SHA 与两份 receipt 均一致：

- `import-XBW-common-walk-v002.json`：`901e9e307a0654ae8c6f8385af2a9b4be94b063e06bfde2ca77cf43db1d1deab`。
- `import-XBW-walk-four-armors-v002.json`：`c14a031fbd674dadb11f4a4d363f9e65e6bac2b724e39533625f2df24f59cac2`。
- `XBW-walk-neutral-state-minus1-extension-v003.json`：`f7c0a4d77528b361208fd72185063ff64f0354a0ac222e27ebbac04bdf4678e1`。

## 实际检查

以下逐行检查身体18和四甲48，全部通过：

- 每行 `source` 绝对路径、SHA256、frame / track / armor_id 与对应冻结 v002 manifest 相符；66个唯一名称组成精确期望集合。源 PNG 实读校验完整块边界、所有 CRC、IHDR 512×512 / RGBA8 / 非交错、IEND 无尾随数据。透明范围与四角等像素记录核对 receipt；本轮未重复全图 alpha 解码，先前像素预检与本轮相同源 SHA 相衔接。
- 每行 root=[256,472]；object_path、package_path、imported_object_paths 均与固定包名和 `_v002` 纹理名精确一致。身体包 `/Game/Production/FirstBatch/v022/XBWWalk` 有18个对象；四甲包 `/Game/Production/FirstBatch/v023/XBWArmorWalk` 有48个对象。
- 两份 receipt 的 `registered_object_paths` 分别精确等于18/48期望对象，无多余、缺失或重复。独立递归枚举实际磁盘目录也分别精确等于18/48个 `.uasset`，没有其它文件。
- 66行引擎导入回执均记载实际类型 `Texture2D`、实际512×512，以及引擎设值后读回的 `TC_EDITOR_ICON`、`TMGS_NO_MIPMAPS`、`TEXTUREGROUP_UI`、NeverStream=true、sRGB=true。独立检查确认字段逐行一致；本轮未启动引擎再次载入二进制读属性，不能将这项称为独立 UE 重载验证。
- 66行 saved=true；每行实际文件路径、非零大小与 `saved_bytes` 相等，文件头符合 UE package tag `c1832a9e`。身体最小17,775 / 最大123,712字节；四甲最小20,656 / 最大48,436字节。合计2,458,815字节。本轮没有读取整个 uasset 计算新 SHA，亦未对导入前后做二进制差分。

## 推理与版本确认

实际新身体 manifest 明确 shared scale=.96、从 native raw 单次重采样；四甲 `source_body_contract_sha256` 锁定新901e…，且 `common_body` 与该身体六帧记录逐项相等。所有66个导入源 SHA 与新 manifest 相等，并逐姿态/层对照旧7185… / 35b3…：**与旧.94交付源同 frame/track 的 SHA 相等数为0**。因此本轮导入的是新.96来源，而不是沿用旧.94交付 PNG。四甲自身为 N096×inverse(O094) 的已冻结来源，不能概括成把旧.94交付图二次放大。

固定 weapon scale=.48、support gate=3.129 的来源版本未变。两份 receipt 的源预检记录通过18组 pose×state(-1/0/3)门，最大2.8255197372570726px；这是冻结来源的几何计算，不是运行中的握持或枪口验收。

三个导入脚本实际 SHA 与交付冻结值相等：

- `tools/scripts/ue-import-xbw-walk-v002.py`：`0b1fd6292fdffd9f045f2d1ec114f889d61a3468ead9860fef72a18f0d7fcd4f`。
- `tools/scripts/ue-import-xbw-armor-walk-v002.py`：`7837dc897df66f87bbb2fb46846b946e0208be56402ffdcaa7e8ef7b02b92680`。
- `tools/scripts/ue_xbw_walk_v002_checks.py`：`abc5d7173800c7a8969821c562074100eccfe16d079c0fcf52a26789b0a289a3`。

## 数量口径与风险边界

独立按实际文件名与目录核数：`Content/Production` **850个 uasset = 831个 T_ + 17个 SW_ + 2个 M_**；831个 T_ = FirstBatch826 + RoomArt3 + SceneExploration2。此次新增导入66张属于 FirstBatch826的子集，不可另加一次，也不能将850全称为纹理。T_/SW_/M_是文件名前缀口径，本轮只有新66张的 Texture2D 类型有上述引擎回执证据。

本次 receipt 的 runtime_verified、footlock_certified、full_coverage_accepted、complete20equipment_combinations、full_equipment_combinations_complete、full_weapon_actions_complete 均仍为false；canvas_refit、BodySize160_changed、movespeed_changed 也为false。当前 Actor/HUD 尚未接入该 walk 版本。本审查没有认证两处跨步 contact proxy、无滑步、躯干 bob、长袖/衣装全覆盖、双向运行装配、initial neutral 实机握持或20种装备搭配。上述状态必须由后续真实运行验证改变，导入计数通过不构成完整单元验收。
