# 窄范围独立复核结果

只读 explorer 初审发现：首次接入晚于真实起跳/闪避会吞掉第一声；独立 legacy Fighter Tick 的 clock/dispatch 不匹配；关闭门早退可能保留 Tick 外待播请求。

修正后的再次只读复核确认：起跳在 V=630 前 seed；Dodge 在 TryStart 前 seed；legacy SimulateMotion 增量全部删除；GameMode canonical H interval 使用明确 From/To；Tick gated/waiting/terminal 提前返回前 drain inactive。三份实际文件 SHA、唯一 before/after 接点及结果 SHA 由 verify-handoff.py 再核对。该范围未发现遗留静态阻断项。

范围：仅支持由 ADungeonGameMode 统一模拟和派发的实际 PlayerFighter；独立 ADungeonFighter Tick 不在候选支持范围。源码候选尚未完成 UE 整体编译、运行接线及试听验证。

独立复核没有写文件、运行 UE、调用 API 或重新运行主机测试；本记录由候选作者依据两次只读复核消息保存。主机 RED/GREEN 属作者执行证据，不混为独立运行。
