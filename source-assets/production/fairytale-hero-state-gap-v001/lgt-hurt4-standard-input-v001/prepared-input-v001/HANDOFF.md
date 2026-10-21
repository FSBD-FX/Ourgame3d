# 当前棕皮LGT + Hurt227：三层四相标准输入

实际现用resolver只将Chest/ShoulderNear/ShoulderFar三项切到HeroLeatherReady。已核12asset import manifest、实际Texture2D导入回执和E278逐字节原件，使用当前注册后Ready frame0棕皮源作为各自唯一appearance；不是旧灰甲。胸衣含原带/原侧口袋，不新增口袋层；近肩短圆cap、远肩窄小tab。

每行官方sprite-gen prepare已实际exit0，完整原prompt/request保留，只有explicit组件prompt适配与100ms/chroma配置；SG代码未改。Hurt227四个原512RGBA只拼成pairedmotion参考，四cell逐像素相等，不含剑或套装，不改变身体/拳像素；每行refs为自己的LGTReady组件、该四相motion与官方guide。

Chest90×90、Near60×44、Far32×30沿用现行组件窗口，整行共享尺度；Far256是已有物理小组件的明确提案，不冒effect，不补像素/放宽真实失败。12个新A/B/整数delta全null，Hurt专属身体遮挡/挂点尚未测，不能挪Ready mask或offset宣称完成。400ms时序不改。

canonicalF含原件/展示/索引，新guide和拼接motion尚未View，先Root E两SHA保全再使用AFTER-E references模板。Root持已有自动预算授权并负责内置调用与ledger，本worker0native/API/UE/Source/Content/Roottools修改。LGT source、组合、native和完整装备保持均未验收。
