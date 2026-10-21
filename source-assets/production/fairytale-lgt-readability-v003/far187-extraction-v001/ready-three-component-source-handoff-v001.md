# Ready 四帧三组件 Source 清单

详见 `ready-three-component-source-list-v001.json`：Chest184 / Near186 / Far187 各四张共同scale诊断PNG及Body158、既有BodyRest/NearArmWithoutHand/NearHand、原ownership masks，均记录SHA。所有新甲 A / Body target B / integer delta仍null，等待Root实际测量提供，不能用bbox中心或旧灰甲特征自动填值。

旧binary ownership masks只记录源RGBA归属，不是盔甲可覆盖区域/隐藏关节/头盔手指保护语义的验收；旧设计site有不确定性，不能冒充新B。预期层序BodyRest→FarShoulder→Chest→NearArmWithoutHand→NearShoulder→Sword→NearHand，Sword仍由Root独立处理。

没有新合成、整数贴合、mask改写或试装PNG。Root先E保全并查看诊断部件，再以实际A/B决定整数translation；完整保留共同Body158和三旧body层像素。
