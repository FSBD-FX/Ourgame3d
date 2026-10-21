# 清理前保全与待执行清单 · 2026-10-21

当前状态：**自动批量目录删除被执行工具策略拦截，尚未删除任何文件，本轮释放空间为0。** 返回理由仅为 `blocked by policy`。人工清理脚本尚未执行，默认仅预览。

## 还需要保存什么

以下已经补存，无需再复制一份完整旧工程：

1. G当前工程相对10/20 active基线的新增/修改：`G-current-project-delta-v001.zip`，426文件，原8,653,005字节，ZIP 2,545,817字节；逐成员SHA已独立复核。包括request264原图/提示词/QC、生成账本、便携启动入口、README/需求/进度/迁移文档及G203运行证据。恢复时先恢复原active四包，再覆盖本增量。
2. 原迁移备份文件夹以外的G归档索引与关键节点：`G-archive-index-and-key-checkpoints-v001.zip`，94文件，原328,897,197字节，ZIP 98,170,512字节；原件与解压成员SHA一致。包含军剑K原生视频和原始采集ZIP、AirJ参考及来源索引、盘点清单、留档政策和.monitor，不重复打包已保存的active/history。
3. 本目录的两个complete回执、清理状态JSON、核验材料和人工脚本一起保留。

以上暂存C盘，原因是G仅剩约0.4MB。工作工程仍为G:/Ourgame。旧备份G:/OurGameArchive/2026-10-20_Ourgame迁移前备份_v001继续保留。

## 经核对可清理的范围

- F:/Ourgame/过程图稿与视频；F:/Ourgame/Game；F下乱码pendingRED旧失败目录：共175.80GiB，113,419文件，当前路径/大小/修改时间与已验证清单完全一致。22个历史ZIP新鲜整体SHA全匹配。元数据快捷比对不能识别刻意同时保留尺寸和时间戳的内容修改。
- F:/Ourgame/UnrealGame/Intermediate 与 F:/Ourgame/UnrealGame/Plugins/UnrealMCP/Intermediate：共2.68GiB，可重建。
- G:/Ourgame/UnrealGame/Intermediate：36.79MiB，可重建。
- G:/Ourgame/tools/runtime/migration-backups/2026-10-12：2.20GiB，两个隔离旧E绝对路径的Intermediate缓存备份；149文件，来源说明与1808编译清单排除均已核对。

预计F释放178.49GiB，G释放2.24GiB。这些都是**潜在值，不是已释放**。即便完成这些清理，G空间仍很紧；G:/knight、G:/game属于另一个聊天的Godot项目，本次未处理；其他软件、引擎安装也未处理。

## 人工执行

打开PowerShell，先运行本目录的 `人工执行清理.ps1` 预览；带 `-Apply` 才实际删除。关闭UE/UBT及F旧目录复制、解压、编辑任务，执行期间保持这些目录无写入。

脚本在任何删除前重新校验完整22 history+4 active包、增量备份和F历史目录，检查精确7目标及祖先/子项的reparse边界；发现新增、变更、备份损坏或路径问题会拒绝继续。执行后在核验材料中新建用户执行回执。

不删除：G工作工程Source/Content/Config/Binaries/插件/源素材、Saved整体、迁移备份包、独有旧E材料、F剩余开发副本、其他项目。删除缓存后首次编译/派生数据生成耗时可能增加。

20GiB容量档位仅在正常汇报顺带提示，不是停工/授权条件；本次删除未执行是工具策略拦截，与容量档位无关。
