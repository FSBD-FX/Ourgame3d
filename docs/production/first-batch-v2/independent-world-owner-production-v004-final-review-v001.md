# World owner v004 最终窄差异复核

日期：2026-10-16（Asia/Shanghai）。本轮 World owner 范围内，上一份 v003 报告保留的晚到刷新缺口已通过真实反例和窄修关闭；未发现该差异引入的新阻塞问题。独立读取 `022145` 实际报告确认 World 三组全部 Success、各 0 errors/0 warnings，原 103 个测试完整名称全部保留并 Success。全量是 110 Success、1 Fail，不能称全 111 通过。其余初审结论和范围限制见保留的 `independent-world-owner-production-v003-review-v001.md`。

本审查只读冻结 Source、实际报告、DLL 和 snapshot。没有运行 UE/UBT，没有修改 Source、测试、脚本、ledger、媒体或既有报告。

## 实际反例与生产差异

独立读取 `FirstRoom-20261016-021659/index.json`（80208B，SHA `845854ac56316d817233304da2491250634db72e46f212e62cecf74765913355`）：全量 109 Success、2 Fail、0 warnings/notRun/inProcess。World Burn 组恰有两个错误：删除旧 BurnExpired、把真实晚到 BurnApplied 改为 BurnRefreshed 并改为旧继承相位的候选被接受；随后完整 Out 已变化。另两个 World 组均 Success。该结果将 v003 报告的静态推断升级为实际 CPP 反例；没有把后续安装变化计成另一个独立生产缺陷。

反例测试先通过真实 staff CD、正常 K 产生旧 burn 到期后的新 application，原完整状态先成功 Restore，之后才修改候选 journal/NextTick。新增真实 RangeEnd、零 HP loss 的 burn tick、晚到 fresh reapplication 正例也已到达，避免只为坏候选添加不合理全局限制。测试 SHA `850534cea7034cba862702f933e6820690f6351187fc77736c31ac74aee51d7f`、31133B 在 RED 和最终 GREEN 两轮之间不变。

对冻结 v003/v004 完整 cpp 作逐行 diff，唯一变化是第 261 行 Refresh 条件增加 `E.AtTime > Prior->ExpiresAt`，增加 27 字节。其余 replay、原始 emitted/source 一致性、正 direct hit 唯一性、phase 累加、零损血允许、旧房间/死亡历史、原子 Candidate 安装均不变。严格 `>` 拒绝跨过旧 expiry 的继承刷新，并保留恰好等于旧 expiry 的 batch 边界；没有改成 `>=` 或按全部 journal AtTime 全局排序。

## 冻结运行绑定

历史依据：`source-assets/production/backups/2026-10-16_worldGREEN-custom-muzzle-tinyRED-v066/compiled-source-manifest.json`。独立从 snapshot 重读以下六份文件，长度/SHA 均匹配 manifest；没有用随后工作的 live tests/DLL 代替该次实际运行。

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| DungeonWorldSnapshot.h | 978 | d3a0e9d2a3117f4ab5a2fad65fad96fbc522a0b8d9439b32bd6671667cd632d7 |
| DungeonWorldSnapshot.cpp v004 | 24530 | 8c4b0a23148bed9f412472f76f701fefadef433b1a3e9282c440d84b2d5b5dcf |
| DungeonWorldSnapshotTests.cpp | 31133 | 850534cea7034cba862702f933e6820690f6351187fc77736c31ac74aee51d7f |
| UnrealEditor-CodexDungeon.dll | 3021824 | d25b066dfb23823068f4c73010877c01b32233caca3e01e02cc1a5f233f1c498 |
| build-editor-20261016-022058.log | 4313 | 72bad8c76e096d5d8a09b0c1b2cf870b75ca9dda2364d51e4638faa14004fde9 |
| FirstRoom-20261016-022145/index.json | 79758 | 2b01ec16911d70a4091f0207b1a82df3d56abe484707e4b46ebc805c50f67286 |

`022145` 全量 110 Success、0 SuccessWithWarnings、1 Fail、0 NotRun、0 InProcess。三项 `CodexDungeon.Content.WorldOwnerSnapshot.*` 全部 Success，实际 gap 反例及原六类反例、RangeEnd/zero-loss tick/equal refresh/fresh reapplication/真实换房历史等同组三组断言均无错误。以 `004750` 的原 103 名称集合核对：缺失 0、非 Success 0。唯一失败为 FighterOwnerSnapshot.InvalidCandidateIsAtomic 的两个 tiny custom muzzle 精确恢复断言，由 Actor owner 工作者继续窄修，本报告不为该项认证。

## 可声明的边界

本结果关闭已实测的 World owner 恢复缺口，证明冻结 schema 1、当前绑定 player、给定 saved WA Context 下的本地完整值校验与安装。它没有运行 live Actor 整体恢复、暂停后继续游戏、磁盘写入/Continue，也没有证明未接入的 aggregate 原子安装。没有重播攻击或 burn 伤害来制造相同结果。完整装备/敌人内容目标仍为 0/15；本轮 owner 数据单元验证不能代替动作、美术、音效或可玩内容验收。
