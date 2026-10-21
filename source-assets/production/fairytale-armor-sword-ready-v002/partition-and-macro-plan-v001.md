# Native158低位Ready：真实三层与宏观甲候选

本目录全新，原155准备/v001和158原帧未改。E141保全后实际看四帧512RGBA及既有0/1近手原像素crop；近拳实际在image-LEFT腰旁，中央胸口露出，不能继承设计275315或155跨胸mask。131仍sole identity；147只给暖灰金属/粗墨线经验，不给新姿势或挂接。

measurement-candidate-v001.json逐新帧记录可见领口下缘、腰带上缘、近袖外弧、远侧露袖外弧的人工选线，误差约3–5sourcepx；胸/近肩/远肩A分别选在实际可见衣面，属于附件设计点，不是骨骼、已测physical rivet或相同feature跟踪。隐藏近/远肩关节、远肩躯干被遮缝、grip与剑轴留null。实际抓握/脚根由root/clean单独量测，本分层不借旧值。

body-partition-v001为实际源RGBA候选分区：BodyRest / NearArmWithoutHand / NearHand。每帧分别手工trace新源可见近臂轮廓、袖-棕腕口、拳-腰带接触边；NearHand含棕手套、其腕口和相关黑墨边，不等同未来剑的精确指/拇指occluder。NearArmWithoutHand含其余近袖，BodyRest保盔/颈/躯干/远臂手/裤靴和所有剩余坐标。所有源RGBA坐标包括alpha0恰一owner，三个输出仅复制自己原RGBA，其他RGBA为0。没有重画、变色、移动、缩放、复制整身到各层、补隐藏身体或沿旧mask。

四帧actual proof均逐RGBA字节重组相等，实际alpha合成后的premultiplied RGBA也相等；无重复owner/丢失坐标，部分alpha原值完整保留。这只证明数值保真，**不证明肩缝/袖手/黑线归属在语义上正确**。肩袖-躯干、袖-腕口、手-腰接触候选有2–3px uncertainty band，须E142后看三层与技术overlay。蓝=BodyRest、紫=近袖、黄=近手；色图/overlay/band都是技术诊断，不能导入冒充新人物或甲片。当前新输出未显式view、semantic_accepted=false。

甲候选拟层序：BodyRest→FarShoulder→Chest→NearArmWithoutHand→NearShoulder→Sword→NearHand。近肩盖真实上袖，不能压前臂/手；先回放近袖再画近肩，避免opaque袖盖掉甲。短远肩仍应有真实可见贡献，既不能放整身体后全遮没，也不能压盔/颈；若组件实际穿插，须重新候选设计或真实局部occluder，不扩大身体mask迎合。分层复原是裸体层原图合成，不包括尚不存在的甲/剑stack通过。

拟初试local extraction窗口：Chest70×50、NearShoulder60×44、FarShoulder30×28，按固定72/416约12.1×8.7／10.4×7.6／5.2×4.8screenpx。窗口是可调设计上限/提取约束，非语义允许bbox或actual fit。胸在真实领口下和腰带上宽面；近肩向外扩剪影而非向盔/领口挤；远肩只取压缩短片，不能从近肩镜像。三件均独立4×167ms、同四源pose、同画布/整身一次镜像、同shared-row scale；生成片实际feature A未产生，必须null。只有量测/技术图root审核后才允许下一native输入。

仅4帧idle的试样准备。没有甲生成、导入、UE/Source/台账修改，不借157攻击首尾、连续循环、四甲或正式装备完成。身体72px不放大；正式完整单元仍0/15。
