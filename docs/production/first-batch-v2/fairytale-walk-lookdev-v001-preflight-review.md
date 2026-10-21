# 六相步态 UE lookdev v001 独立预检

2026-10-16（Asia/Shanghai）。结论：当前冻结导入清单、实际六包导入回执与四份显示/Probe源码未发现阻塞问题，可以交由root编译并进行独立真实运行观察。此报告是静态/资源预检；没有运行UE/UBT或录制，没有把原PNG、导入成功或字段正确称为实际画面/动态通过。仅新增本报告，Source、脚本、资产、ledger与冻结清单均未修改。

## 冻结资源与源码事实

导入清单为 `F:/Ourgame/source-assets/production/fairytale-walk-lookdev-v001/manifests/import-walk-lookdev-v001.json`，6780B，SHA `16c5cfef46662730a48ac1a5c68a6e250710f5330fe11c57b548d7e2779787fd`。六个来源精确为v008 curated0..5，六个不同PNG SHA、512×512透明RGBA、原alpha bbox/phase顺序、83ms×6、nativeFacing+1，源request/frames/atlas/raw/registration五项冻结引用完整。唯一新namespace为 `/Game/Production/ArtTrials/EV047/v002/HeroCommonWalk`，不覆盖原v001 HeroIdle/StoneIdle。

实际导入回执 `UnrealGame/Saved/Bootstrap/fairytale-walk-lookdev-v001-import-20261015-193357-409584.json`，7543B，SHA `8644226159e33d7f77eafffb7bce65de206549c3ea63a4a9624f1b24cfa60f5f`：六个实际Texture2D，actual/saved/expected=6，registry/disk exact set成功。独立读取当前六份uasset的字节数/SHA，与回执全部相符。原只读 `checks.preflight(require_unused=False)` 通过；root补充新六包保护后，再独立执行当前 `verify-fairytale-walk-lookdev.py --preflight-only --manifest <冻结清单>`，实际exit0，输出source_PNGs=6、native_imported_packages_unchanged=6、old_packages_unchanged=863。当前Production为869包；没有重新导入或写资源文件。

Importer实际源码使用不替换旧对象的AssetImportTask，逐对象检查512尺寸与Texture2D类型，设置/读取确认TC_EDITOR_ICON、NoMipmaps、UI group、never_stream、sRGB后保存。回执证明此实际过程；本预检没有重新进入UE读取对象属性，也不把uasset SHA当GPU最终呈现的像素证明。

四份当前源码SHA均与 `evidence/fairytale-walk-lookdev-v001/source-optin-v001-manifest.json` 相同：

| 文件 | SHA256 |
| --- | --- |
| DungeonHUD.h | e47b8057b0f06cece8a4ed1f47f9de27b1fc08bf349a7febe33e717060b370d1 |
| DungeonHUD.cpp | 1d2f024a9a1b46f8a535318f850403f2acfbddfc95e695bef1f9b2346da5ddd9 |
| DungeonFairytaleLookdevState.h | 2b5cc4eb4f72e30738764ece762b158069fb0904607acb8a6bd76ec41c74432e |
| DungeonFairytaleLookdevProbe.cpp | ab5231275f5cb0f92c39ac5afbd4c49f79b6dbfe0f6df4eca1aff0e7bedc67ca |

## 显示/录制链的静态核对

新walk开关只在既有 `DungeonFairytaleLookdevPreview` 分支解析 `DungeonFairytaleWalkLookdev`。Hero实际加载六个 `T_Fairytale_HeroWalk_%03d_v002` 路径，sample=floor(elapsed/.083)、frame=sample%6；Stone仍独立floor(elapsed/.167)、%4，原v001路径/roots/canvas不变。没有继续用同一个sample代替两个时钟。缺纹理/未就绪时记录失败并跳过该模型，没有回退旧身份/装备贴图。

Hero统一canvas=88.6153846154、pivot=[256,464]；六帧可见alpha高度按原图为72/70.4423/71.1346/70.9615/70.6154/71.4808，不能要求每帧72或逐帧重缩放。该pivot是展示锚点，不是认证身体/足根。Hero屏幕脚线锚点[435.2,540]，Stone[819.2,540]，由既有Ground/Screen投影产生；镜像按nativeFacing与展示Facing比较，Hero根X居中，Stone沿原根处理。

旧idle默认仍4×167ms、7.2s/60fps；新profile为4.2s/30fps，正常D→A→D各1.4s，其他正常输入只作冻结压力。既有GM独立preview提前返回与Controller→GM tick依赖链保持，A/D仅更新展示朝向，不是实际Fighter移动。新增Probe记录clip、mode、实际draw/path/sample、selected Game/Equipment/World/RNG/audio观察字段，依旧保留真实prewarm、capture stop和writer flush边界。

