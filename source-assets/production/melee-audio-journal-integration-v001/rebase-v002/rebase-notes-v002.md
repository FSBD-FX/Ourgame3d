# 未应用近战声音patch重定位 v002

保留旧v001候选，当前目录只保存本次rebase。Fighter/World的基线SHA与v001相同，原两个逻辑hunk逐字保留；HUD两个音频局部hunk基于当前文件重新生成行号/上下文，不回写整份HUD、不回退Bound consumer/P3V002或其他并行修改。总计仍3文件、4hunk，未应用ActualSource。

- [当前基线、尺寸/SHA及3tests关联](baseline-v002.json)
- [未应用patch](production-rebased-v002.patch)
- [实际git apply --check结果](git-apply-check-v002.json)

关联原测试文件SHA c2de7b0a3fc49970d3145d51fb12ded19cb7c34ee9bf7935b03171a9657815d5，仍3组且逐字未变。Root先准入测试并实际取得语义RED后才可准入本patch；本轮没有UE/UBT/音频播放/实际RED或GREEN。git检查只证明检查时这些hunk可应用，不证明C++编译或声音效果。五cue旧语义、Schema、RNG、战斗时钟仍未改。

若Root继续修改相同HUD区域，应再次检查/重定位小hunk并登记新SHA；不恢复本目录记录的整文件，不改旧candidate。相关声音差异与最终听感仍未设计/验收。
