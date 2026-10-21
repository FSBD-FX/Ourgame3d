# Native218–220：标准提取准备候选

本包当前只有文本和可执行候选；没有读取新raw像素、生成图片、调用native/UE或View。
仅Root已经通知实际raw完成F/E留档后，才能把真实F/E文件pins填写到新的admission记录，
然后运行提取。旧standard18文件和Guard review冻结不动。

三行独立NEW run：Dodge218四帧10fps、Hurt219四帧10fps、Death220五帧5fps。
每个run从原数值request只选择自己的state；原multirow request另pin保留，不改它。
raw直接按字节复制，保留原生实际尺寸/模式，不把标准guide的512格假作raw切图坐标。
每行共享一个实际ratio，真实component分离，禁止slot fallback、缺帧复制、Ready合成、
源码手绘、逐帧缩放或改QA阈值。

标准工具顺序：已pin的项目shared-row extractor→SG compose atlas→SG export curated→
SG preview→SG inspect。均用sprite-gen venv。默认命令只核文本/工具，不读新raw：

```powershell
& 'C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001/hero218-220-extraction-v001/extract-retained-rows-v001.py'
```

Root通知后，NEW admission记录必须包含真实通知说明、native编号、F raw pin与已保全的
E original pin，F/E必须同bytes/SHA且E路径必须在指定留档根内。模板中的false/null
不是通过证明，也不能在raw未留档时改成true绕过。通知本身已经授权本范围，不需再向
用户请求确认。按行执行 `--extract --state dodge --admission <NEW实际记录绝对路径>`，
hurt/death同理。run已存在则停止，失败也保留旧版本，不能重跑覆盖。

标准extract/compose/export失败会保留全部失败输出和日志并冻结，不改像素重写历史。
inspect的姿态相似/运动启发式发现另记录为WITH_INSPECT_FINDINGS，不放宽阈值，也不
把自然倒地轮廓差异直接自封为已验收。每个NEW run包括完整命令/log/pins、实际raw
大小、curated RGBA/SHA、alpha与alpha128 bbox/覆盖像素、共享ratio、atlas frame_layout
和实际fps/loop。统计只描述像素，不能冒称身体语义、真实物理脚点或解剖正确。

所有实际Floor/身体支撑、Root/Crown、Grip/Axis和hand replay mask仍null。标准bottom
placement边界不等于已测脚锁；三行共享ratio各自成立，也不证明跨行头盔/身体比例一致。
后续需要对真实像素测量，并与唯一SwordReady v002 frame0身份锚对比。

Death最后帧从.8秒保持是runtime美术采样方案，不是gameplay deadline。SG QA GIF是
便利预览：当前SDK对loop=false写GIF loop=1，不能把该文件当终端无限保持的运行证明；
receipt会记录实际编码循环参数。真实不循环/尸体hold必须由之后native运行证明。

新curated、atlas、QA contact/GIF和任何后续diagnostic都必须先由Root保全到E，包括
originals/presentation/index，再View。此脚本只在owned F候选下写新run，不显示媒体；
不写E、Source/Content/tools/ledger/status，也不会自动导入、接受或登记新源。
