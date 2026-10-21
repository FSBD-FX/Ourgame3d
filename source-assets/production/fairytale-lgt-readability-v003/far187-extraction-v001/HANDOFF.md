# Far187 提取诊断 v001

- standard-baseline: extract exit 1; inspect exit 1; frames 0; manifest ok=None; inspect ok=False.
- shared-diagnostic: extract exit 1; inspect exit 1; frames 0; manifest ok=None; inspect ok=False.

标准 extract 的逐帧 fit 基线与既有项目共同 scale hook 结果分开保存；共同版调用同一安装标准 extractor 的 chroma、components、QA 路径，仅替换已锁定的 HD fit hook，没有修改安装工具。所有原始输入按字节保留，没有新 prepare 或输入字段改写。

供 Root 未来逐像素检查的是 `run-shared-diagnostic-v001/frames/`。原生187现在保留窄弯右缘tab，组件边缘仍需 Root 实际像素检查，组件语义、mask、实际fit、A及动画均未验收；全部 A=null。没有生成、导入、UE、ledger、人工裁切/绘制，也未浏览/截图新输出。Root 必须先 E 归档再查看。

详见 `numeric-diagnostic-v001.json` 的真实命令、退出码、共同 scale 与每帧尺寸 / alpha / 颜色数；不得把自动 QA 等同于最终装备通过。
