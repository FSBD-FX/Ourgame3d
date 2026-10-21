# AxeCycle tooling v003：及时发布真实 PID／exit／native 状态

Root实际 v133右侧 PID40736 的native已PASS，689帧、22.95672s、63/15/63/15/15、44resident。原v002 launcher在启动后只改内存PID，直到checker失败进入catch才写index，导致独立checker先读到null PID并错误拒绝。原v002／首次失败与同原件后续重核必须保留，不把重核说成首次全通过。

NEW v003仅三处发布顺序修复：Start-Process得到PID后立即写index；WaitForExit后发布exit_code；读真实report后发布native_reported_passed，均在调用checker之前。失败catch与最后状态写入保留。Source H/CPP/HUDpatch/protocol逐字不变；主checker除自身candidate冻结文件名v002→v003外逐字相同，六名称及全部native oracle不改；独立回执文件仍`independent-known44-AxeCycle-v002.json`，native/session schema仍v001。

新fresh capture使用 `tooling/capture-known44-axecycle-v003.ps1`；Root新prereg只换candidate_freeze_pin绑定此总freeze，实际Source/DLL/snapshot不因这个工具修复而重编。已有v133原件可直接用原v002 checker在已落盘真实PID的原index上重核，不重新跑UE；本候选不改它的index/report/PNG。

静态检查会核三次Set-Content顺序及主checker仅冻结路径变化。没有本候选UE/UBT或媒体/View执行。准确索引发布修复不改变任何AI、时钟、HP、窗口或覆盖规则。