新只读checker分别核Hero6/83与Stone4/167、双朝向全pose、Hero每side至少两次实际5→0、Stone每side至少一次3→0；每张PNG对应当前递增drawSerial/相同epoch/合理draw-to-callback时差、准确path/scale/root/投影/flip。它要求UI/text/legacy stack/旧weapon/audio requests为0，selected game字段逐row与baseline相等，正常输入均有press/release记录。这是观测摘要一致，不冒称每个私有kernel字段已经逐字比较。

原无损native检查器SHA-pinned复用：prewarm不混入录制，逐PNG viewport BGRA CRC、复制CRC、排他文件reservation、唯一FIFO/计数/时间顺序及close/flush/drain规则保留；没有改旧helper或伪造audio stop。PS独占UE、拒绝覆盖历史archive，按真实monotonic PNG间隔编码30fps silent MP4，再全解码并严格识别Audio stream声明，不会因ffmpeg `audio:0KiB`摘要假报音轨。

## 真实运行观察清单（全部待实测）

1. **证明是在UE里看新图。** 绑定同次compiled Source/DLL、六新uasset与本清单/回执，验证每原PNG CRC与draw记录；实际看1280×720场景，不能拿v008源contact代替game。原场景/迷雾保留，新Hero与旧Stone可见，UI无顶底栏、血条、文字、箭头、旧武器层残留。
2. **六帧与双方向。** 从原PNG选取实际hero0..5的左右朝向及至少两组5→0邻接，逐张核身份/遮挡/前跟/手臂；确认新模型无missing/fallback，Stone仍原四帧上下文。检查固定小尺度与展示脚线，不能由metadata直接宣布视觉比例合理。
3. **冻结事实。** 核sim/body/HP/Focus/Ammo或记录的资源游标、Room/World/RNG/audio摘要不随A/D或J/K/E/Enter/Space/Shift等压力改变；A/D只变展示。当前是站定播放walk图，不是地面距离驱动的可玩走路。
4. **循环观感。** 在实际短片完整播放多圈后，再判1→2/3→4近手快切、passing下沉/两半抬靴、5→0盔面/鞋形与脚滑。原PNG数量、CRC通过、源metadata无错或录制文件存在均不能单独通过motion gate。只看选定PNG时应明确未看完整连续动画。
5. **诚实媒体边界。** 记录silent video无音轨并全解码，源83ms保持；30fps呈现采样与GIF80ms量化不能混同。先F/E保全原PNG/报告/视频后再独立审图与展示，不以本预检替代运行或美术验收。完整目标仍0/15。

初审发现当前六包来源保护没有在录制前自动重算；root已在本报告冻结前补齐，四份C++未改变。新版checks固定实际导入回执SHA，核对成功/数量/manifest SHA与逐项object_path/source_sha256绑定，再核当前六份uasset精确路径、字节数与SHA。新版PS在创建archive/启动UE前执行`--preflight-only`，失败即停止。独立实际预检通过，因此该缺口已关闭。它证明当前磁盘资源绑定，仍不能代替同次compiled Source/DLL绑定、GPU原PNG或动态视觉审查。

实际导入时使用的原三工具另存于 `source-assets/production/fairytale-walk-lookdev-v001/import-tool-version-used`，没有用当前增强版冒充原导入版本。独立核其中原checks SHA `5cfb764522fd1fc06e955b42c94e233f140bdfdaf091f6fce9b84471c19023dc`、importer SHA `56ad58a4c4903ab6d2190842f595fbaead3dd3994befaff292979e8e4c54ece8`，均匹配实际回执；原import PS SHA为 `80a28a24e01e5f5030bd5c7573899cd81e416e29e30fbb563feb59b0fa4feb02`。

## 工具绑定与状态

- 当前checks.py（6522B）SHA：`d7755d4787cc9e22e3964ba239bbc86ddb38a6bfdcc03af41730c6daf1b70248`
- 当前runtime checker（8883B）SHA：`70643b536642620ffc95dda55013293759503ef4235e10036c35405ec27e75e9`
- 当前PS profile（8372B）SHA：`7d1aad6e603c7d7c5725a4abae583bb3307a17756f3c83c44d87938f1ee4e8ec`
- 原native audit SHA：`f94684fa62e1080d330b096ea5ba2f1f0ef5a1be1075c027f187ad25b9d176b1`

本报告截点仅静态/实际导入文件预检通过，root编译/真实实录/后续F/E视觉证据仍分别取得结果。没有新UE gameplay身份安装、动作衔接/足根/stride/战斗/音效通过、用户终批或完整内容单元完成。
