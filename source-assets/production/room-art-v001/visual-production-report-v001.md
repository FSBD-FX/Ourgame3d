# 环境分层候选 · 2026-10-15

本批仅新增3次内置生成（请求25/26/27）：far scenery、mid scenery透明层、石地面material。使用asset-gen流程及generate2dmap的side_scroll_mode/brawler、parallax_layers契约。不是完整地图；演员、门、箱、可拾取物、危险物、可走障碍均没有烘焙进图。碰撞、walkable belt、scene hooks仍由现有工程提供。

可接入最终冻结合同：`manifests/import-subset-v005.json`（SHA256 `932409106c3adfc8c25ad9cf9396f23da6ab09f17dfaa97f23be7fdbfd4cc124`）。Far主层1280×720；Mid主层1280×720、RGBA，Y323..719 alpha全0；Floor为512×512独立材质，以世界格重复，建议一格显示256×256stage px，仅供运行调试，不定义实际世界碰撞尺度。UE资源名T_RoomFar_v001 / T_RoomMid_v001 / T_RoomFloor_v001，目录 /Game/Production/RoomArt/v001/。

Far/Mid原始均1672×941，统一float crop[0,.25,1672,940.75]后单一等比Lanczos到1280×720，没有非等比拉伸。两层左上anchor[0,0]，wall footline合同目标323，Far scroll[.10,0]、Mid[.30,0]、runtime zoom1.2。Far最低装饰石边约340，由独立floor323起覆盖；这是视觉锚点而非从像素推导碰撞。Mid实际非透明bbox bottom321，中央留空，背景远拱可见。相机±457、zoom后的边缘覆盖仍须运行端检查，不能仅凭静态图声称全部parallax范围通过。

Mid处理保留了全部尝试：v001的180/260色键误删暖琥珀石块；v002改90/140恢复4334个opaque像素，但有细洋红边；v003改90/190及源分辨率色键残留清理；最终v004增加归一后透明边缘色键清理，移除1891个残余像素。只令被判定洋红污染像素alpha0，不绘画补洞或重涂；未额外生成。最终无洋红污染像素、无强制下半遮罩、Y323以下自然抠为全透明。过度抠色失败版和中间合同都留存，接入只用最终v005所列文件。

Floor原始1254×1254，单一等比缩小到512；未拼接混合修缝。原样2×2重复预览已审看，没有明显断带。对边RGB平均差 X4.2376、Y4.9831；邻列/行差 X2.1875、Y3.0846。它是可重复基础材质候选，未声称像素级完美无缝，仍需实际材质/相机缩放检查。无演员/道具/坑洞/障碍；石缝和浅裂纹仅装饰。

工具原件原路径保留，所有source/raw/processed/preview/合同均双留存到 `F:/Ourgame/过程图稿与视频/2026-10-15_遗迹地牢环境分层_v001` 与 `E:/OurGame/Knight/过程图稿与视频/2026-10-15_遗迹地牢环境分层_v001` 的原件、展示副本、index.json。提示词与来源hash在统一ledger/层合同中。单一主ledger为 `F:/Ourgame/source-assets/production/first-unit-animation-v003/generation-ledger.json`：本自动窗口2为3/24；自EV039累计27次，加EV038历史24次共51次。外部API0，host费用未知。

这里只生成、确定性处理、逐图审阅和核验，未启动/改动UE。根代理负责导入、场景组合、迷雾/边界、截图录像和实际110px主角可读性验收。已生成合成预览仅是QA，不作为运行地图或碰撞来源。
