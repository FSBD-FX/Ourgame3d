# 首件二维图集 manifest 小规格 v1

适用 `first-unit-v2`：WPN-SWD-001＋ARM-LGT-001＋ENM-STN-001。校验器 `tools/scripts/validate-content-atlas.py` 只读 JSON / 文件与真实 PNG 像素，不生成或修复图片，不启动引擎。依赖 Pillow，可使用项目 asset-gen Python 运行。它验证素材数据合同；画风、动作质量、授权真实性和玩法/运行验收仍须分别审阅。

## 执行与状态

```powershell
& 'F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe' -X utf8 -B 'F:\Ourgame\tools\scripts\validate-content-atlas.py' 'F:\Ourgame\docs\production\first-batch-v2\example-manifest.json' --root 'F:\Ourgame'
```

stdout 为结构化 JSON，`passed=true` 退出0，否则退出1；始终 `engine_executed=false`、`runtime_status=not_evaluated`。当前例子明确 `template_unfulfilled` / `placeholder=true`，文件与帧未制作，**预期退出1**。不要用测试通过或改状态字段代替正式素材完成。

## 顶层与来源

- `schema_version:1`，`profile:first-unit-v2`，`units` 恰为上述三个稳定ID。
- 正式数据候选只接受 `status:production_candidate`、`placeholder:false`；模板/原型不通过。实际帧层路径位于 prototype / placeholder / placeholders 目录时也拒绝，不能只改标志把现有原型帧报成正式图；这些源文件仍可作为新绘制的来源参考证据。
- `provenance` 是来源ID到记录的映射。每项包含 `origin`（original/third_party/derived/generated）、明确 `license`、`source_path` / `source_sha256`、`license_evidence_path` / `license_evidence_sha256`。路径均相对显式 `--root`，禁止绝对路径或越界；证据必须真实存在且字节哈希一致。工具核对证据，不作法律判断。
- generated 来源另要求真实 `provider` / `model`、保留的 `prompt_path` / `prompt_sha256`。宿主不披露底层型号时如实记 `host-managed-not-disclosed`，不冒写Gemini。供应商条款依据与用户授权范围也应保存在对应来源证据中；新输出不自动继承参考包的CC0标签。

## 两个 actor 与帧层

`actors` 恰有一个 `role:player` 和一个 `role:stone_knight`。

| actor | 必需层的最低集合 | 必需动作 |
| --- | --- | --- |
| player | body_far / armor / weapon / body_near | idle / walk / jump / fall / land / dodge / hurt / death / primary_1 / primary_2 / primary_3 / air_primary_1 / secondary |
| stone_knight | body / shield | dormant / wake / idle / walk / charge / shield_bash / recovery / hurt / death |

这是本版最低数据覆盖，新增实际状态须扩展清单和测试；不能据22个动作ID就宣称所有运行状态或22套画面已验收。空中第一段必须有明确帧层绑定，可以共享合法源部件，不凭地面动作名隐含跳跃姿态。拾取/换装/交互等实际表现与武器释放仍须在运行验收中检查，本工具不执行这些流程。

actor 包含 `canvas_px:[w,h]`、`ground_pivot_px:[x,y]`、`required_layers:[...]`、`facings`、`actions`。生产角色建议沿D12使用512×512、脚底(256,440)；工具允许≤4096的其他整数尺寸以便小测试/真实版本，要求该actor所有帧一致。脚底是地面投影锚点，跳跃时脚像素可以升高，ground_root不漂移。

player 另有 `weapon_id`、`armor_id`，及 `weapon_compatible_armors` / `armor_compatible_weapons` 两个许可列表，必须双向包含本组合。stone_knight 的 `enemy_id` 为 ENM-STN-001。

每个 action 含唯一 `id`、`duration_s`、`geometry_kind`（none/melee/body/emission）、`phases`、`frame_count`、`frames`。帧含连续 `index`、绝对 `time_s`、相同canvas/pivot、`markers_px` 和完整 `layers`。时间从0严格递增，不超过动作长度；不存在的帧、文件或任何一帧漏层都失败。所有攻击阶段至少有一个实际帧采样；三张全在前摇不能通过。这里不替画师确定最终帧数/帧率或插值质量。

