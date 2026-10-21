# Native161宽胸候选：raw同向，挂点待实测

2026-10-16，scale_tests。E153后独立view原2171×724 raw（工具显示缩至2048×683，未据显示图量精确挂点）。四片均与正向160C0同样3/4透视，较大近带/侧开口在image-LEFT，压缩远侧在image-RIGHT；四片都有单独中央raised round boss，较旧160更横宽。这里只确认raw候选方向/可辨feature存在，不接受四帧fit、位置或动作；160失败全保留，无局部mirror。

本次标准shared-row extract→atlas→curated→preview，无逐帧scale/rotate/warp，原request4×167ms/raw不改。标准preview实现由fps计算统一duration，GIF10ms单位也不能编码精确167ms，因此结构preview文件并非request时序证明；actual GIF metadata另列，未播放、未重定时，不能拿它认证运行循环节奏。

新curated/诊断/QA先freeze等待新E保全开放才显式view。四片actual中央boss A仍null，必须看真实绘制圆boss边界取中心，不能bbox-center、highlight中心或side strapbolt替代。随后如获准，仅将实际A整数平移至158衣面设计target[259271等]±3px，保存独立registered文件，原curated与共同ratio不变。无导入/UE/Source/台账/新native调用，完整内容0/15。
