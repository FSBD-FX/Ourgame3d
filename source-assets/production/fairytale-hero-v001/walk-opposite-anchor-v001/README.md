# Opposite-contact 单姿势纠错输入 v001

状态：仅输入准备。没有调用图像生成器、提取器、UE/UBT，没有生成任何最终角色像素或动作帧；不是完整 sprite-gen run。此目录不覆盖旧版 walk、原稿、Source、ledger 或保全索引。

## 事实、推理与边界

唯一身份输入是 request131 的 idle-v002/curated/frame-0.png，字节副本位于 references/identity；SHA f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718。该 512² RGBA 图已实际查看：完整钟盔、双琥珀眼、灰黑内衣、棕手套和靴、空手、原生朝右三分之四视角。既有技术 idle 身份不等于最终用户美术或动作验收。135/136 仅留在旧审阅报告，未附为新生成输入；129 早期 base 和整张 idle strip 也不附。

root 要求的 near 手前 / far 腿前是对侧摆臂，自洽；near 腿后 / far 手后是另一对。将“两只鞋接地”明确为远前脚跟与近后脚趾接触同一线，避免误生两只平底全掌贴地的战斗站姿。新技术 guide 的红=近侧、蓝=远侧，不把画面左右当肢体身份；颜色只用于讲解，不是最终角色配色。

guide 是从空白画布绘制的原创技术骨架，SVG 与 PNG 均随本版保留。build-inputs.py 没有读取或改画角色像素，仅字节复制身份图；所有骨架点都是设计说明，不能作为新角色实际足根、盔甲包围盒、动作长度或 runtime 物理测量。新 guide 尚待 root F/E 保全和实际视觉审核；本准备者没有展示或宣称看过新 guide。未来生成原件也必须先保全再看。

## root 后续输入

使用 anchor-request.json 的两附件顺序与 prompts/far-contact-anchor.txt 完整提示词：1=唯一身份，2=仅肢体角色 guide；生成 exactly one far-contact full-body pose。费用/生成由 root 处理，本准备者没有调用供应商。新原件须独立落 raw/far-contact-anchor.png、记录实际 request/尺寸/SHA、F/E 保全后审图；不预先编造原件、足根或 alpha 报告。

静帧审核顺序：先身份和刚性钟盔；再逐条连接肩→肘→近前手/远后手、髋→膝→近后腿/远前腿；再确认前跟/后趾接地、没有多手多腿/断腕/融膝；最后检查小尺度可辨性。若不符，保留失败版本并另版再生成，不能本地修画角色或改时长掩盖错误。

## 不把单图当完整 walk

sprite-gen/docs/directional-anchor-workflow.md 的 State anchor gate 明确禁止把单个 peak pose 作为最终 cyclic locomotion row 的唯一状态锚点。本图只隔离 far_contact 的纠错题；若随后静帧接受，它可加入同时包含两种相反 contact 的多姿势 motion reference，并配六相骨架。canonical idle 始终拥有身份；不得把此一姿势重复成六帧，也不能直接把它当后半循环已经完成。

完整六相仍须连贯支持/摆腿/推蹬、真实播放 5→0、落足/步幅量测、左右镜像与实际 UE 小尺度检查。本次没有新增 armor、weapon sockets 或 gameplay，formal complete units 仍 0/15。

## 文件与复现

anchor-request.json 是本次输入入口；pose-contract.json 区分技术设计值与尚未知的生成实测值。prep-receipt-v001.json 绑定所有准备输入 SHA。原始 guide 几何与渲染均在 build-inputs.py；只允许在新的空版本目录复现，脚本拒绝覆盖本版已存在的准备输出。运行所用 Python 为 sprite-gen 自带 .venv/Scripts/python.exe；未修改 installed skill。
