# 软皮轻甲 Ready 单一编辑目标纠错 v002

三次标准 sprite-gen prepare 已实际执行，退出码均为 0。每组仅引用对应 180 / 181 / 182 错误原图的逐字节副本作为编辑 target，不附加 layout guide 或其余旧参考。技术 guide 保留用于记录标准 prepare，不代表造型通过。

- Chest 草案183：保留软皮胸/腰及附着小袋；删除两侧肩 cap 和灰 undercloth。
- Near 草案184：仅保留每个原背心的图像 LEFT 短皮肩 cap；删除躯干、腰袋、远肩和灰 innerhole。
- Far 草案185：仅保留每个原背心的图像 RIGHT 小 cap；删除其余内容，不镜像近肩。
- 每行 4×167ms；Chest / Near / Far 共同缩放窗口为 90×90 / 60×44 / 30×28，整行统一 scale，future A 全部 null。
- 输出要求不透明平绿 #00FF00；这是下一次原生图像编辑，不能在本地裁切整背心伪称分层成功。

`lgt-ready-correction-input-draft-v002.json` 为交接入口，各行的 `prompt.path` 都在其 run 的 `prompts/<state>.txt`，帧数及 durations 从 request 派生。标准 request / prompt 修改前副本和明确字段恢复记录保留。草案编号不是 ledger 预留，Root 先选择 Near 或 Chest 单次试验时按实际下一编号落账。

generation_ready=false。Root 完成输入检查和 E 归档后，才可浏览新 guide；未经语义检查不可导入。执行者未生成、未改 ledger / ActualSource / README / progress / 过程媒体，未浏览、截图或绘制/裁切最终图。180—182 的 FAIL 来自 Root 实际审图报告，不是执行者自行看图结论。
