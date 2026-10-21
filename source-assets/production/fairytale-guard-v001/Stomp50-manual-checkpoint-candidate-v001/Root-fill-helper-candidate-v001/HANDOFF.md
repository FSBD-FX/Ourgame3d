# Root fill helper candidate v001 — not executed

只新增本子目录。原manual freeze f93bbb的11成员保持原字节。脚本未运行，未创建Root checkpoint，未启动UE/build/import，未写实际Source/Content/tools/.cmd。

Root使用实际参数运行：

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-guard-v001/Stomp50-manual-checkpoint-candidate-v001/Root-fill-helper-candidate-v001/prepare-Root-Stomp1332-checkpoint-v001.py' --snapshot '<fresh193 snapshot directory>' --full-suite '<same actual full193 index.json>' --source-rows '<Root-GuardStomp6-preimport-source-rows-v001 actual approved.json>' --import-manifest 'F:/Ourgame/source-assets/production/fairytale-guard-v001/root-Stomp6-import-v001/import-manifest.json' --native-import '<actual guard-Stomp6 receipt.json>' --independent-import '<actual twoSHA verification.json>' --data-admission '<actual oneData Source admission.json>'
```

默认输出NEW `source-assets/production/fairytale-guard-v001/root-Stomp1332-checkpoint-v001`，已存在即拒绝。只有实际approved两rows、正确namespace/native6真实success及independent两SHA、full193严格GREEN、fresh Source/1332/DLL、两旧Source admission+新Data实际pin全部通过后才创建目录。RootApproved只由这些已批准实际输入驱动，FinalAccepted始终false，不编造source IDs/成功receipt/像素事实。

输出五份填好的文档：manual-input、production extension、Stomp50两row approval、原Data-admission exact-byte副本、原import-manifest exact-byte副本；另输出fresh Known44 source-profile prereg、`Native-Stomp50-profile-contract-v001.json`归一50表及preparation receipt。两exact-byte副本仅供审查，证明链仍引用原实际receipt/manifest路径。

Fresh44 prereg仍原`profile_facts`10与`all_profile_rows`13逐值不变，即11 unaffected含Move、两原Stomp closed；更换的是freshcounts/manifest与实际admitted sourcepins/production extension。Death16、Hurt14、Stomp10源pins从freshsnapshot读回，不拿v138旧HUD/FullPresentation整文件pins当current，也不放宽链外mismatch。

归一50表直接给walk_runtime_review的native prereg helper：schema `Root-GuardStomp50-profile-contract-v001`，profile_id `GuardStomp50V004`、source_count50/logical_budget57、rows13。旧11来自v138allrows，新A/R来自实际preimport批准两rows。frame字段`frame/object_path/source/RGBA_sha256/floor_pivot/pivot_authority`，authority显式1/2/3映射原VisibleShoeSupport/ArtistStandingRootPropagation/ArtistNearSupportDeltaPropagation。Dormant→Wake0 alias零source，Move空且closed。Root首个原生capture另由其helper生成左右prereg，本脚本不生成或运行native观察。

Data receipt最小实际shape：

```json
{
  "schema": "Root-GuardStomp-approved-Data-admission-v001",
  "is_template": false,
  "RootApproved": true,
  "success": true,
  "FinalAccepted": false,
  "Source_count": 262,
  "previous_Data_pin": "stage0 admission admitted中的原stub exact pin object",
  "admitted": ["仅Root实际准入后的DataV004 exact pin object"]
}
```

上面的字符串只是shape说明，不是可用receipt。previous与admitted每个pin均`{path:项目相对Source路径,bytes:实际字节数,sha256:实际SHA}`；after必须Root实际写入后读回。Count以实际两receipt推导Source集合为准。

完成写出后脚本直接调用原冻结manual checker只读verify（其两SHA/Source链/13row/import/parser门全保留）。失败保留NEW目录和success=false preparation receipt，不覆盖旧版本、不启动UE。通过后Root可直接对输出manual-input运行v010 `-ValidateOnly`，再独立决定实际tools/.cmd采用与手动试玩。

已发现并告Root的prepare emitter格式差异已由Root修正：两标准FRow override块各`A.Add(MoveTemp(R));}`，最后Result=ProfileFull逐Clip替2；否则冻结manual parser会拒。这里不改变任何冻结checker。
