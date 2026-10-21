# Landing priority AV presentation candidate v001

候选仅准备工具。没有运行 UE、当前原生 checker、真实编码、F 媒体输出、E 保全、View 或试听；不是实际四场景通过，也不是最终美术验收。Root 独立 scoped review 后执行。

固定入口是 `prepare-landing-presentation-v001.py`。六个参数均必须显式传入，路径请替换为 Root 的真实已完成 archive/prereg/result；output 必须是 `F:/Ourgame/过程图稿与视频` 下不存在的新一级目录。不可覆盖旧目录。

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-hero-air-v001/landing-presentation-candidate-v001/prepare-landing-presentation-v001.py' `
  --archive '<actual archive>' --prereg '<actual Root prereg JSON>' `
  --independent '<retained single-native or four-case independent JSON>' `
  --checker 'F:/Ourgame/source-assets/production/fairytale-hero-air-v001/landing-priority-observer-candidate-v001/tooling-review-fix-v002/verify-landing-priority-native-v001.py' `
  --checkerfreeze 'F:/Ourgame/source-assets/production/fairytale-hero-air-v001/landing-priority-observer-candidate-v001/tooling-review-fix-v002/HeroLandingPriority-Task2-tooling-freeze-v002.json' `
  --output 'F:/Ourgame/过程图稿与视频/<NEW dated-topic-facing-action-v001>'
```

每个 J/Shift × left/right 以实际 prereg 独立调用一次。工具复核最终 16681b… 脚本和 c785c6… freeze 全成员，再调用官方 `--archive/--prereg`，并与 retained 单侧 dict 或四侧 cases 中唯一匹配 prereg 的分支做逐类型精确比较。拒绝时返回 3 并保留部分输出与 stdout/stderr；不从旧 Air296/three-jump 流取得当前 PASS。当前官方 checker 自身会核现有实际 Source/Content，后续开发变更后应在变更前完成本轮媒资准备，或由 Root 用新注册流程处理，不能绕过此门。

12 个辅助函数逐字保留自 b0dd84… 冻结 Air 展示源，含完整 PNG 微秒 VFR、完整原 PCM 复制、完整 AAC mux/EOF 解码、全帧 PTS 和完整音轨长度/原点检查。内部历史 Air6/Stomp 编码文件名保留以免修改已证函数；本轮真实 case 由索引/原 runtime schema 与 requested_action/facing 决定。视频有损；完整 engine/canonical WAV 原字节另存。无 trim、变速、补帧、拟合、静音替代。

动作样本使用最终 checker 的原 source_pixel_witnesses，中点选择不重算；J 每6姿态为真实 legacy8层，Shift 每4姿态为真实9层/33 resident。Air0..4、初末 Ready 同样来自实际 callback/PNG。全部层栈读取实际 rendered_player_stack/actual_stack，不读 stale body_texture。

首动作边界始终展示真实上一 callback→首动作，实际上一姿态可为 Land4/Land5/其他。另列 first Land4 causal token→首动作端点：有间隔就显示 ENDPOINTS 与 intervening callback 数、全部索引/clock。末动作→首 Ready 同理，有间隔则另加两处真实相邻边界；不增加 Land4 必须相邻的假门。full 原幅和 256×320 原像素 crop 板均不缩放，标签放游戏矩形外；保存后逐像素复核 crop 相等。

完整原 PNG 留在 native archive，媒体包仅复制选定原幅样本/端点、必要元数据和完整两份 WAV。索引列出每个全帧 source pin/原 wall offset/实际 decoded PTS；不假称自包含全 raw PNG 或 E 已完成。Root 需保全原 archive 和媒体新包后才 View/试听，保持 visual_reviewed/audio_listened/FinalAccepted=false 直到真实审阅和批准。

依赖：上述本机 Python（Pillow/imageio_ffmpeg/numpy 与 checker 依赖已在项目 runtime）、冻结 c785 checker 全闭包、冻结 b0dd 源、655457… retained-microsecond-VFR helper、本机 imageio_ffmpeg 自带 ffmpeg。无外部 API/生成图像/桌面录音。只读 archive/checker/CM；写入新 F output。

小 host 测试仅数据适配测试：不会调用官方 native checker、不编码、不运行 UE、不生成实际 F/E 媒体。旧13项测试记录留存；当前15项含合法 Land5 间隔、Ready 间隔、错 token/缺 witness/借错 PNG/旧元数据替代/错 schema和数量/错时序/重复 PNG/typed dict/aggregate唯一性/最终 checker exact pins，以及原 timing gate 的变速漏帧反例。不是 runtime 或听感验收。
