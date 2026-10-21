# Unity 初始化历史记录（已被 Unreal Engine 5 取代）

2026-10-10 用户明确改用 **Unreal Engine 5**。本记录与 `Game/`、`tools/scripts/unity-*.ps1` 均为历史准备材料，不代表当前引擎选型，也不应据此继续启动 Unity、连接 Unity MCP 或制作 Unity 玩法。原文件、Library 和日志已保留。

## 实际完成的准备

- 复用本机 `G:/UNITY/6000.0.43f1/Editor/Unity.exe`，版本修订 `97272b72f107`。
- 从编辑器自带 `com.unity.template.3d-cross-platform-17.0.11.tgz` 提取 URP 工程资产与设置；未把模板 Library 当成编译结果。
- `Game/Packages/manifest.json` 固定主要依赖：URP 17.0.4、Input System 1.13.1、Test Framework 1.4.6、Recorder 5.1.2、Newtonsoft JSON 3.2.1、uGUI 2.0.0。
- MCP 包使用 `file:../../tools/unity-mcp/MCPForUnity`，与本地 CoplayDev/unity-mcp 提交 `30d22075093d1d35dfb0091c1c7550e9ad948577` 对应，包版本 10.2.0。
- 包管理器真实生成了 `Game/Packages/packages-lock.json`；例如 Burst 1.8.19、Collections 2.5.1、Timeline 1.8.7 已被解析记录。未沿用原模板不匹配的 lock。
- 创建 `Assets/Scenes/Foundation.unity`：相机、光源、校准地面、1 米方块和运行探针。仅为准备场景，没有玩家、敌人、战斗或关卡流程。
- 建立 Art、Audio、Prefabs、Scripts、Scenes、Tests 导入目录。
- 复制 7 个 Kenney 代表 FBX、2 张 colormap 纹理、各包 CC0 License 与来源/SHA 清单；复制 Blender 连接测试 FBX。完整商业/游戏素材准备不在这个代表导入验收的证明范围内。

## 运行与验证结果

首次 batch 与交互启动因本机无有效 Unity Editor 许可证失败；另用独立临时工程探测 Unity 2022.3.60f1，也出现相同授权错误。没有把 `Game/` 降级到 2022。未读取或展示账号、令牌或许可证正文。

用户报告已激活后，09:31:49 重试 Unity 6 batch。该进程实际完成 C# 编译、项目初始化及代表 FBX/纹理导入检查，日志出现：

- `[CodexBootstrap] Prepared FBX/texture import and Blender 1x1x2 metre bounds verified.`
- `[CodexBootstrap] Initialization complete. Foundation scene and locked package manifest ready.`
- `Batchmode quit successfully invoked - shutting down!`

切换 UE5 的指令到达时，该 batch 尚处于退出阶段。按停止要求结束了仅本次启动的 PID 70116；包装脚本因此报告退出码 **-1**。这不是一次退出码 0 的完整 batch 验收，不应将终止后的进程结果描述为正常退出。

`Game/Logs/import-verification.json` 是 Unity 内实际执行生成的报告：8 个代表 FBX 有网格和渲染器，2 张调色纹理导入成功，Blender 测试模型的实际 Unity 世界包围盒为 **(1, 2, 1) 米**（Blender Z 向上映射到 Unity Y 向上）。此检查不认证动画、骨骼、材质视觉、碰撞或游戏可玩性。

本轮最终没有启动授权后的交互 Editor，没有 Unity 客户端连接 MCP 的证明，也没有执行 Play 探针或录像。之前排队的 Play 请求已改名为 `Game/Temp/CodexAutomation/play-proof.cancelled-ue5-20261010.txt`，防止后续误触发。

## 历史脚本和诊断

这些脚本仅供明确恢复 Unity 时参考，当前 UE5 路线不执行它们：

- `tools/scripts/unity-compile.ps1`：同项目无 Editor 时，batch 初始化并生成导入报告。
- `tools/scripts/unity-open.ps1`：交互启动，可选 `-PlayProof`；该历史脚本会尝试连接本机 Unity MCP。
- `tools/scripts/unity-status.ps1`：只读进程、workspace-status、运行探针与最新日志。
- `Assets/Editor/WorkspaceBootstrap.cs`：创建 Foundation，写编辑器状态；连接设置为 HTTP base `http://127.0.0.1:8080`，插件内部用 `ws://127.0.0.1:8080/hub/plugin`。AI 客户端端点为 `/mcp`。
- `Assets/Editor/ImportVerification.cs`：导入代表模型并记录网格/包围盒/纹理。

证据日志在 `Game/Logs/bootstrap-compile-2026-10-10.log`、`Game/Logs/editor-20261010-092708.log`、`Game/Logs/license-probe-2022.log`、`Game/Logs/compile-20261010-093149.log`。项目脚本经本机 Roslyn 语法解析、PowerShell 脚本经 Parser 解析均无语法错误；最终 C# 编译以 Unity 实际初始化日志为依据。没有截图或视频在此任务中展示。
