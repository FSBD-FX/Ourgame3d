Dodge218 的四个原始 512 RGBA cell 已逐像素核对，拼接参考只提供闪避动作/镜头/可见灰布与肩部方向。每个当前棕皮 Ready 组件各自是唯一外观身份：Chest184、Near186、Far187；未使用 Hurt227/233、旧灰甲或其他整身作 Dodge 身份。

三个官方 sprite-gen prepare 均实际 exit0。原始 request/prompt 保留，显式适配为 single-component row；SG 源码未改。Chest128×100 是共同最大安全窗口，Near60×44、Far32×30；不要求逐相填满窗口，不逐帧缩放。Chest/Near 的512与小 Far 的明确256像素门保持。Far 的第二参考是同一187的 exact20×28裁片 nearest12x，四份 refs 的角色序号已统一。胸衣真正的领/腋孔使用绿背景负空间，禁止 opaque black backing。

native output 给新的固定 process-batch 路径，native序号仍null并由Root实际reserve回执记录；绝不往已冻结 prepared run 写原稿。预先 null 的raw/scale/A/B/fit不冒未来事实。400ms四相仅美术采样，不改原400ms/185world/无敌区间或输入逻辑。新媒体未View，先Root E保全后使用 AFTER-E refs。0AI调用、0quota改动、0Source/Content/tools/ledger/README修改。