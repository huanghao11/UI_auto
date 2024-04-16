import cv2
import numpy as np
import os
from config_tools import read_yaml
from file_tools import clear_folder

MUTLI_DISTANCE = read_yaml("mutli_distance") or 0.7

def save_rectangles(image, width_range, height_range, output_folder):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 20, 50)
    dilated = cv2.dilate(edges, None, iterations=4)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rectangles = []
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        if width_range[0] <= w <= width_range[1] and height_range[0] <= h <= height_range[1]:
            cropped_image = image[y:y+h, x:x+w]
            file_name = os.path.join(output_folder, f"cropped_{i}.jpg")
            cv2.imwrite(file_name, cropped_image)
            rectangles.append((x, y, w, h, file_name))

    return rectangles

def is_rectangle(corners):
    return len(corners) == 4

def match_subimage(image, subimage_path, rectangles, visualize=True):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_height, image_width = image.shape[:2]

    # 初始化SIFT检测器
    sift = cv2.SIFT_create()
    # 设置FLANN匹配器参数
    flann_index_kdtree = 0
    index_params = dict(algorithm=flann_index_kdtree, trees=5)
    search_params = dict(checks=100)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # 读取子图像并转换为灰度图
    subimage = cv2.imread(subimage_path)
    subimg_gray = cv2.cvtColor(subimage, cv2.COLOR_BGR2GRAY)
    # 检测子图像中的关键点和描述子
    kp_subimg, des_subimg = sift.detectAndCompute(subimg_gray, None)

    # 存储匹配到的区域
    matched_regions = []

    # 遍历给定的矩形区域
    for (x, y, w, h, _) in rectangles:
        # 裁剪图像并转换为灰度图
        cropped_img = image[y:y + h, x:x + w]
        cropped_gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        # 检测裁剪图像中的关键点和描述子
        kp_cropped, des_cropped = sift.detectAndCompute(cropped_gray, None)

        # 使用FLANN进行匹配
        matches = flann.knnMatch(des_cropped, des_subimg, k=2)
        # 筛选出好的匹配点
        good_matches = [m for m, n in matches if m.distance < MUTLI_DISTANCE * n.distance]

        # 如果找到足够的匹配点，则找到单应性
        if len(good_matches) >= 4:
            points_cropped = np.float32([kp_cropped[m.queryIdx].pt for m in good_matches])
            points_subimg = np.float32([kp_subimg[m.trainIdx].pt for m in good_matches])

            # 使用RANSAC算法计算单应性矩阵
            M, mask = cv2.findHomography(points_subimg, points_cropped, cv2.RANSAC, 5.0)
            # 如果单应性矩阵存在，则计算子图像的角点在裁剪图像中的位置
            if M is not None:
                h_sub, w_sub = subimage.shape[:2]
                corners_subimg = np.float32([[0, 0], [0, h_sub - 1], [w_sub - 1, h_sub - 1], [w_sub - 1, 0]]).reshape(-1, 1, 2)
                corners_cropped = cv2.perspectiveTransform(corners_subimg, M).reshape(-1, 2) + np.array([x, y])

                # 计算匹配区域的坐标
                x_min, y_min = np.min(corners_cropped, axis=0).astype(int)
                x_max, y_max = np.max(corners_cropped, axis=0).astype(int)

                # 确保坐标在原图尺寸范围内
                if 0 <= x_min < image_width and 0 <= y_min < image_height and 0 <= x_max <= image_width and 0 <= y_max <= image_height:
                    matched_regions.append(((x_min, y_min), (x_max, y_max)))

                    if visualize:
                        cv2.polylines(image, [np.int32(corners_cropped)], True, (0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    return matched_regions


def mutli_match(image_path, subimage_path, width_range, height_range,num,output_folder='tmp'):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 删除目录下已经有的图片
    clear_folder(output_folder)

    image = cv2.imread(image_path)
    rectangles = save_rectangles(image, width_range, height_range, output_folder)
    matched_regions = match_subimage(image, subimage_path, rectangles)

    # 清除临时文件
    # clear_folder(output_folder)

    matched_regions.sort(key=lambda x: x[0][1])

    return matched_regions

# # 调用主函数
# main_image_path = 'D:\\Users\\demo1.jpg'
# subimage_path = 'D:\\Users\\sub2.jpg'
# width_range = (50, 200)  # 例如，宽度在50到200像素之间
# height_range = (50, 200) # 例如，高度在50到200像素之间
# tmp_folder = 'D:\\UI_auto\\tmp'
#
# matched_regions = mutli_match(main_image_path, subimage_path, width_range, height_range,tmp_folder)
# for region in matched_regions:
#     print("Matched region:", region)

