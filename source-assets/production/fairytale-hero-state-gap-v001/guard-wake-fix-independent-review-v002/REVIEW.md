# Guard wake v007 独立审查 v002

事实：已独立核实 `FirstRoom-20261018-114243/index.json`（3525B，SHA eb03df9029c9880cde0770ca0205ceaf84fa7590f69e8bb40f56075af1a2806a）。0成功/1失败/1error/0warning；宽Driver已Accepted，短区间endpoint经真实kernel判inside后，唯一错误是第121行目标N.Accepted。这次是真正Driver semantic RED。旧113329仍是fixture前置失败，二者不混记；实际测试与v005候选字节相同。

事实：v007 freeze2601B SHA c8b45b620bb12e20bfe9e9f7a1c3f77814c420f70e9c8f84c07f96a35a252bf0，10项冻结文件核对零差。我独立按exact before Driver上下文在内存应用2个hunk，结果419行逐行等于reconstructed-driver，完整exact-helper嵌入一致。初步意见发出后Root已准入actual；最终pins另列v129保全before（21268B/da61c077…）及当前actual，当前actual正规化行也等于候选。我没有对Source应用patch。v006未使用。shim语法0只证明shim环境语法，未被写为UE编译通过。

推理：未发现阻止Root对v007继续原生验证的新P1/P2。

- NextBoundary切每个From/To，hits边界只会进一步缩短。在开区间内倒序PositionAt选择固定覆盖段或原Frame fallback；空档/重叠合法记录也没有未切分的映射切换。exact Begin/End可能是零时长/新段，现分开查询。
- 原Cursor Pump仍先观察；helper第15行Inside(Begin)仅不重复分段，不绕原LOS/alive/whole-room gate。
- 第48–55行先真实查AfterBegin，再搜至BeforeEnd。相邻端点无开片，只有一个内部double时单独查询。Begin孤立点与End跳跃位置不会被混入开片解析曲线。
- 第19–22行真实Inside(Limit)独立成为bracket，封住v003解析false veto真实终点的缺口。第57行End独立fallback只接受实际End，不凭跨跳跃chord造更早Wake。
- 第34–44行两端实际outside/inside，2102上限、mid等端点退出和范围/Inside复查保留。原Next>Cursor拒绝未改，无epsilon、强推时间、状态写或Wake重播。
- 后续仍原Kernel/InputAt在该边界观察，235×110、目标存活、LOS、queue、WakeAt+1、HP/receipt都没改。

风险：v007HANDOFF已明确只证bounded observed slice及已认证bracket的邻接crossing，不冒称全浮点域所有切线/非单调舍入孔洞的全局最早点。Begin几何inside但LOS阻挡时，仍由原后续边界Pump观察，未新增连续LOS搜索。driver/kernel重复几何表达式在/fp:fast下仍需native真实点/前邻回归验证，静态同形不证编译逐位等价。开片增加少量PositionAt查询，二分内无LOS/分配/kernelstep；最坏单次PositionAt扫描很多段，成本不能笼统称常数。本审查无native benchmark。

下一步：Root使用同一v005、不改断言，完成实际UE编译、定向及真实registry全量，再做原要求的NEW63mask真实Wake录制。静态审查、shim语法0和unit GREEN都不代替真实画面覆盖。本次只写NEW文本/JSON，无生产patch、Source/tools/候选修改、UE/UBT/native执行或媒体操作。
