# Native167：标准提取停止

按原30×28设计窗口与同一shared-row标准提取，frame02实际used495低于character profile floor512，extract exit1，warnings0。已停止compose/export/preview；未改QA、窗口、subject、min-used-pixels或原像素，不单帧放大。

新增request原先未显式chroma；标准native extractor本机extract.py2604–2616会将默认rgb/unmix4/spill.005写回request，post-run逐字节检查因此失败。自动写回版、diff及before均留在本报告目录；只撤回工具这项副作用，原request已逐字节恢复1442B/SHA7d31b18cb52cecfbb5164c546dff1b94136bbbddbdcbe03a1491ce27a2f6150a，未再运行提取。

E177原raw已独立实际查看：167六片未见166新增的大中央正面圆盘，保留topstrap铆钉构造。此项存在性纠正不等于穿戴/首斩适配/同物件全身份通过；实际A仍null。新派生未view，失败源保持，不导入。
