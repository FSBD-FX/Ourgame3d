# 原生墙碑与探索运行复核 v003

2026-10-15。实际13/13正常输入检查通过；新版苔墙/石碑实际被HUD调用，整件未知石碑隐藏。root实看4个原生帧、独立9个，共13独特原帧复核；正式完整内容仍0/15。

编译来源`source-assets/production/backups/2026-10-15_scene72-GREEN-nativeProps-v036`，786文件61,282,531字节；build-editor-20261015-125830.log exit0，实际UE125946严格72/72，零警告/失败/未运行。DLL SHA256 `95B534B86A8DE3DF6C5058C3C02D2DA6CFEF8DF6C8FFEC12A8959269BFDCE2DC`。快照包含源码、DLL、Production资源、Scene importer/冻结manifest/实际receipt、启动与录像脚本。

F原批`过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v003`；视频`展示副本/scene-exploration-normal-inputs.mp4`。E副本`2026-10-15-OurgameUE-原生墙碑探索13项-v028`，751文件2,748,361,512字节，大小/SHA两遍零差、E根README未改；完整保全后才查看。

739电影原帧+1预热共740原生PNG逐像素CRC通过，展示740帧。实际录制24.650808099657297s，UE主混音24.64s，音频与墙钟差.010808099657296566s，首帧.02917660027742386s，最大原帧间隔.04778560250997543s。保留原UE WAV和仅修BlockAlign头的副本，PCM完全一致；全流解码通过，未变速、改增益或替换声音。此门槛不证明听感、逐sample同步或性能。

正常E调查只提交一次且无收入，正常移动和J军剑清敌，E/Esc/新Enter换房13流程成立。真实石骑持续追随，本定向QA只在sim0禁止自主起攻；普通手动Scene预览不禁起攻。Room2保持Run、武器Instance1与HP100/Focus100/金币0，新碑未调查/无记忆，旧碑调查历史保留。

root实际审看MovieFrame64/170/182/264：壁前接触、发现碑、调查后、退回记忆。苔墙替换灰块后与地牢材质相近，角色圆盔与缩比保持，近距提示移高后可读；调查正常按键停到碑西60cm，无改物件位置/半径/战斗状态。碑身仍部分被人物遮挡，不能认定全部碑纹可读。退回后场景暗下且保留位置记忆。

只读trace在170/182显示实际墙和碑两条Texture路径、surveyRendered=true、memory/visibility1；264显示visibility0/memory1。新房738仅墙路径、surveyRendered=false、memory/visibility0。13检查本身不独立断言native纹理成功，实际路径与原帧是额外证据。映射`evidence/2026-10-15_scene-exploration-runtime-v003/review-selection.json`按最近捕获完成戳选择，非GPU逐帧同点。

墙sprite whole512保持uniform260/478与root256408映射真实近前沿(-900,60)，底座沿共享WorldStatic AABB显示。素材实际顶面深约24.48logical/立面高38.08，与最初38/24意向不同，隐藏后脚仍inferred；不能称整AABB已由图像精准匹配或全遮挡通过。石碑uniform.18/root256431映射(-920,300)，不新增碰撞。旧QA掉落未接正式Bound来源，场景变化仍较少。隐藏奖励/多房布局/全AI动作/声音混音/完整装备敌人/D13仍待制作。

独立实际审看0/1/407/536/621/698/710/722/738共9张，与root4张不重复。Frame0是Scene初始化前菜单渲染，不能拿postinit before_menu trace冒称同帧像素；Frame1才是已有actualWallPath且sim0等待开始的Scene菜单，菜单仍遮挡部分画面。Frame738为无菜单的新房直接隐藏对照。路径字段记录实际DrawTexture调用，不保证离屏quad产生可见像素；出口处两条路径不得解释为离屏碑在画面可见。独立报告见`scene-exploration-visual-review-v003.md`。
