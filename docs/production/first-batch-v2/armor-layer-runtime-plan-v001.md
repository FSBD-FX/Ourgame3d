# 四甲真实分层运行接入

2026-10-15，Asia/Shanghai。上一目标回合已取得实际strictUE38、normalE/Q9、Explore26；本回合继续制作完整15单元，不重新定义完成范围。根负责HUD/资源导入/Probe及统一UE运行；ranged_adapter负责Actor远程接线，ranged_review独立新测试，assets_prepare仍是唯一视觉写入者。

事实：独立v008已有60idle纹理（12共用身体、48真实甲前后层），P1四甲扩展刚冻结36纹理（12共用身体、24甲front），没有独立可见背面，合同明确null而非空白伪造层；现HUD仍只画旧整身。此前贴身足迹口径一致，不能为视觉分离放大碰撞使90cm盾击不可达。

裁定：先把实际存在的idle/P1组件接入显式 `DungeonArmorLayerPreview`，保持原默认QA/38/Explore26；缺失动作仍明确用旧候选并记录实际层是否使用，不能算完整四甲完成。此暂时兼容会有全状态外观断层，须继续逐clip替换，而不是把两clip当验收终点。无甲省甲层，四甲始终复用同一body，HUD只读真实ArmorId，不改库存或属性。

绘制顺序为可见back→common far→armor front→独立剑→common near，所有层512原画布/同Root，整体一次镜像；读取冻结Root/Grip/Angle/时段，不做各帧bbox重fit。P1null back原样跳过。Sword不再从旧整身ROI重放近手，而由真正near层覆盖；实际被遮挡材质采所有已画层，不能显示一个没装备的旧甲轮廓。

导入P1用独立v009目录，核对冻结manifest SHA、36实际PNG/alpha/四角/源hash/时段、每项Texture2D配置与保存回执，拒绝覆盖旧资源。idle/P1的实际layer paths/使用标志供Probe只读记录。实际源注册E换甲和左右J第一段驱动一次演示，不能HUD直接换ArmorId充作交互成功。

运行门：原38和远程新增组以真实注册数量核对；组件预览另做正常E/方向/Enter/J/A/D实录，记录前后装甲身份/层路径/源hash。先F/E保全再审看各甲、无甲、左右、第一段与回待机；源选区细边和缺失clip全部列限制，正式0/15保持直至全动作/20搭配/反馈/来源/存档验收。
