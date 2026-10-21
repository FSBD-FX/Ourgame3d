# Air48 finite native import tooling candidate v001

本目录只有工具、保留的合成测试和只读验证记录。尚未运行UE或导入任何纹理；不写实际Source/Content、Root输出目录、E留档或需求台账。

目标是旧Production1371原文件大小/SHA不变，8层×6相新增48 Texture2D，最终精确1419。命名空间固定 `/Game/Production/ArtTrials/EV048/v020/HeroLeatherAir6`。军剑复用旧独立对象，不导入任何剑、组合整图或烘焙持剑层。

`air48_import_contract_v001.py` 验证实际源512RGBA、解码RGBA SHA、非空alpha及统计，canonical source49闭包、61成员冻结闭包、Root有限导入批准、真实v002 E索引/ZIP全成员/F原件两遍字节与SHA一致。没有独立E PNG路径。若批准提供E600，则另核源准备包中48PNG、旧剑源、manifest、freeze、canonical descriptor及typed Data真实ZIP成员。输入使用Root实际schema `Root-Air48-limited-source-import-approval-v001`；不会创建或猜测Root批准。

`prepare-Air48-Root-import-v001.py` 的纯源验证模式不需批准、不写输出。实际准备需Root批准和固定SHA的Source292/Production1371快照；只在新目录生成host解码回执和import-manifest。原生UE嵌入Python不要求Pillow，但绑定此确切host解码回执、当前工具pins，并重新核验源文件/冻结/E ZIP。

`ue-import-hero-Air48-v001.py` 默认不导入。原生模式在任何变更前exclusive创建claim，检查UE项目、空registry/disk namespace、旧1371两SHA及精确成员，读取旧剑原生Texture2D512但不改/不存它。新48实际检查类、objectpath、尺寸、sourceimport文件名、TC_EDITOR_ICON/NO_MIPMAPS/UI/neverstream/sRGB/bilinear读回，再保存。失败保留所有partial包、claim、receipt和日志，不回滚、不重试。

`import-hero-Air48-v001.ps1` 先host预检，拒绝已有UE/UBT，开独立Hidden顺序进程。原生成功回执后才执行独立host saved-byte两遍核验旧1371+新48的大小/SHA/精确成员；host独立检查读回回执合同，不冒称又进UE重新读取原生metadata，更不代表49GPU、绘制、动作或美术验收。

边界：UE SavePackage自身没有原子CREATE_NEW；使用空新namespace、replace_existing=false和每个save前目标不存在检查，仍依赖Root禁止外部并发编辑/写入。不能声称可阻止检查后外部进程抢写。所有JSON则以exclusive create、flush/fsync写入，失败不覆盖原件。

## Root执行顺序（本候选没有执行这些写入/UE命令）

```powershell
$airTools='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\import-tooling-candidate-v001'
$airSources='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\native-ready-candidate-v001'
$airApproval='F:\Ourgame\docs\production\first-batch-v2\evidence\HeroAir6-v142-v001\Root-Air48-limited-import-v001\Root-source-approval-v001.json'
$airBaseline='F:\Ourgame\source-assets\production\backups\v142-HeroAir6-Baseline292-200G3R-v001\compiled-source-manifest.json'
$airOut='F:\Ourgame\source-assets\production\fairytale-hero-air-v001\Root-Air48-import-v001'
$airPython='F:\Ourgame\tools\runtime\asset-gen\Scripts\python.exe'
& $airPython -B -X utf8 "$airTools\prepare-Air48-Root-import-v001.py" --source-manifest "$airSources\import-Air48-v001.json" --source-freeze "$airSources\Air48-native-ready-freeze-v001.json" --source-approval $airApproval --old-snapshot $airBaseline --output-dir $airOut
if($LASTEXITCODE -ne 0){throw 'Air48 preparation failed; preserve outputs'}
& "$airTools\import-hero-Air48-v001.ps1" -Manifest "$airOut\import-manifest.json" -ValidateOnly
# Root审查当前原件与输出后才执行：
& "$airTools\import-hero-Air48-v001.ps1" -Manifest "$airOut\import-manifest.json"
```

输出目录必须不存在，位于production source-assets且不在已冻结source候选内。任何失败换新版本诊断，禁止删旧目录或原地重试。上述变量只供Root实际执行；本次没有创建Root-Air48-import-v001。

## Host测试

`test_air48_import_contract_v001.py` 在本工具目录的新validation-runs生成合成512PNG、真实ZIP字节结构、假Production包字节及明确标为SYNTHETIC的批准/metadata字段。覆盖缺48、重复/越界/ADS/UNC/保留名/控制字符路径、错误counts/相位bool、RGBA/alpha、伪E声明/缺ZIP成员、冻结漏项、错误baseline、审批范围、receipt类/尺寸/来源/设置、exclusive输出、旧成员及独立saved-byte正负例。合成包绝不是原生UE资产证明。

最早 `host-contract-20261018-163952-350453` 是测试fixture过长路径失败原件，保留。`t164016487930` 是中间24case运行，运行中工具扩充，不用作最终冻结的验证结论。最终有效run应由freeze的accepted_host_result pin唯一指定，并要求sources_unchanged_while_running=true。

`t164158637103` 的第25项暴露独立verifier测试注入root未传至metadata/旧文件检查，已显式传ROOT修复；该失败回执及合成原件仍保留，不纳入最终PASS。

`t164327704749` 已25/25通过并固定源pins；随后依Root只读审查建议，先保全pre-bytecode-fix-source-v001旧importer原件，才在本地contract import前设置sys.dont_write_bytecode=True。最终新增第26项使用无-B新Python子进程实际验证不会向冻结工具目录写__pycache；最终结果由freeze pin指定，旧25项run继续保留。

Root基线 `4f55684c...2fb85d`、批准 `b403264d...f4fe9`、native-ready manifest `1cd238d8...5f32c`、freeze `e3786b74...fea7` 仅作读取依据。工具冻结记录完整pin，不把历史Dodge32数量/路径当本轮事实。
