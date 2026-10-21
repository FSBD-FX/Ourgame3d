# 原motion warning分母与来源补充

原inspect/提取/失败报告全部保持；没有改阈值、重跑pipeline或自动豁免。数值report逐项给512整画布→64缩图分母、实际mask union分母及max90×90设计窗口，并精确重算原metric。四帧RGBA不同只说明不是像素复制，不能证明动作正确。

Chest228原five-step全0，extract0E0W，inspect0E1W；Near229同样five-step全0且inspect1W。Chest四透明仅在E431后实际View；Nearcurated未View。Far230仅extract0/compose1，后续三步未执行，源帧4张仅frames/非curated；原默认compose512稀疏失败和raw宽肩杯身份偏差独立保留，不能拿32×30缩小当tinyFar身份通过。

本补充只有JSON/Markdown，未生成新图；无自动准入或AI重试，全部A/B/整数挂点/coverage仍null。
