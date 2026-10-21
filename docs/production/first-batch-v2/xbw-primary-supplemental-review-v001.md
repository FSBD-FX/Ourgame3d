# 猎弩射击v001：左右待机及装填身份独立补审

2026-10-15，ranged_review。root已确认F/E v025保全158文件/546,374,244字节、两遍SHA零差后，本agent逐张调用view_image原尺寸实看以下4原件。未重复root已看的射击93/95/96/101/108，不改archive index或原件，不运行UE/UBT。

原件批：`F:/Ourgame/过程图稿与视频/2026-10-15_猎弩专属射击三阶段运行_v001/原件`。来源v032是实际72 RED DLL，和随后Scene优先级修复候选分开；这段片没有走Scene确认层，不把其11/11冒称Scene72 GREEN。

选择以实际trace同clip/facing/pose的中间观察对应最近native capture完成时间；不是GPU精确同步。下表pose为trace记录，图片是独立实看范围：

| 原帧 | 实际观察 | trace wall秒 | capture wall秒 | 实看结论 |
| --- | --- | --- | --- | --- |
| 33 | 右待机，pose3 | 1.245467 | 1.237097 | 圆盔、双手胸前持弩，前托手与后握手可区分；短宽弩轮廓完整，没有玩家剑/剑弧残留。 |
| 67 | 左待机，pose3 | 2.742766 | 2.738128 | 弩与手臂一同朝左，未见双重镜像、额外手掌或裁断；双手仍接在弩的前后部。 |
| 139 | 右装填期，pose0 | 5.758519 | 5.747449 | 保持圆盔与双手持弩，HUD显示贯甲弩矢；没有裸几何头或回退玩家长剑。 |
| 127 | 右装填期，pose3 | 5.358518 | 5.347641 | 保持同一持弩身份与当前比例；画面仍为ready姿势，没有可观察的拉杆、上弦或插箭机械动作。 |

绿色测试靶自身举着的长剑不属于玩家Sword残留。当前1280×720原件中玩家约百像素高，头身、弩臂和双手关系能读；扳机/弦的细部没有据此完成逐像素接触验收。四张静态观察不能判脚锁、全motion、听感或世界muzzle。

独立读取`runtime-report.json`：profile=`xbw_authored_primary_body_normal_inputs`，Required11/Checks11且passed=true；primary frame mask55只实际观察0/1/2/4/5，phase mask7；reload_body_is_ready_pose_placeholder=true。未捕获的primary pose3不认证，本补审不补造其帧；装填保持身份不等于机械装填动画完成。

运行报告SHA256：`dd8f4de4c6c48fd31ff78d9c755cf7318fc79a9c38c9e1acb512584e9e0a2121`。

原帧SHA256：33=`059bde97842228deb758348bc99548ea24ab91b9c46bbd1c441f134817dac7b6`；67=`170b202c2513d74ade4f40ca27209e763cd44e79a613c2a561ade6b29ab8780e`；139=`aa0af838b2e8ef72f4d6d594c67171dbc6c09d4b4f01c0b63978a98bea6f5f7b`；127=`b62815d24965ef6540f49a00c8c8b2959ae9c8f3ded9ff8e35574e83a2bdbc29`。

本补审仅上述静态持握/身份局部可观察事实；攻击全6姿、装填机械动画、世界发射坐标、正式掉落/音频/D13均未因此验收，正式完成仍0/15。
