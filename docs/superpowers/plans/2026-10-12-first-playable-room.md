# 首个可玩房间 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 在 UE5 中交付可直接试玩的单人 2.5D 战斗房间，贯通移动、跳跃、纵深命中、死亡掉落、拾取和清房出口。

**Architecture:** UE C++ Actor/Pawn 保存地面 X/Y、独立跳跃高度、战斗和物品状态；固定二维投影与按纵深排序的 Canvas HUD 呈现角色、场景和界面。采用本地 Blender 将已许可 CC0 模型转为透明序列帧，原型美术与最终画风分别记录。

**Tech Stack:** UE 5.5.4，C++，Blender 5.2.2，本地 PNG 转绘，PowerShell / UE Python 自动化。

**Spec:** `docs/2.5d-direction-2026-10-11.md`；`项目需求台账.md` EV-012～014。

## Global Constraints

- 项目主目录 `F:\Ourgame`；旧 E 工程和既有验证地图保留。
- 首版单人；长期完整武器、装备、道具和后续合作目标不以原型代替。
- 固定侧向构图；地面纵深与跳跃高度独立，按纵深判定攻击。
- 本轮不调用付费生成；原型使用已备 CC0 素材。
- 图像、视频展示前归档原件、展示副本、来源与状态；以实际运行证明交付。

## Review Focus

- 不同纵深的敌人不能被平面重叠误伤；离地攻击规则必须明确。
- 死亡只结算一次；重复攻击不能重复掉落。
- 斜向移动速度一致，角色不能越过房间边界。
- 满血药水不应浪费，武器切换需有可见差异。
- 死亡、清房和重开后输入及敌人状态正确；资源丢失有可读占位。

## Task 1: 核心玩法（slice_gameplay）

**Files:** `DungeonFighter.h/.cpp`、`DungeonGameMode.h/.cpp`、`Tests/DungeonCombatTests.cpp`。
**Interfaces:** `ADungeonFighter` 提供位置、生命、朝向、跳高、动画、武器；`ADungeonGameMode` 提供敌人、拾取物、清房状态及交互入口。最终字段以头文件为准，修改接口先同步 HUD 实作者。

- [x] 写出纵深 / 朝向 / 离地命中和拾取边界的失败测试，记录失败原因。
- [x] 实现 WASD / 方向键移动、Space 跳跃、J 攻击、E 拾取/出口、Q 武器切换、R 重开。
- [x] 实现敌人追击与攻击、受击无敌窗口、死亡一次性掉落、三敌清房和出口。
- [x] 构建并运行引擎自动测试，补充真实运行检查。

## Task 2: 本地二维角色资源（slice_sprites）

**Files:** `tools/scripts/render-prototype-sprites.py`、`source-assets/prototype/first-room-v1/`。
**Interfaces:** human/orc 各 idle/walk/attack/hurt/death 顺序 PNG，统一画布与落脚点，JSON 来源/帧率/动作清单；根实现负责导入 UE。

- [x] 检查 CC0 来源和 Blender 动作，固定相机、尺寸和透明输出。
- [x] 转绘两角色动作，验证透明、非空、站姿、朝向和落脚点。
- [x] 原件/展示副本归档，再审阅样帧；保留来源、许可和生成参数。

## Task 3: 可见房间与运行入口（root）

**Files:** `DungeonHUD.h/.cpp`、Config、`tools/scripts/prepare-first-room.py`、`play-first-room.ps1`、运行验证脚本。
**Interfaces:** 消费 Task 1 公开状态和 Task 2 PNG；创建 `/Game/Maps/FirstRoom`，使用 `ADungeonGameMode` / `ADungeonHUD`。

- [x] 实现分层地牢、角色纵深排序、接地影子、攻击/受击反馈、生命/金币/武器/操作说明及清房提示。
- [x] 导入序列帧与中文字体，保存新地图，编译实际 F 工程。
- [x] 启动图形运行，验证命中、错层不命中、掉落拾取、清房与重开；捕获运行证明并审阅。
- [x] 更新 README 资产尺寸/来源、需求台账和运行报告，独立审查后修复关键问题。

## 执行记录

- 2026-10-12：用户“开始制作”授权执行既定 2.5D 首个切片。本轮直接执行，不再次询问相同范围的确认。
- 当前分支 `codex/preparation` 尚无提交与 Git 作者配置；不代造身份，保留本地源码和可运行文件。
- 此计划用于当前已授权制作的执行记录；不将本轮默认数值、原型画风视为用户最终验收。

### 完成证据与边界

- 最终 Editor 构建：2026-10-12 20:13，exit 0；纯规则 11 项检查全部通过；UE 自动化 2/2 成功（含受击无敌窗口）。
- 图形运行：v004 19 项世界 / 控制器检查通过，578 连续帧，固定 30 FPS 模拟；录像完整解码，移动 / 跳跃、战斗和清房样帧已审阅。原型美术与平衡未视为用户最终验收。
- 审查修复：出口测试夹具验证拾取优先再退出；自动演示改走 PlayerController::InputKey，行走动画实测；录像验证脚本在失败报告、少帧或缺报告时返回非零。
- 规则：正常启动停在 Enter 开始界面；此版本依赖本机已安装 UE5.5，未打包独立发行 exe。
- 延后小项：转绘 v1 源目录当前视为不可变；后续重转绘需要新版本或显式导入替换与原始导入哈希比较，不能复用旧资产宣称重导成功。
- Git 尚未设置作者且无初始提交；保留本地工程与证据，不伪造作者或提交历史。
