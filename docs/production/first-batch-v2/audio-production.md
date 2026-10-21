# 首批本地音效制作 audio-v001

日期：2026-10-14，Asia/Shanghai。**已实际生成17条原创程序合成候选，仍未试听、未导入UE、未通过最终听感验收。** 本轮不使用TTS、人声、第三方采样、付费服务或API；不启动Editor、不修改UE资产/代码/根文档、不提交Git。

## 事实、推理与风险

- 事实：17条WAV均为48kHz、单声道、有符号PCM16；已从落盘文件完整解码。独立libsndfile复核17/17通过，采样削波计数0，首尾采样均为0，采样峰值为−7.959至−5.515dBFS。
- 推理：该批补足可试听的剑/枪破风、弩弦、火焰及石体动作材料；通过数值检查后可以进入听感筛选与真实事件接入，不能登记DONE-FEEDBACK完成。
- 风险：短淡化和采样余量不证明音色自然、无可闻伪影、混音合适或true-peak合格。破韧与死亡目前只有共享碎裂材料候选，需要试听后制出可分辨版本。石翼、刮擦、冲锋刹停的实际展示钩子仍待定义，不借伤害事件伪报命中。

## 版本、来源和重现

- 固定主seed：`20261014`。每条seed由SHA256(`first-content-sfx-v1:<主seed>:<音效ID>`)前8字节按大端整数导出；不使用环境RNG或当前时间。
- 原创方法：固定种子噪声、随时间变化的一阶带通、扫频非整数谐波、短颗粒；去均值后加8ms淡入/15ms淡出（平方正弦），按目标峰值缩放再量化PCM16。所有参数、逐条seed、文件SHA256、采样峰值、RMS均在manifest。
- 原始生成脚本：`tools/scripts/make-first-content-sfx.py`。本批另存完全相同的`source-assets/production/audio-v001/generator-source.py`，SHA256为`37d4e5b796bb2b4e51baf4beced290c7d96b87b9abe0d4f9e1314b5429da40d0`。
- 当前Python：`3.12.14`。同脚本hash/seed/Python版本下测试可逐字节复现；不同平台的浮点数学库可能产生细微差别，换运行时应重新核对哈希。
- 无第三方采样，因此不继承Kenney或其他CC0素材的归属要求；本批没有替原素材重新声明CC0或对全球著作权资格作承诺。
- **任何已存在的输出目录都拒绝覆盖，包括空目录与不完整版本。** 不自动换seed重试；本批已做真实二次运行，退出2且已存文件哈希不变。若以后要重制，显式使用新的版本目录；不要删旧版。

生成命令（本批已运行；现在重复会按设计拒绝）：

```powershell
& 'C:/Users/22499/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'F:/Ourgame/tools/scripts/make-first-content-sfx.py' --output 'F:/Ourgame/source-assets/production/audio-v001' --seed 20261014
```

## 实际产物

目录：`F:/Ourgame/source-assets/production/audio-v001`。

