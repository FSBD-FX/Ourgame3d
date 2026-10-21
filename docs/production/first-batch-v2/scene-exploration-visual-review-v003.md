# Scene v003：9原帧独立复核

2026-10-15，ranged_review。root确认F/E v028保全751文件/2,748,361,512字节、两遍SHA零差后，本agent逐张view_image原尺寸实看9个distinct原件：**0、1、407、536、621、698、710、722、738**。未重复root的64/170/182/264；合计13unique，独立实看仍只记9。未改Source、测试、归档或index，未运行UE/UBT。

F原件批：`F:/Ourgame/过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v003/原件`。捕获源v036，DLL=`95b534b86a8de3df6c5058c3c02d2da6cfef8df6c8ffec12a8959269bfdce2dc`。

独立读取runtime-report：正确profile、Required13/Checks13全true、passed=true、failure为空；另读取`FirstRoom-20261015-125946/index.json`为72Success、0Fail/Warning/notRun。媒体index记录24.650808秒、739电影帧+1prewarm共740PNG CRC门通过，音画时长差0.010808秒；本agent未重算740张CRC或试听。

| 原帧 | 实际可观察结果 |
| --- | --- |
| 0 | 初始化前菜单渲染态，玩家仍中央、武器UI尚无+0。before_menu trace在初始化后发出，不能把两者当GPU同点或以此认证Scene初始显隐。 |
| 1 | 首个实际Scene菜单，英雄已在左入口、军剑+0和native低墙出现。trace sim0/waiting=true，仅WallPath，SurveyRendered=false、visibility=memory=0；像素菜单有遮挡，故结合只读记录判定。 |
| 407 | 英雄实际面向前方石骑，圆盔/军剑造型和当前比例可读，低墙纹理已替换灰盒；不以这张静帧认证完整攻击运动。 |
| 536 | 房01/敌0及清房指引明确，石骑倒下；金币/药水/斧的旧QA几何及重叠标签仍在。 |
| 621 | 旧665附近仍房01，没有确认层；真正出口在右方，仍能看到“附近没有装备”反馈。 |
| 698 | 风险确认层、不可返回/遗留物不带走、Enter离开/Esc继续探索清楚可读。 |
| 710 | 取消后确认层消失，仍原房原位置，顶部已正确改为“继续探索。靠近出口按E可再次查看离开提示。”旧Enter离开提示问题已实际消除。 |
| 722 | 新E后确认层再次出现，没有借取消或旧Enter直接换房。 |
| 738 | 房02/敌1、回到左入口、同军剑/HP100/金币00；没有碑体或碑名透雾。native低墙的当前比例可读，大片灰雾与空地仍明显。 |

补帧1采用首个实际WallPath且SurveyRendered=false的菜单观察：trace wall0.0768384→最近native completion frame1 wall0.0761393，仅补本文，不改原mapping。最近completion映射本来不宣称GPU精确同步。738为无菜单遮挡的新房对照：trace只有WallPath，SurveyRendered=false、visibility=memory=0；HUD room1→2、resetserial2→3。近碑trace实际两native paths/Rendered=true由已读记录确认，近碑完整形状/标签的直接图证由root170/182另审，不假称本agent重复看过。

静态窄审：墙root[256,408]、uniform0.543933映射共享近侧中心(-900,60)，碑root[256,431]、uniform0.18映射实际Object.Position；与冻结manifest一致。整碑/标签零可见度且零记忆即跳过，近标签Y−140；GM开始/取消提示修正不改动作或资源。未见静态阻塞。draw paths代表实际绘制调用/准入，离屏quad不能据此宣称有屏幕像素。

本轮确认取消文案与未知碑整件隐藏的实际修复；开始后初始提示由root before-survey帧主审，不以407的“已调查”文案代替。低墙隐藏后脚/完整AABB美术对齐仍未验证；基础地面保实际XY，native图只作立面/顶面。旧QA掉落的Bound拾取链仍缺，不能当正式来源/奖励完成。9静帧不消除全motion、frame snapping、脚锁或听感问题；灰雾留白仍多，不判完整Scene美术、完整AI、D07/D08隐藏收入/D13。正式15单元仍0/15。
