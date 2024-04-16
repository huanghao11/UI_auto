1、文字识别部署参考：https://blog.csdn.net/weixin_43545322/article/details/108695021和https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/quickstart.md
其中在部署本地或服务端时，代码可能会出错，可能是json文件的key因为版本没对应，debug后修改即可
2、demo.py文件中基本演示了所有的UI自动化在文字和图像上的匹配功能
3、文字识别算法和子图匹配功能是UI自动化的核心，如果仍未完成需求，可以考虑使用开源的yolov8目标检测算法，但是前期打标训练成本巨大，但是准确率高，不是无奈之举不推荐使用。
4、项目中写死了一些图片路径，进行更改即可

UI自动化背景：
在业务测试中，需要大量人力去进行回归，uiauto使用xpath定位不准。
考虑从文字识别和图像识别的角度，去实现元素的点击和断言
实现功能：
文字：
对于回归流程中，需要实现特定文字的点击，以及页面上特定文字的断言。
1、判断文字在图片中是否存在
2、判断文字在选定区域中是否存在（避免背景等影响）
3、判断文字在选定区域之外是否存在（排除banner图等对页面的断言）
4、对于tab锚定框，可以判断当前文字是否锚定
5、对于文字的点击，可以返回图片中第n个文字的中心坐标，起始坐标为1
图片：
1、传入多张子图，如果存在其中之一则返回True，适用于同一种ui多种样式
2、输出第一个匹配的子图的中心坐标及其宽度和高度
3、演示一下元素分割，直观化
4、图片中存在多个一样的子图，传统的Sift特征匹配会失效，结合元素分割，可以实现限定宽度和高度的元素区域来匹配（减少了全部分割元素的匹配，与返回的子图宽度和高度结合），可以返回所有匹配子图的坐标（实现了可视化）
5、可以毕竟任意文字与文字，文字与图片，图片与图片之间的位置关系，包括空间方位和距离限制，对于子图也限定了宽度和高度，防止元素分割的区域同时也包含了待匹配子图
6、可以检测黑白灰屏，其中怎么判断黑白灰屏，可以传入占屏比阈值
7、可以判断两张图片的结构相似度，可以去除颜色的差异，防止因为屏幕色温等影响
8、判断两种图片结构是否一样，与文字无关
关键点：
1、Sift特征匹配用来匹配子图，以及在判断结构相似中选取特征点。Sift相比模板匹配拥有尺度不变性，旋转不变性，光照不变性，但是计算量较大。
2、文字匹配上实现了本地pp-ocrv3模型部署和服务端的接口部署。
3、对于黑白灰屏检测，采取了图像压缩的方法（原始图像像素量巨大），再遍历图像以检测大面积单一颜色的区域，采取了一定的步长的滑动窗口，大大减少了复杂度。
4、结构相似，通过检测sift特征，并使用flann匹配器匹配，筛选好的匹配点后，再通过匹配数量来判断布局是否一致
5、结构相似度对比了ssim、mse、phash和直方图的相似度，其中ssim：亮度、对比度和结构三个方面的信息。Mse：对亮度和对比度变化非常敏感,计算速度快。Phash：能够捕捉图像的结构信息，对旋转、缩放等变换有较好的鲁棒性。直方图：能够考虑颜色分布信息，对于彩色图像比较有用，不考虑亮度、对比度和结构信息。最终采用了直方图的相似度。
6、sift只能用来检测图像中唯一的子图，可以适用于不同像素的子图，但是存在多张子图会失效！采用元素分割后筛选特地大小的子图来匹配，再返回坐标映射原图
7、元素分割：灰度化后提取边缘，再进行膨胀连接相邻的边缘，找到轮廓后遍历轮廓筛选出大于特定阈值的区域，并使用矩形去逼近，从而对于不同元素实现分割。
