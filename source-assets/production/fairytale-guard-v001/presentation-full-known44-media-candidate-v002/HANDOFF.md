# AxeCycle media v002：仅兼容两个精确冻结工具输入

保留media v001与首次launcher索引失败。NEW v002只接收session.native schema v001/scenario=AxeCycle、成功 `independent-known44-AxeCycle-v002.json`，工具冻结白名单恰两件：

- tooling-v002：`2a5579483e4e5f0eab1da02a3492909e4f8d7d38a9f64d6472498dfed84e5b1d`
- tooling-v003：`09447cf8c83c1d6db964f043bb39a5cc06ce814dcd04bcf34eb65603c0234906`

两原freeze本身均按精确path/bytes/SHA验证；session只可匹配其中一件，其他hash拒绝。另核磁盘session PID与native report一致；修正后的原v002失败capture可在Root原件独立重核成功后使用，不能跳过重核或把第一次失败隐去。

其余24合格样本／同首Aid／join资格、v011微秒PTS／帧数cap／framemd5时间舍入上界／decoded-last规则不改。输出文件名仅换v002，不改原PNG/report/index。索引/README仍要求未存在，防覆盖旧媒体；如已经生成旧presentation，Root须另规划新的展示目录版本而非删除旧原件。

命令：项目Python `-B -X utf8` 执行本目录 `tooling/prepare-known44-native-media-v002.py --archive <absolute actual capture> [--validate-only]`。去掉validate-only才编码完整静音录像、copy24原幅PNG与join pair。新产物必须Root E保全后View；本候选未执行UE/ffmpeg/View，无新媒体或最终验收。
