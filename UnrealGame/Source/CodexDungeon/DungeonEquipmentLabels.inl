#pragma once
// docs/design/equipment-v2/affixes.json SHA256 e6e3737cb15e64f0782dae0f0652dbac80ebaabf9ee9d97c46bd3e439402c75e
// docs/design/equipment-v1/armor.json SHA256 9407e458aef80b9f0d8f0e958b089e7b7a6f4180aef41b7b7df97534fe780e9d
// docs/design/equipment-v1/weapons.json SHA256 95757819382832cfa31e6596f3ba90f1e983e83fbd69504da3c99d5ea2a272b4
// Display text from frozen design; no ownership, RNG or attribute calculation.
namespace DungeonEquipmentLabels {
inline FString Name(const FString& Id) {
    if(Id==TEXT("WPN-KNF-001")) return TEXT("折巷短刃");
    if(Id==TEXT("WPN-KNF-002")) return TEXT("燕尾双匕");
    if(Id==TEXT("WPN-KNF-003")) return TEXT("破缝锥刃");
    if(Id==TEXT("WPN-DAO-001")) return TEXT("断梁大刀");
    if(Id==TEXT("WPN-DAO-002")) return TEXT("折肘短斩刀");
    if(Id==TEXT("WPN-DAO-003")) return TEXT("铸潮阔刀");
    if(Id==TEXT("WPN-SWD-001")) return TEXT("尺衡军剑");
    if(Id==TEXT("WPN-SWD-002")) return TEXT("银线刺剑");
    if(Id==TEXT("WPN-SWD-003")) return TEXT("折锋弯剑");
    if(Id==TEXT("WPN-GSW-001")) return TEXT("裂碑重剑");
    if(Id==TEXT("WPN-GSW-002")) return TEXT("远誓长锋");
    if(Id==TEXT("WPN-GSW-003")) return TEXT("双脊钝剑");
    if(Id==TEXT("WPN-SPR-001")) return TEXT("疾雨短枪");
    if(Id==TEXT("WPN-SPR-002")) return TEXT("守门长矛");
    if(Id==TEXT("WPN-SPR-003")) return TEXT("逐阵棘枪");
    if(Id==TEXT("WPN-HAL-001")) return TEXT("巡门长戟");
    if(Id==TEXT("WPN-HAL-002")) return TEXT("倒钩战戟");
    if(Id==TEXT("WPN-HAL-003")) return TEXT("半握月戟");
    if(Id==TEXT("WPN-XBW-001")) return TEXT("栓机猎弩");
    if(Id==TEXT("WPN-XBW-002")) return TEXT("转轮袖弩");
    if(Id==TEXT("WPN-XBW-003")) return TEXT("绞盘重弩");
    if(Id==TEXT("WPN-PST-001")) return TEXT("旧港转轮短铳");
    if(Id==TEXT("WPN-PST-002")) return TEXT("双管礼仪铳");
    if(Id==TEXT("WPN-PST-003")) return TEXT("冷铁单发决斗铳");
    if(Id==TEXT("WPN-SGN-001")) return TEXT("矿工短喷");
    if(Id==TEXT("WPN-SGN-002")) return TEXT("长管收束猎铳");
    if(Id==TEXT("WPN-SGN-003")) return TEXT("鼓腹扫荡铳");
    if(Id==TEXT("WPN-RFL-001")) return TEXT("哨岗栓动步枪");
    if(Id==TEXT("WPN-RFL-002")) return TEXT("铜胆三连铳");
    if(Id==TEXT("WPN-RFL-003")) return TEXT("带刺卡宾枪");
    if(Id==TEXT("WPN-STF-001")) return TEXT("余烬灯杖");
    if(Id==TEXT("WPN-STF-002")) return TEXT("霜脊刻杖");
    if(Id==TEXT("WPN-STF-003")) return TEXT("鸣针导杖");
    if(Id==TEXT("ARM-LGT-001")) return TEXT("行路短衣");
    if(Id==TEXT("ARM-LGT-002")) return TEXT("折风短甲");
    if(Id==TEXT("ARM-LGT-003")) return TEXT("铜扣游射衣");
    if(Id==TEXT("ARM-MED-001")) return TEXT("巡路环甲");
    if(Id==TEXT("ARM-MED-002")) return TEXT("锁肩鳞甲");
    if(Id==TEXT("ARM-MED-003")) return TEXT("灰盐护纹甲");
    if(Id==TEXT("ARM-HVY-001")) return TEXT("门栓板甲");
    if(Id==TEXT("ARM-HVY-002")) return TEXT("沉锚铆甲");
    if(Id==TEXT("ARM-HVY-003")) return TEXT("封釉重甲");
    if(Id==TEXT("ARM-ROB-001")) return TEXT("灰烛法袍");
    if(Id==TEXT("ARM-ROB-002")) return TEXT("断章短袍");
    if(Id==TEXT("ARM-ROB-003")) return TEXT("静脉长袍");
    return Id;
}
inline FString Skill(const FString& Id) {
    if(Id==TEXT("sword")) return Skill(TEXT("WPN-SWD-001")); // Explicit historical QA alias.
    if(Id==TEXT("WPN-KNF-001")) return TEXT("跨步点刺");
    if(Id==TEXT("WPN-KNF-002")) return TEXT("撤身回刃");
    if(Id==TEXT("WPN-KNF-003")) return TEXT("寻缝深刺");
    if(Id==TEXT("WPN-DAO-001")) return TEXT("压阵横扫");
    if(Id==TEXT("WPN-DAO-002")) return TEXT("贴地截步");
    if(Id==TEXT("WPN-DAO-003")) return TEXT("回潮二扫");
    if(Id==TEXT("WPN-SWD-001")) return TEXT("进身斜斩");
    if(Id==TEXT("WPN-SWD-002")) return TEXT("三点连刺");
    if(Id==TEXT("WPN-SWD-003")) return TEXT("带身拨锋");
    if(Id==TEXT("WPN-GSW-001")) return TEXT("落碑重压");
    if(Id==TEXT("WPN-GSW-002")) return TEXT("掠锋平斩");
    if(Id==TEXT("WPN-GSW-003")) return TEXT("蓄身直顶");
    if(Id==TEXT("WPN-SPR-001")) return TEXT("迅雷三刺");
    if(Id==TEXT("WPN-SPR-002")) return TEXT("撑杆退刺");
    if(Id==TEXT("WPN-SPR-003")) return TEXT("横杆逐阵");
    if(Id==TEXT("WPN-HAL-001")) return TEXT("开门推斩");
    if(Id==TEXT("WPN-HAL-002")) return TEXT("回钩牵引");
    if(Id==TEXT("WPN-HAL-003")) return TEXT("刃尾连击");
    if(Id==TEXT("WPN-XBW-001")) return TEXT("贯甲弩矢");
    if(Id==TEXT("WPN-XBW-002")) return TEXT("连压三矢");
    if(Id==TEXT("WPN-XBW-003")) return TEXT("钩索牵引");
    if(Id==TEXT("WPN-PST-001")) return TEXT("撤步双响");
    if(Id==TEXT("WPN-PST-002")) return TEXT("压火分射");
    if(Id==TEXT("WPN-PST-003")) return TEXT("定音贯铳");
    if(Id==TEXT("WPN-SGN-001")) return TEXT("顶肩重喷");
    if(Id==TEXT("WPN-SGN-002")) return TEXT("单孔铅柱");
    if(Id==TEXT("WPN-SGN-003")) return TEXT("双响清道");
    if(Id==TEXT("WPN-RFL-001")) return TEXT("支肩定射");
    if(Id==TEXT("WPN-RFL-002")) return TEXT("定距点放");
    if(Id==TEXT("WPN-RFL-003")) return TEXT("反手刺刀");
    if(Id==TEXT("WPN-STF-001")) return TEXT("铺炭火线");
    if(Id==TEXT("WPN-STF-002")) return TEXT("霜扇刻痕");
    if(Id==TEXT("WPN-STF-003")) return TEXT("双极贯闪");
    return TEXT("武器技");
}
struct FAffixLabel { const TCHAR* Name; const TCHAR* Unit; int32 Direction; bool Beneficial; };
inline FAffixLabel Affix(const FString& Id) {
    if(Id==TEXT("AFF-P-001")) return {TEXT("锋利"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-002")) return {TEXT("轻快"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-003")) return {TEXT("震击"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-004")) return {TEXT("延伸"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-005")) return {TEXT("精确"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-006")) return {TEXT("凶猛"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-007")) return {TEXT("熟练"),TEXT("%"),-1,true};
    if(Id==TEXT("AFF-P-008")) return {TEXT("疾装"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-009")) return {TEXT("节能"),TEXT("%"),-1,true};
    if(Id==TEXT("AFF-P-010")) return {TEXT("汲血"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-011")) return {TEXT("灼热"),TEXT(""),1,true};
    if(Id==TEXT("AFF-P-012")) return {TEXT("寒意"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-013")) return {TEXT("电痕"),TEXT(""),1,true};
    if(Id==TEXT("AFF-P-014")) return {TEXT("坚固"),TEXT(""),1,true};
    if(Id==TEXT("AFF-P-015")) return {TEXT("护纹"),TEXT(""),1,true};
    if(Id==TEXT("AFF-P-016")) return {TEXT("稳固"),TEXT(""),1,true};
    if(Id==TEXT("AFF-P-017")) return {TEXT("健壮"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-018")) return {TEXT("凝神"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-019")) return {TEXT("复原"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-P-020")) return {TEXT("灵动"),TEXT("%"),1,true};
    if(Id==TEXT("AFF-N-001")) return {TEXT("钝化"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-002")) return {TEXT("笨重"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-003")) return {TEXT("松劲"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-004")) return {TEXT("短锋"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-005")) return {TEXT("迟钝"),TEXT("%"),1,false};
    if(Id==TEXT("AFF-N-006")) return {TEXT("卡涩"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-007")) return {TEXT("漏魔"),TEXT("%"),1,false};
    if(Id==TEXT("AFF-N-008")) return {TEXT("破损"),TEXT(""),-1,false};
    if(Id==TEXT("AFF-N-009")) return {TEXT("漏护"),TEXT(""),-1,false};
    if(Id==TEXT("AFF-N-010")) return {TEXT("松散"),TEXT(""),-1,false};
    if(Id==TEXT("AFF-N-011")) return {TEXT("虚弱"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-012")) return {TEXT("散神"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-013")) return {TEXT("难愈"),TEXT("%"),-1,false};
    if(Id==TEXT("AFF-N-014")) return {TEXT("易伤"),TEXT("%"),1,false};
    if(Id==TEXT("AFF-N-015")) return {TEXT("惧术"),TEXT("%"),1,false};
    if(Id==TEXT("AFF-N-016")) return {TEXT("拖步"),TEXT("%"),-1,false};
    return {TEXT("未知词条"),TEXT(""),1,false};
}
}
