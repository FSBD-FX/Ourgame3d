# 请求258：两帧 Primary1 接入候选

只准备本目录，没有启动 UE、生成图片、改像素、改实际 Source/Content/tools/E/status。Root 已对 matte v002 静图做有限接受；本目录不提升为完整美术、运动或内容单元验收。

## 实际内容和最小变更

- 14 个新 Texture2D：J0/J1 各 4 个已清理的 body owner 加 3 个原 LGT 整数平移层。所有 source PNG 仅引用已冻结文件，不复制改色或缩放；源 FarShoulder/NearShoulder 映射到运行 ShoulderFar/ShoulderNear。
- 新目录 `/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge`。旧资源全部保留，预计 Production 1425→1439，新增类型全为 Texture2D。
- 只修改 `DungeonFairytaleSwordPresentation.cpp` 的两处 exact seams；不新增 header、Source 文件或测试。实际原文件仍是 23904 B / SHA `3df9a140d5fce3c2348d5a21c2bf12c4e19633aa51716df0d91209aff898d49d`。
- 显式追加 `-DungeonFairytalePrimary1Bridge258Preview`；同时必须已有 Bound 模式和 `-DungeonFairytaleLeatherPrimary1Preview`。真实绘制仍要求成功绑定的 LightArmor、SWD001、落地 stage0、帧0/1。关闭新 flag 时保留原分支。
- 新 Root=(256,464)，J0 Grip=(211,343)/Axis=(.94,-.341)，J1 Grip=(159,213)/Axis=(-.2,-.98)，均为有限实机试验 marker；轴不是测量出的真实刀柄方向。J2–5、Ready、Air、Dodge 不改。现有 kernel 的 85/85/60/60/155/155 ms 不改，无新输入或独立动作时钟。
- 原独立剑、组件 grip=(99,256)、统一 scale=.50、atan2 旋转和单次负 U 镜像全部复用。四 body owner 不会画入旧拳头多边形；最后一次 draw 使用新的 NearHand 纹理。

## metadata 与实际像素边界

候选两帧的旧完整 Body 仍由原代码加载，保留 `Record.TexturePath` 和非空资源 readiness 条件。这只是旧 legacy reference，既不是新整幅 body，也不是实际新像素证明。在 committed LightArmor 分支，实际 body 绘制只来自 ReadyLayers；旧完整 Body 不经过 DrawBodyLayer。

实际固定8项 DrawStack 是新 BodyRest、新 ShoulderFar、新 Chest、新 NearArmWithoutHand、新 ShoulderNear、新 HelmetForeground、原独立军剑、新 NearHand。准确路径、两帧 marker、legacy TexturePath 的独立字段见 `source/expected-two-frame-draws-v001.json`。后续新 native checker 应验证同 callback 的实际8项 DrawStack 和对应 GPU 像素；旧 TexturePath 不能当作新 body 像素证明。原老 observer 若硬编码旧7层路径，不能据此直接认可新版本。

## 导入设置与预算

原生源512×512 RGBA/straight alpha，不下采样；TC_EDITOR_ICON、TEXTUREGROUP_UI、NO_MIPMAPS、never_stream=true、sRGB=true 与旧 Primary1 同类 Canvas 图层一致。显式 TF_BILINEAR 与当前 Air48 同类导入一致；旧 Primary1 导入器没有显式设置 filter，所以不宣称其旧 serialized enum 也一定是 bilinear。设置依据和原脚本 SHA 在 `source/import-settings-basis-v001.json`。

这批 PC 原型使用现有 UI RGBA 模式，14张无 mip 源预计增加14 MiB未压缩纹理载荷，实际显存以 native resource 为准；每 actor 活跃绘制仍是原8层，未增加 draw count。它们是固定镜头2D Canvas 贴片，不是需要 mesh LOD0–3 的3D hero；手机移植、BC7压缩和 GPU性能签字均未做。

## Root 下一步

1. 独立审查 freeze、exact seams、14 asset manifest。当前局部静态校验和源 PNG 验证通过不代表 C++ 编译或实机通过。
2. 先完成另一条声音 native proof；随后按 `source/exact-seams-v001.json` 精确应用两处接入，不能覆盖整 cpp 或还原其他工作者变更。Root 按其既有流程记录 actual admission。
3. 导入器默认不导入。直接使用此冻结候选中的脚本，显式 `--native-import --host-proof <本目录/reports/host-preflight-v002.json> --output <NEW Root evidence目录/import-receipt.json>`。receipt/claim 必须位于本项目内、冻结候选之外。Root 独占 editor，禁止 overwrite/retry/delete。若只完成部分，保留所有资源和失败 receipt 后再分析。
4. 导入器会验原1425包两次、14新目标不存在、原PNG/冻结依赖、Texture2D类型、原生尺寸、source filename、设置 readback、真实 async compilation finish、精确 registry/disk membership。全部导完后仍需 Root 独立文件哈希与必要 native source/GPU 验证。SoundWave 六包也属于旧1425保护集。
5. Root 真实 Editor compile；保持旧无新 opt-in 的203项回归，通过后另做新 opt-in 的真实 J0/J1→旧J2…→Ready 左右方向观测，尤其检查握柄、上挑衔接、脚底和暗/亮背景边缘。必须留 F/E 再 View。不得用静图代替动作衔接验收。

本地复核命令（PowerShell，cwd `F:/Ourgame`）：

```powershell
& ./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 <本目录/source/verify-source-binding-v001.py> --expected-current before
& ./tools/runtime/asset-gen/Scripts/python.exe -B -X utf8 <本目录/import/ue-import-primary1-bridge258-v001.py> --validate-only
```

`reports/host-preflight-v001.json` 是增加 native freeze gate 之前的历史报告，其 importer SHA 已过期，只保留追踪；生效报告是 v002。所有导入结果、实际 C++ 编译、画面、全动作、声音试听和完整内容单元验收仍待 Root 执行。FinalAccepted=false。
