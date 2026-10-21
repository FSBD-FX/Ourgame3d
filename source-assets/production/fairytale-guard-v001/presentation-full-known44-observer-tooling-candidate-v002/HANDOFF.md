# Known44 AxeCycle tooling v002：精确六测试 oracle 修复

真实阻断：Root Source231 / Production1254、build130513 exit0、FirstRoom130609 full184 strictGREEN。v001 source-only首次实际失败发生在UE启动前：旧checker要求`FairytaleGuardPresentation.*`恰3个，但实际合法第四个`TerminalDeathMaterialClockReview`使其误拒。原v001冻结／Root失败证据保留；此处不改actual Source/tools/Content、不要求重新编译。

唯一行为修复是把两个prefix计数断言换成六个精确名称各出现一次、state=Success/errors=warnings=0。全suite仍核真实registry数、唯一测试名、所有测试严格Success且无错误警告；同prefix其他合法测试允许。`tooling/validate-native-test-oracle-v002.py`以真实184报告验证，并保留额外合法同prefix、缺目标、重复目标、Fail/error/warning/错误布尔计数反例。

H/CPP/HUDpatch/protocol与原source-AxeCycle-freeze-v001完全相同。native报告仍`guard-art-known44-native-observer-v001`、session仍`guard-art-known44-native-session-v001`、scenario=AxeCycle；工具版本变化不假造新native协议。新独立核验回执名`independent-known44-AxeCycle-v002.json`。CRC/FIFO、角色／时钟／source／floor／首AttackId及位置断言保持，主checker除本次测试oracle外只有工具自身路径/回执版本替换。

Root在原v132 snapshot保持不动，从实际v132 prereg另写新文件，只把`candidate_freeze_pin`换为此 `known44-AxeCycle-tooling-freeze-v002.json`的精确pin；原schema、actual compiled manifest SHA、typedcounts、实际admitted Source pins、10known/13allrows、审批/import均保留。先执行NEW `tooling/verify-known44-axecycle-v002.py --snapshot <actual-v132> --root-prereg <NEW-absolute-prereg> --source-only`，再用NEW `capture-known44-axecycle-v002.ps1`，不原位覆写旧文件。模板仅供字段参考，不在本候选中制造Root新审批或捕获成功。

完整正常输入/原生覆盖/缺口范围沿原v001 HANDOFF：只有首Axe WU6/A4/R4+Wake6/实际Ready4，44 resident不等于44渲染。当前只完成静态oracle修复与核验，未启动UE/UBT/capture、不称nativeGREEN或最终美术接受。
