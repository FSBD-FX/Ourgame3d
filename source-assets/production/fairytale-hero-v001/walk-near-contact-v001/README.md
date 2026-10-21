# Near-contact 单姿势纠错输入 v001

仅准备输入，无生成/提取/UE/UBT；非完整 sprite-gen run，不改旧图、Source、ledger 或保全索引。新技术guide尚未view，待root F/E保全后实际查看；它是原创骨架，不是最终美术。

事实：已实际查看137 far-contact原件、131 canonical及已保全far-guide。137近侧大手跨胸前摆、近后腿/远前腿角色比136清楚，静姿势可继续；未判运动/脚根/最终批准。详细报告位于docs/production/first-batch-v2/fairytale-hero-far-contact-137-independent-v001.md。

本次相反接触：近手左后、远手右前；近腿右前且前跟接地/脚尖略抬，远腿左后且后趾接地/脚跟抬。前摆手与前腿属对侧，身体及钟盔仍保持原生朝右三分之四视角，不镜像整个人来换相。

唯一身份是131 idle-v002/curated/frame-0.png，字节副本SHA f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718。primary只附canonical＋新guide两张。137只作已留档的相反姿势/体积对照，不默认附给生成器，不替代身份；135/136失败行、129 base和整idle行均不附。技术guide由空白画布画出，全部坐标为设计点，不能当作新角色足根或体积实测。没有用PIL修改任何现有角色像素。

root后续读取anchor-request.json与prompts/near-contact-anchor.txt完整提示词，先保全输入/guide并实看，再独占生成一张raw/near-contact-anchor.png；实际输出request/尺寸/SHA生成后再记录，没有预编原件哈希。保全新原稿后，逐链复核近/远肩肘腕与髋膝踝、前跟后趾、刚性头盔与身份、空手公共身体和解剖，再做独立静态判定。不符则另版生成，不画改或重定时。

两张contact也不是完整walk。若新静姿势接受，按sprite-gen locomotion边界把它与137组成包含两个相反contact的多姿势motion参考，并配完整六相guide；canonical131继续独占身份。不得把单contact作为唯一整行peak-pose anchor，也不重复两张充当六帧。后续仍须实际六相逐帧/循环播放、5→0、真实脚根/步幅/镜像与UE小比例检查。完整单元仍0/15。

prep-receipt-v001.json绑定准备文件。build-inputs.py只使用sprite-gen自带Python，从空白创建技术SVG/PNG并严格字节复制canonical；不调用native生成或installed skill，拒绝覆盖本版既有输出。PNG/SVG需要root保全后视觉核对，文件/几何检查不代替看图。
