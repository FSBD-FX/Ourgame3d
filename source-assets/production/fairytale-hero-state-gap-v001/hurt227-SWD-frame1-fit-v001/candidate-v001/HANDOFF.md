# Hurt227 frame1 + 独立军剑：配准候选v001

复用已核对E原件的独立军剑clean源（SHA2efb5519...badded5a），实际Ready绑定sourceGrip[99,256]及统一scale.50。Hurt1自身source（SHA21b75917...e48621）实际闭拳分割为BodyRest和NearHandForeground，二者排他且全部RGBA逐像素重构原件；没有读取/套用Ready hand mask。军剑只作确定性刚性旋转、平移和.50缩放，原body/手RGBA未绘改。

Grip[194,289]是作者选定的可见掌面像素；Axis[.8,.6]明确是右下斜持的艺术选择，源图没有真实柄或可唯一测出的孔轴。已记录轴穿手mask的两端位置、真实护手alpha对腕口ROI零交叠及完整剑边界；这些数值不等于握持通过，必须看合成。

Hurt227同行最大/站立末帧冠底416，固定Canvas72×512/416=88.6154；standingRoot[256,464]是固定地面显示基准，不是隐藏骨或足锁。Hurt1自然收缩显示约67.33px，不能逐帧拉回72。近手foreground覆盖剑柄、其余body在后；新mask边界/遮挡仍待Root实际审。

候选图、放大手部和约实际显示大小图均尚未View。先Root E两SHA保全本批后审单帧；通过/修正后再扩四帧。本批无AI、Source/Content/Roottools/ledger/UE改动，LGT/native、完整Hurt4装备保持和状态衔接仍未完成。
