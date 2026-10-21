# 卡通暗黑童话六相步行试样 v001

2026-10-16，Asia/Shanghai。沿EV045/046/047及自动授权继续；本轮没有新增图像生成或外部API调用，计数仍145、window007为1/24、lifetime169，内置计费未知。

事实：唯一身份仍为131钟盔/琥珀眼公共身体。按原计划138/142/143/137/141/145六相顺序，把六张1254原稿无损拼成一行，每块逐像素等原稿；同次native去键/组件提取、全行416/1043共享缩放、atlas及curated得到v005。各帧高度416/407/411/410/408/413，没有逐帧归一化；原时序83ms×6=498ms保留。数值QA零警告/错误，但不代表运动衔接通过。

推理与纠错：全身bbox中心随摆臂和足展改变，原图相对稳定的盔部被额外横移。v005同色区域中心跨度12.5px。新v008在同一组件提取/共享fit阶段，用原1254画布中心627映射到输出256，横向位移−3/0/+9/+5/+5/+4；纵向底边、比例、姿势、顺序和时序全部保留。新六帧裁剪RGBA逐字等v005；对应native组件也逐字匹配原单图。相同色区测量的头中心为257.5/257.5/257/257/257/256，跨度1.5px。此色区仅是观察代理，不能认证刚性盔体、身体root或鞋底接触点。

真实失败保留：v006 curation误选不存在的plain twins，compose实际失败；v007取消variant后仍在integerX的BICUBIC变换中使少量半透明边RGB差1，裁剪RGBA严格断言实际失败。v008改为提取时直接placement，无二次affine重采样，六帧字节检查通过。未改已安装skill、未补画/插帧/重排/改时长。原共享fit的3项工具回归检查也实际通过。

展示前已保存：F盘 `过程图稿与视频/2026-10-16_暗黑童话六相步态基线_v001` 与 `2026-10-16_暗黑童话六相横坐标对照_v001`，原件/展示副本/来源和失败索引齐全；E盘对应v087/v088共147文件、59,374,482字节，两遍源/目标SHA和大小零差，E根README未改。Root在留档后实际看了v005/v008两张完整contactsheet；独立v005实际看完六帧。IAB已打开v008正式curation页并确认六帧正在播放，未把界面帧计数当作主观动态验收。GIF展示仅有80ms量化，不能替代83ms运行时manifest。

风险与下一步：摆臂快切、两半周期抬靴高度、passing下沉和5→0的形状/颜色微漂仍须实际播放与UE小尺寸观察。v008为完整来源序列试样，尚未导入UE、未完成动作/四甲/战斗适配或用户画风终批。下一步在独立造型预览中接入六帧，按72px目标高度检查左右朝向与循环；最新实际游戏仍v054四帧待机试样，原房间/迷雾/UI关闭。正式内容目标0/15不变。

源run：`source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/`；运行矩形/时序以其 `manifest.json` 为准，机械registration细节见 `frames/frames-manifest.json` 与 `source-cell-registration-receipt.json`。可重放工具为 `tools/scripts/register-fairytale-walk-source-cell-v002.py`（固定已存在版本不允许覆盖）；v001脚本是保留的失败试验，不能充作当前成功入口。

独立v008短审：`fairytale-six-phase-native-registration-v008-review-v001.md`，SHA `130640f6a80fd77540eded8ee6b84b46ba2e4fd0f4b5deaae4955e1ada6e030b`；实际看六curated，复核六裁剪RGBA不变及横向跨度12.5→1.5px。未播放GIF，仍不判完整动态通过或UE已接入；root已读并核SHA。
