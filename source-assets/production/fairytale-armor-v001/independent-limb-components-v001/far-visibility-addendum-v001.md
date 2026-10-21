# Far shoulder visibility and layering boundary

2026-10-16。补充root在原输入冻结后的明确遮挡要求；原26文件与preparation-freeze-v001.json保持，不覆盖任何既有稿。

Native right-facing+1时，far是图右、处于头盔/躯干后的真实远肩。其target mount0/1/2/3为[296,255]/[296,253]/[296,256]/[296,255]；lower-rim support为[302,275]/[302,273]/[302,276]/[302,275]。它们是实际查看131后的衣服设计挂接点，RGBA和歧义在数值合同，不是推算骨点。头盔遮住肩的上方，far可见甲应该是头盔下缘以下的窄压缩弧面，向右下走到上臂，不画完整对称肩球或连到脖子/脸部的顶盖。

当前131仍完整一层。只在生成件**实际可见轮廓完全避开头盔/颈/手**时，空手idle可以body→chest→visible-far-cap/visible-near-cap观察；samequad只是坐标变换一致，不会自动解决遮挡。farcap不能先画在whole131下面、被全盖住，却以TextureReady=true宣称已显示；画在whole131上也不能压住头盔、脸或颈圈。

若原生生成的cap真实轮廓穿过头盔/躯干，保留原稿并拒绝该直接overlay试装；需要按同131真实RGBA建立binary ownership partition或正确源像素occluder，再以精确重构和实际可见像素证明解决。不能搬旧style mask、修改131轮廓、裁掉甲片假装本来没有交叉、画假桥或把近肩镜像成远肩。遮挡不接受时不能仅因为4组件/0warnings就放行。

56x44与32x40始终只是可审的near/far尺寸窗口，不是生成前已经量过的适配结果。四帧应分别量真实mount rivet与lower-rim，不换feature、逐帧缩放、旋转或warping。后续护腕/护胫同样要按真实身体肢体各自坐标和可见深度生产，不可复制一件充当near/far。