| 候选ID / 文件 | 用途 | 时长s | 采样峰值dBFS | 全文件RMS dBFS |
| --- | --- | --- | --- | --- |
| `AUD-SWD-WHOOSH-01__v001.wav` | 单手剑轻破风 | 0.190 | -6.376 | -20.358 |
| `AUD-GSW-WHOOSH-01__v001.wav` | 重剑沉破风 | 0.340 | -5.515 | -19.944 |
| `AUD-SPR-THRUST-01__v001.wav` | 枪短刺 | 0.075 | -6.936 | -18.157 |
| `AUD-SWD-WHOOSH-02__v001.wav` | 单手剑轻破风 | 0.210 | -6.376 | -20.127 |
| `AUD-GSW-WHOOSH-02__v001.wav` | 重剑沉破风 | 0.380 | -5.515 | -20.166 |
| `AUD-SPR-THRUST-02__v001.wav` | 枪短刺 | 0.085 | -6.936 | -18.329 |
| `AUD-SWD-WHOOSH-03__v001.wav` | 单手剑轻破风 | 0.230 | -6.376 | -18.960 |
| `AUD-GSW-WHOOSH-03__v001.wav` | 重剑沉破风 | 0.420 | -5.515 | -19.402 |
| `AUD-SPR-THRUST-03__v001.wav` | 枪短刺 | 0.090 | -6.936 | -18.354 |
| `AUD-XBW-RELEASE-01__v001.wav` | 弩弦释放 | 0.200 | -6.021 | -23.246 |
| `AUD-FIRE-LAUNCH-01__v001.wav` | 火焰发射 | 0.300 | -6.376 | -19.057 |
| `AUD-FIRE-BURN-SHORT-01__v001.wav` | 短燃烧 | 0.480 | -7.959 | -20.324 |
| `AUD-STONE-AWAKE-01__v001.wav` | 石材苏醒 | 0.650 | -6.021 | -24.201 |
| `AUD-STONE-WING-01__v001.wav` | 石翼振动 | 0.280 | -6.559 | -20.101 |
| `AUD-STONE-ARMOR-SCRAPE-01__v001.wav` | 石甲刮擦 | 0.320 | -6.745 | -23.817 |
| `AUD-STONE-CHARGE-BRAKE-01__v001.wav` | 冲锋刹停 | 0.340 | -5.680 | -22.663 |
| `AUD-STONE-FRACTURE-01__v001.wav` | 石体碎裂 | 0.500 | -5.515 | -23.420 |

实际WAV数量：17；WAV总字节：489,388；总时长：5.090s。17条全部为有限one-shot，未声明循环点。

记录文件：

- `manifest.json`：种子、参数、源脚本hash、格式、逐文件hash/峰值/RMS及待试听状态。
- `validation-report.json`：实际落盘文件的独立libsndfile-1.2.2解码、格式/时长/hash/首尾/余量复核和拒覆盖记录。
- `generator-source.py`：本版源脚本快照。

## 测试与验证

先写4个行为测试，执行后4项均因生成器尚不存在、CLI无法生成而失败；随后实现生成器，4项全部通过。测试覆盖实际WAV格式/余量/短淡化、固定seed复现与变体差异、manifest对真实PCM的指标和hash、对已完成/空目录均拒覆盖。测试不播放音频。

```powershell
& 'C:/Users/22499/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -m unittest discover -s 'F:/Ourgame/tools/scripts/tests' -p 'test_first_content_sfx.py' -v
```

独立复核从本机`G:/UE_5.5/Engine/Binaries/ThirdParty/libsndfile/Win64/libsndfile-1.dll`直接调用解码；未启动引擎。17份WAV全部核对为`0x10002`（WAV PCM16）、48kHz mono，完整帧数/EOF、有限采样、零端点、≥5dB采样余量、manifest指标与SHA256全部一致。RMS不是LUFS，采样峰值不是dBTP。

全量发现测试的第一次并行快照也已运行：33项中音频4项通过，`test_content_atlas.py`的27项非法输入拒绝测试当时失败，收到`passed=true`。该模块由其他参与者制作，本子任务没有改动；具体失败名称保存在validation-report。这个历史快照不是最终集成全绿声明，根代理应在该模块完成后重跑完整测试。

## 后续试听与事件边界

1. 首先试听SWD三条轻破风、石材苏醒/石甲/刹停，与现有CC0接触材料一起筛选；轻甲沿用衣料候选，没有为常驻轻步新造技能声。
2. 枪短刺75/85/90ms可作为三连刺独立起音候选，实际时刻仍来自已接纳最终动作/SubHitID，不能由音效时长驱动攻击或补播未发生的旧段。
3. 火焰发射绑定真实放出；短燃烧只在原有燃烧事件/tick使用，不增加火球主攻的隐含燃烧或让余焰产生新伤害。
4. 弩弦释放不能冒充补弹提交；机括装填仍需原有候选及真实ReloadActionID。
5. 石材苏醒只播真实WakeEventID；石翼/刮擦/刹停需独立展示钩子、取消/暂停/恢复/跨房清理合同。碎裂需区分普通接触、破韧和死亡，Boss死亡不能播放成功奖励。
6. 后续试听后才决定增益、EQ与派生层；单条5dB以上采样余量不保证多条叠层不削波，最终还要引擎混音和打包播放验收。

音频主版本保留在source-assets。本说明没有更新总账或把17条候选标成最终制作完成。
