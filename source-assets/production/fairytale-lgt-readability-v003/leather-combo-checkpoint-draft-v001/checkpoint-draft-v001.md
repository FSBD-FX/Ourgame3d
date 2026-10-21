# EV048 软皮轻甲三连斩检查点草稿

记录日期：2026-10-17。供 Root 更新项目文档；本稿未改 README、生成账本、源码或旧证据。用户尚未最终接受美术，正式完整内容单元仍为 0。

## 事实

新版软皮轻甲已覆盖待机及军剑三段普通攻击。本次 `diag_v002` 用正常 Enter／E／A取消／E 完成一次实际轻甲提交，再分别向左右执行正常 J 三段连击，间隔经过真实连击链过期与转向。168 条原生观测、169 张 PNG，左右各三段六相全部覆盖，六个不同 AttackId 1–6，收招后 Ready 计数为左15／右3；`passed=true`、mismatch=0。旧 `diag_v001` 的首次使用缺图 RED 原样保留，本次重录未复现该问题。

原生帧逐项绑定 CRC／FIFO／异步停止刷新；1348 个 Source／Config／DLL 等输入与 1151 个 Production 包合同核对零差。5.601 秒墙钟过程已制成约5.6秒 CFR30 静音视频并完整解码；浏览器播至结束，error=null。以上为限定三连斩美术诊断证明，本批 `current_full_GREEN=false`、automation=null，既有 Guard 三项 Capture 语义 RED 保留，不替代全套验证、默认试玩或音频验收。

依据：[原生报告](F:/Ourgame/过程图稿与视频/2026-10-17_NONRELEASE软皮连招美术诊断_diag_v002/原件/runtime-report.json)、[独立验证](F:/Ourgame/过程图稿与视频/2026-10-17_NONRELEASE软皮连招美术诊断_diag_v002/原件/independent-leather-combo-verification-v001.json)、[源绑定](F:/Ourgame/过程图稿与视频/2026-10-17_NONRELEASE软皮连招美术诊断_diag_v002/原件/leather-combo-source-binding-verification-v001.json)、[浏览器播放记录](F:/Ourgame/过程图稿与视频/2026-10-17_软皮三连斩浏览器播放复核_v001/原件/playback.json)。

## 可见结论

继续采用暗黑童话、卡通怪诞的手绘方向：钟盔冒险者、72px 小比例、暖棕软皮胸甲与短肩片、独立军剑 .50，传统 HUD 隐藏。Root 在 E315 保留后实际查看六张左右三段联系图（共36张原生240×160局部）与1280×720整场，确认暖棕胸甲、短肩片及钟盔发光眼辨识更明确，第二段上斩与第三段低扫有区别；本次未见首次使用缺图。E316 保留后又检查播放器结束截图和播放记录。

此段为 Root 本轮协作消息确认的观察；本子任务没有再次查看媒体。E315 旧索引中的 `visual_review_pending` 保持历史时点，不能倒改成当时已经审阅。Root 审阅也不等于用户最终接受。

画面与长期留档：[F盘整场与36相复核](F:/Ourgame/过程图稿与视频/2026-10-17_NONRELEASE软皮连招美术诊断_diag_v002/展示副本/leather-combo-whole-phase-view-v001.html)、[F盘静音录像](F:/Ourgame/过程图稿与视频/2026-10-17_NONRELEASE软皮连招美术诊断_diag_v002/展示副本/leather-combo-trial-silent.mp4)、[E315 原生留档](E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-combo-native-v315)、[E316 播放复核留档](E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-combo-browser-v316)。

## 未完成动作与下一步

薄剑、握柄／拇指、甲片接缝与挥砍净空仍须连续运动复核；移动、换装完整过程、受击、死亡、闪避、空中与其他武器／防具组合的新风格适配尚未完成。特效、连击反馈、音效与听感、合法掉落／商店来源及存档延续也不能由本片推定通过。

先以这次原比例实景和录像确定方向、标出握柄／接缝问题；随后补完缺失状态及动作衔接，再做全套装备适配与真实战斗视听验收。另行完成生产代码全套验证并绑定新 DLL／Source 后，才能推进正式原生证明；本诊断片保持独立。

## 193–198 生成账本建议

六行均已完成真实生成留档、标准提取／curated 导出、整数装配、每行6张Texture导入，并在本次左右三段原生证明中实际使用。建议统一追加阶段状态 **`native_combo_trial_verified_pending_user_acceptance`**；保留原生成收据和失败记录，不改成 final／完整动画／完整装备通过。

| 生成号 | 部件 | 已完成范围 | 必须保留的边界 |
|---:|---|---|---|
| 193 | 第二段胸甲 | 六相提取→整数装配→v014导入→左右原生覆盖 | 适配与连续运动仍trial |
| 194 | 第二段近肩 | 六相提取→整数装配→v014导入→左右原生覆盖 | 语义遮挡与接缝待复核 |
| 195 | 第二段远肩 | 六相提取→整数装配→v014导入→左右原生覆盖 | 单行显式min160／core≥128；保留512／256失败，不泛化放宽 |
| 196 | 第三段胸甲 | 六相提取→整数装配→v015导入→左右原生覆盖 | 实际Body175为run-primary3-v001，索引旧错名更正另存 |
| 197 | 第三段近肩 | 六相提取→整数装配→v015导入→左右原生覆盖 | 原动作形变／遮挡未最终接受 |
| 198 | 第三段远肩 | 六相提取→整数装配→v015导入→左右原生覆盖 | 保留2109×745原图、共同行scale与显式小部件门 |

阶段依据：[第二段18源索引](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/primary2-far195-small-tab-v002/primary2-eighteen-source-index-v002.json)、[第三段18源更正索引](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/primary3-leather-extraction-v001/primary3-eighteen-source-index-v002.json)、[第二段装配](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/primary2-integer-assembly-v001/assembly-proof-v001.json)、[第三段装配](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/primary3-integer-assembly-v001/assembly-proof-v001.json)、[真实联合导入证明](F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003/combo-import-v001/joint-import-proof-v001.json)。装配中的隐藏挂点 B 仍是 artist TRIAL；零裁切、RGBA可逆和旧身体字节相等不是语义遮挡或完整美术验收。
