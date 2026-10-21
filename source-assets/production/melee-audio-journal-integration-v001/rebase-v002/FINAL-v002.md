# 使用final v002候选（未应用）

本轮最终入口：[production-rebased-final-v002.patch](production-rebased-final-v002.patch)、[baseline-final-v002.json](baseline-final-v002.json)、[git-apply-check-final-v002.json](git-apply-check-final-v002.json)。仍3文件4hunk，仅HUD位置重生成，Fighter/World逻辑与原v001相同；3tests原c2de7b0a文件未改且关联在baseline。

首轮production-rebased-v002.patch统一CRLF，普通git apply --check拒绝原生LF的World文件；原patch/基线/失败结果完整保留。最终patch以字节写出，Fighter/HUD上下文保原CRLF、World上下文保原LF，未使用ignore-whitespace绕门。最终实际结果见final JSON，不能以首轮失败误称C++/游戏行为RED。

未应用ActualSource、未UE/UBT，旧v001候选和当前Source均未改。Root先实际3组语义RED再准入此patch；git check通过仅是补丁可应用证据，不是C++、声音或运行GREEN。Root后续若改同一HUD区，仍需再次检查小hunk，不恢复整文件。
