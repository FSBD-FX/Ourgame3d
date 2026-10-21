# Request260 轻甲整数试装候选 v001

范围：12 个既有轻甲 PNG 的512画布整数平移，4张四身体owner参与的无剑诊断装配。未调用图像生成，未看图，未改实际 Source / Content / tools / E盘 / ledger / status。Root 已允许260内部层准备；本候选没有正式美术接受。

| K帧 | 真实既有甲源 | ShoulderFar ΔXY | Chest ΔXY | ShoulderNear ΔXY |
|---|---|---|---|---|
| K0 | Ready0 / EV048 v012 | +6,+2 | +1,+1 | 0,0 |
| K1 | Request258 J1 / 已内部接入新14 | -9,-16 | -15,-12 | -19,-30 |
| K2 | Request258 J1 / 已内部接入新14 | +2,-14 | -8,-12 | -7,-42 |
| K3 | old J2 / EV048 v013 | -112,-40 | -15,-18 | +50,-14 |

每个选择的原PNG路径、SHA、真实object_path、source feature坐标及RGBA、原/新bbox、手/头/布料交集均有JSON逐层记录。源上扣饰/缝线/甲片尖端是既有可见特征；新位置是未经目视的数字布料候选，不能解释为测得的骨骼挂点。

12层无旋转、无缩放、无warp、无补洞、无颜色或alpha修改；逐RGBA逆平移完全一致；裁掉非零RGBA=0。4帧身体owner逐RGBA排他重组完全一致；独立验证重新合成4装配一致。输入41个pins两遍核验0差异。

无剑装配顺序：BodyRest → ShoulderFar → Chest → NearArmWithoutHand → ShoulderNear → HelmetForeground → NearHand。正式8slot中的 IndependentSword 未加入；K Grip / Axis 没有借用旧J标记。NearHand最后恢复，far手保留BodyRest。

四帧最终 near-hand supplied owner 与 far-hand warm-hull supplied heuristic 区域 RGBA变化均0。Chest原始 near-owner交集为K0=989、K1=0、K2=0、K3=617px；这些是源层交叠，被正确晚绘的NearHand恢复，不能错误汇报为原始无交叠。所有Chest alpha128悬空0。肩甲alpha128悬空：K0far3、K1far4/near12、K2far19，其余0；原像素完整保留，不截去这些边缘来凑数字。

待Root确认：K3旧J2甲片朝向未变，不能仅靠平移保证前倾透视适配。K2 near肩与HelmetForeground原交集175px；K3 Chest281 / near肩434px，按晚绘头盔保留。K1/K2手盔距离原图很近，身体owner语义边界尚未批准；far手mask仅暖色凸包+4px的启发式保护，0变化不等于完整手轮廓证明。整套wear fit / 动作连续性 / GPU / native / 音效均OPEN。

先由Root按项目保全流程保存F原件与展示副本、E副本与索引，再View `diagnostic-assembly-no-sword/K0..3.png`；本代理未展示媒体。若肩甲方向或袖胸分界不合适，保留当前候选作失败依据，不能强行宣称通过。

只读复验（不会写冻结目录）：

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/request260-LGT-fit-candidate-v001/verify-LGT-fit-source-closure-v001.py' --check-only
```
