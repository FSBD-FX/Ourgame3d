# 185 远肩透视审核 v001

已使用 view_image 原尺寸实际查看 Root 已保留的182（E257）和185（E269）原图，未查看新Chest/Near输出或guide。185判定 FAIL：宽正面/近肩式盖与长下垂环取代了原182背心最右侧的窄弯far tab。孤立4件不代表远肩通过。无法仅凭两图证明模型是否逐像素复制近肩，或环是否完全新增。

下一次唯一target应回到原182。2172×724、零基准、右下不含的定位ROI候选：

1. [419,219,480,310]
2. [918,211,979,303]
3. [1438,220,1499,311]
4. [1946,215,2007,311]

边界不确定约±8源px；这些是技术定位窗，可能包含相邻胸甲/黑缝，不能当mask、不能本地矩形裁成最终cap，A全部null。视觉指示：仅保留胸片侧黑缝外的极窄image-RIGHT弯tab，保留原大小/位置/压缩透视；删除宽image-LEFT盖、胸/领/腰袋，禁止新增长环。

`perspective-review-v001.json` 记录原件SHA、实际查看、只读NumPy bbox依据与不确定；`next-far-edit-visual-instruction-candidate-v001.txt` 可作为Root后续短prompt的视觉补充，generation_ready=false。未生成、导入、提取185、改图或写媒体。