单帧结构示意（这些占位字符串不是已存在的文件或有效SHA）：

```json
{
  "index": 0, "time_s": 0.0,
  "canvas_px": [512, 512], "ground_pivot_px": [256, 440],
  "markers_px": {
    "ground_root": [256, 440], "hand_near": [300, 250],
    "grip_primary": [300, 250], "weapon_tip": [430, 180]
  },
  "layers": {
    "weapon": {
      "path": "source-assets/art/first-unit-v2/REPLACE.png",
      "sha256": "REPLACE_WITH_ACTUAL_SHA256",
      "provenance_id": "REPLACE_WITH_REAL_SOURCE_ID",
      "placeholder": false,
      "baked_mirror_count": 0, "runtime_mirror_count": 0
    }
  }
}
```

真实帧还必须含 actor 声明的其余层。每份PNG必须真实解码、PNG 8-bit RGBA、尺寸等于该actor逻辑canvas，alpha须同时有透明像素和可见内容；不转换RGB、抠图或改哈希来修好输入。当前版本要求每层都有可见像素，完全隐藏/空层、trim atlas、不同尺寸的分离武器贴图或异形长武器不在本版支持范围；本例军剑导出为对齐的全画布层，原始独立剑源仍另存握柄局部坐标。

## 时间、握点与镜像

phases 为连续绝对秒 `[start_s,end_s]`，从0覆盖完整duration；不能每阶段重新从0计时。攻击需依次 windup / active / recovery，并符合当前基础源时长：

| 动作 | 前摇 / 有效 / 恢复（秒） |
| --- | --- |
| primary_1、air_primary_1 | .17 / .12 / .31 |
| primary_2 | .15 / .12 / .27 |
| primary_3 | .22 / .12 / .32 |
| secondary | .20 / .10 / .38 |
| charge | .90 / .80 / 1.60 |
| shield_bash | .70 / .12 / .90 |

来源为本目录 combo-spec v2、旧军剑武器技和D05沉石骑士；profile固定这些基础制作时轴，装备速度变化由运行逻辑重映射，不用PNG帧触发真实命中。普通状态同样须合法连续phase，但工具不替代其游戏规则时长验证。

所有帧必须有ground_root；player需hand_near / grip_primary / weapon_tip，主握柄与近手误差≤1源像素；stone_knight需shield_contact。emission动作另需emitter_primary。所有点是逻辑canvas像素坐标，须有限且在canvas内；不据画面标记改动游戏射程或发射原点。

`facings` 当前只支持对称部件的canonical right＋一次父级镜像：

```json
{
  "right": {"source_facing": "right", "baked_mirror_count": 0, "runtime_mirror_count": 0},
  "left":  {"source_facing": "right", "baked_mirror_count": 0, "runtime_mirror_count": 1}
}
```

每层自身两个mirror_count均为0，握点/装备层跟随同一父级变换，不再独立翻第二次。不对世界Y、跳跃Z或事件序号镜像。工具校验声明，不能从一张PNG自动识别它是否已被偷偷翻转，也不验证运行shader/骨架真正只执行一次。非对称装备与专门左向绘制需要后续明确升级schema，不能套用此版通过声明。

## 测试范围

测试使用临时目录的真实小PNG与真实字节哈希，覆盖坏文件、RGB、全不透明/全透明、尺寸/脚底漂移、缺动作/帧/层、阶段重置/缺阶段采样、错握点/emit点、镜像重复、左右与装备不兼容、来源/授权证据、占位与路径越界。只读性测试核对输入PNG、许可、manifest字节及文件集合均未改变。

人工画风/像素边缘叠底、动作是否真的不同、石像与轻甲识别、左右遮挡、运行坐标、游戏判定、音频试听和完整内容八项验收，均不在这个离线校验器的通过结论内。
