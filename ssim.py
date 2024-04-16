import cv2
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np
import imagehash

# 亮度、对比度和结构三个方面的信息
def calculate_ssim(image1_path, image2_path):
    # 读取图片
    img1 = cv2.imread(image1_path)
    img2 = cv2.imread(image2_path)

    # 确保图片大小相同
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # 转换成灰度图
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 计算SSIM指数
    score, _ = ssim(img1_gray, img2_gray, full=True)
    return score

# 对亮度和对比度变化非常敏感,计算速度快
def calculate_mse(image1_path, image2_path):
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    image1_gray = image1.convert('L')
    image2_gray = image2.convert('L')

    image1_array = np.array(image1_gray)
    image2_array = np.array(image2_gray)

    mse = np.mean((image1_array - image2_array) ** 2)

    image1.close()
    image2.close()

    return mse

# 能够捕捉图像的结构信息，对旋转、缩放等变换有较好的鲁棒性。
def calculate_phash_similarity(image1_path, image2_path):
    # 读取图片文件
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    # 调整图片大小（为了保证图片大小相同）
    image1 = cv2.resize(image1, (100, 100))
    image2 = cv2.resize(image2, (100, 100))

    # 将图片转换成灰度图
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 计算图片的phash值
    phash1 = imagehash.phash(Image.fromarray(image1_gray))
    phash2 = imagehash.phash(Image.fromarray(image2_gray))

    # 计算汉明距离（Hamming Distance）
    hamming_distance = phash1 - phash2

    # 计算相似度
    similarity = 1.0 - (hamming_distance / (len(phash1.hash) ** 2))

    return similarity

# 能够考虑颜色分布信息，对于彩色图像比较有用，不考虑亮度、对比度和结构信息
def calculate_histogram_similarity(image1_path, image2_path):
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    hsv_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
    hsv_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)

    hist1 = cv2.calcHist([hsv_image1], [0, 1], None, [180, 256], [0, 180, 0, 256])
    hist1 = cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)

    hist2 = cv2.calcHist([hsv_image2], [0, 1], None, [180, 256], [0, 180, 0, 256])
    hist2 = cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)

    similar = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return similar


def calculate_fill_ratio(image_path):
    # 读取图片并转换成灰度图
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("图片不存在")

    # 获取图像尺寸
    height, width = image.shape

    # 初始化差分图像
    diff_image = np.zeros_like(image, dtype=np.int32)

    # 计算每个像素与其左边和上面像素的差值
    for y in range(height):
        for x in range(width):
            # 对于第一个像素，没有上面和左边的像素，值直接取像素值
            top_pixel = image[y - 1, x] if y > 0 else 0
            left_pixel = image[y, x - 1] if x > 0 else 0
            current_pixel = image[y, x]

            # 计算与上面和左边像素的差值
            diff_image[y, x] = abs(int(current_pixel) - int(top_pixel)) + abs(int(current_pixel) - int(left_pixel))

    # 如果与左边和上面的像素计算后的值大于0，则记为1
    diff_image = (diff_image > 0).astype(np.uint8)

    # 计算填充度
    fill_ratio = np.sum(diff_image) / (height * width)

    return fill_ratio


# 识别图片中的黑屏，白屏，灰屏等矩形区域并返回区域坐标，矩形区域阈值可以传参设置
def detect_ui_issues(image_path, width_ratio_threshold=0.6, height_ratio_threshold=0.2, scale_factor=0.05,
                     skip_steps=5):
    # 读取图片并转换成灰度图
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("图片不存在")

    # 缩放图像
    scaled_width = int(image.shape[1] * scale_factor)
    scaled_height = int(image.shape[0] * scale_factor)
    scaled_image = cv2.resize(image, (scaled_width, scaled_height), interpolation=cv2.INTER_AREA)

    # 定义起始的窗口大小
    min_width = int(scaled_width * width_ratio_threshold)
    min_height = int(scaled_height * height_ratio_threshold)

    # 遍历图像以检测大面积单一颜色的区域
    for y in range(0, scaled_height - min_height, skip_steps):
        for x in range(0, scaled_width - min_width, skip_steps):
            # 检查当前窗口
            window = scaled_image[y:y + min_height, x:x + min_width]
            if np.all(window == window[0, 0]):
                # 检查这个区域的实际大小
                actual_w, actual_h = min_width, min_height
                # 向右扩展
                while x + actual_w < scaled_width and np.all(
                        scaled_image[y:y + min_height, x:x + actual_w + 1] == window[0, 0]):
                    actual_w += 1
                # 向下扩展
                while y + actual_h < scaled_height and np.all(
                        scaled_image[y:y + actual_h + 1, x:x + actual_w] == window[0, 0]):
                    actual_h += 1

                # 检查区域是否满足阈值要求
                if actual_w >= min_width and actual_h >= min_height:
                    top_left = (int(x / scale_factor), int(y / scale_factor))
                    bottom_right = (int((x + actual_w) / scale_factor), int((y + actual_h) / scale_factor))
                    return True, (top_left, bottom_right)

    return False, None


# 用来判断两张分辨率相同的图像布局是否相似
def compare_layout(image_path1, image_path2, MIN_MATCH_COUNT=3500):
    # 读取图片
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    # 初始化SIFT检测器
    sift = cv2.SIFT_create()

    # 检测SIFT特征
    keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(img2, None)

    # 使用FLANN匹配器进行匹配
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)

    # 筛选好的匹配点
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    # 根据匹配数量判断布局结构是否一致
    if len(good_matches) > MIN_MATCH_COUNT:
        return True
    else:
        return False

#
# image1 = "D:\\Users\\demo21.jpg"
# image2 = "D:\\Users\\demo3.jpg"
# a = compare_layout(image1, image2, 3000)
# print(a)
