# Owner 默认 111 入口最终独立核对

日期：2026-10-16（Asia/Shanghai）。本报告补充已冻结的 `independent-fighter-owner-schema2-final-review-v001.md` 与 `independent-world-owner-production-v004-final-review-v001.md`，不覆盖历史 RED/GREEN 审查。本次只读文件、SHA、脚本差异及实际报告，没有运行 UE/UBT 或修改任何 Source、测试、脚本、ledger、媒体。

## 默认运行与文件绑定

实际 `FirstRoom-20261016-024800/index.json`：111 Success，0 SuccessWithWarnings/Fail/NotRun/InProcess；111 行对应 111 个唯一完整测试名称，总 errors=0、warnings=0。与 `004750` 原 103 个名称集合比较，缺失 0、非 Success 0；新增名称精确为既定 FighterOwner5 + WorldOwner3，全部 Success。没有换名或加重复测试凑计数。

冻结目录：`source-assets/production/backups/2026-10-16_fighter-schema2-world-default111GREEN-v070/`。独立重读 manifest 所列 **1085 个文件、73,299,914B**；逐份对 frozen 长度/SHA 以及当前对应 source 长度/SHA，共 **2170 份文件端点检查，差异 0**。没有只检查目录存在或只转述 root 的 audit JSON。

| 绑定 | 字节 | SHA256 |
| --- | ---: | --- |
| v070 compiled-source-manifest.json | 256489 | 0bc9f6933ad05aba66b207dec7ef8493cd978ee512e5d71f8c19b69db414dc27 |
| 默认脚本 tools/scripts/test-first-room.ps1 | 1589 | 148caa2afc59620e2447e93242ddff35e0fd1112c0b5b3e7695fe00f75c6cdb2 |
| 实际 FirstRoom-20261016-024800/index.json | 80040 | c10fba131ff1a0c579245ae757e2fbe6b1efc0d7840e68c9dbf0fcfffa1f09cc |
| 实际编译 DLL | 3041280 | 2665d1f0058935cd3cc739fbef1851eb4f6f4637d2d6dc8af4628ce983b434de |

独立比较 v069/v070 manifest 共同路径，唯一内容变化是 `test-first-room.ps1` 默认 `ExpectedTests=103` → `111`。完整 unified diff 只有该行；旧非零进程/缺报告/Fail/NotRun/成功数检查原样保留。Source、Fighter Schema2 及 World 生产源码、全部测试、DLL 均与上一份 v069 的最终审查绑定一致，没有以修改实现或减弱断言换取默认入口通过。实际报告路径随独立运行改变，旧 `024633` 报告保留。

Fighter.cpp 为 `834aae1d256ff894fd9c656088f96de4cca23b344d7f069790a61050b00132a2`，Snapshot.h `4668cc12f6091729b6aecc54a1c738e1f867b1c63f6eb2afd90375d0797ccf3e`，Fighter tests `21789d30e819493c920961bd92a2b13ef20523fd3b0849111677820d1b883554`；World.cpp 为 `8c4b0a23148bed9f412472f76f701fefadef433b1a3e9282c440d84b2d5b5dcf`，World tests `850534cea7034cba862702f933e6820690f6351187fc77736c31ac74aee51d7f`。

## 结论范围

本轮 owner 实现、真实反例修复、完整回归与默认计数入口之间的文件证据闭环成立，未发现最终冻结版本的新阻断问题。Fighter Schema2 的 actual native anchor 与 JumpHeight/Facing 独立保存，精确安装与旧 runtime 不变结论沿完整 Fighter 报告；World 的发射/receipt/burn phase 边界沿 World 报告。

这仍是当前本地 owner API 与独立 staging 恢复验证。没有整局 live Actor map 事务安装、磁盘编码/Continue、新进程正常输入续玩或新视频/音频验收。六相美术目录只是已保全的 metadata-only 来源计划，没有拼图、生成、播放或导入。完整装备/敌人内容目标仍为 0/15。
