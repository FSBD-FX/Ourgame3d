# Air48 importer v002: confirmed asynchronous texture placeholder repair

Root真实UE只读诊断确认旧军剑在compiling时尺寸32×32，执行 `Editor.AsyncTextureCompilationFinishAll` 后512×512，纹理设置相同，旧uasset大小/SHA不变，0import/0save。v001实际失败发生在48tasks创建前；失败run、v001冻结和原件全部保留。

本NEW v002复制v001同名5工具，contract/preparer/launcher/26case source逐字节不改；只修改UE importer增加真实编译finish barrier。旧剑尺寸门前、每个新Texture尺寸门前、设置更改后的最终读回/保存前均调用本机实际命令，回执记录texture/stage/before_dimensions/command/command_requested/after_dimensions；after仍严格512×512，否则保留失败。void命令不冒充编译完成ack，以实际after尺寸检验。

Root须新建准备输出目录，使用本v002目录下同名prepare及launcher。不能复用v001已失败Root输出/run/claim；只能在旧1371两SHA/精确成员未变且新namespace仍不存在时重试。manifest命名空间和48源身份不变，不导入军剑，不改actualSource/Content/E/ledger，实际执行仍由Root独占。

旧v00126/26结果只作为未改contract/prepare/metadata/byte-verifier基础合同证据绑定；本轮独立mock测试执行实际v002 native()函数，注入明确synthetic的Unreal API以检查编译命令先于真实尺寸门/保存、错误尺寸继续拒绝和异常回执保全。Mock不是UE运行/原生资产证明；此候选不宣称实际重试或保存已通过。

```powershell
$airTools='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\import-tooling-candidate-v002'
$airSources='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\native-ready-candidate-v001'
$airApproval='F:\Ourgame\docs\production\first-batch-v2\evidence\HeroAir6-v142-v001\Root-Air48-limited-import-v001\Root-source-approval-v001.json'
$airBaseline='F:\Ourgame\source-assets\production\backups\v142-HeroAir6-Baseline292-200G3R-v001\compiled-source-manifest.json'
$airOut='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\Root-Air48-import-v002'
$airPython='F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe'
& $airPython -B -X utf8 "$airTools\prepare-Air48-Root-import-v001.py" --source-manifest "$airSources\import-Air48-v001.json" --source-freeze "$airSources\Air48-native-ready-freeze-v001.json" --source-approval $airApproval --old-snapshot $airBaseline --output-dir $airOut
if($LASTEXITCODE -ne 0){throw 'Air48 v002 preparation failed; preserve outputs'}
& "$airTools\import-hero-Air48-v001.ps1" -Manifest "$airOut\import-manifest.json" -ValidateOnly
# Root复核新输出后，再执行同一launcher，不传ValidateOnly。
```

UE SavePackage仍无原子CREATE_NEW：保持独立顺序进程、空namespace、replace_existing=false、每次save前目标不存在门，Root禁止外部并发写。JSON/claim/receipt exclusive create和失败不覆写规则不变。
