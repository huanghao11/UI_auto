import cv2
import numpy as np

# 设定一个最大的窗口大小，例如屏幕分辨率
max_window_height = 800
max_window_width = 1200


def resize_image(image, max_width, max_height):
    height, width = image.shape[:2]
    if width > max_width or height > max_height:
        # 计算纵横比
        ratio = min(max_width / width, max_height / height)
        image = cv2.resize(image, (int(width * ratio), int(height * ratio)), interpolation=cv2.INTER_AREA)
    return image


def is_rectangle(corners):
    # 计算四边形的两个对角线
    diag1 = np.linalg.norm(corners[0] - corners[2])
    diag2 = np.linalg.norm(corners[1] - corners[3])
    # 如果两个对角线长度相近，我们可以认为它是矩形
    return abs(diag1 - diag2) < 0.1 * max(diag1, diag2)


def match_subimage(image, subimages, visualize=True):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()
    kp_img, des_img = sift.detectAndCompute(img_gray, None)

    flann_index_kdtree = 0
    index_params = dict(algorithm=flann_index_kdtree, trees=5)
    search_params = dict(checks=100)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matched_regions = []

    for subimage in subimages:
        subimg_gray = cv2.cvtColor(subimage, cv2.COLOR_BGR2GRAY)
        kp_subimg, des_subimg = sift.detectAndCompute(subimg_gray, None)

        matches = flann.knnMatch(des_img, des_subimg, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.65 * n.distance:
                good_matches.append(m)

        if len(good_matches) >= 4:
            points_img = np.float32([kp_img[m.queryIdx].pt for m in good_matches])
            points_subimg = np.float32([kp_subimg[m.trainIdx].pt for m in good_matches])

            M, mask = cv2.findHomography(points_subimg, points_img, cv2.RANSAC, 5.0)
            if M is not None:
                h, w = subimage.shape[:2]
                corners_subimg = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                corners_img = cv2.perspectiveTransform(corners_subimg, M).reshape(-1, 2)

                if is_rectangle(corners_img):
                    x_min, y_min = corners_img.min(axis=0).astype(int)
                    x_max, y_max = corners_img.max(axis=0).astype(int)
                    center_coord = ((x_min + x_max) // 2, (y_min + y_max) // 2)
                    width_height = (x_max - x_min, y_max - y_min)

                    matched_regions.append((center_coord, width_height))

                    if visualize:
                        cv2.polylines(image, [np.int32(corners_img)], True, (0, 255, 0), thickness=2,
                                      lineType=cv2.LINE_AA)
        else:
            print("Not enough matches found for one of the subimages.")

    return matched_regions

# 返回原图中能匹配到的多张子图的坐标列表，并可视化所有区域
def match_all_region(image, subimage_paths, visualize = True):
    # 读取图像
    image = cv2.imread(image)

    subimages = [cv2.imread(path) for path in subimage_paths]

    # 这次调用时设定visualize参数为True或False
    matched_regions = match_subimage(image, subimages, visualize=visualize)
    print(matched_regions)

    # 可视化处理
    if visualize:
        resized_image = resize_image(image, max_window_width, max_window_height)
        cv2.imshow('Result', resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# 传入多张子图，如果原图中存在其一，断言返回True，若均不存在，返回False
def subimage_exists(image, subimage_paths,visualize = False):
    # 读取图像
    image = cv2.imread(image)

    subimages = [cv2.imread(path) for path in subimage_paths]

    # 这次调用时设定visualize参数为True或False
    matched_regions = match_subimage(image, subimages, visualize=visualize)
    for match in matched_regions:
        if match is not None:
            # 可视化处理
            if visualize:
                resized_image = resize_image(image, max_window_width, max_window_height)
                # cv2.imshow('Result', resized_image)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                temp_filename = "pic\\processed_subImg1.jpg"
                cv2.imwrite(temp_filename, resized_image)
            return True
    return False



# 对于不确定的子图，前端传入多种场景子图，如果存在就返回第一个符合的子图区域坐标
def match_one_element(image, subimage_paths,visualize = False):
    # 读取图像
    image = cv2.imread(image)

    subimages = [cv2.imread(path) for path in subimage_paths]

    # 这次调用时设定visualize参数为True或False
    matched_regions = match_subimage(image, subimages, visualize=visualize)
    for match in matched_regions:
        if match is not None:
            if visualize:
                resized_image = resize_image(image, max_window_width, max_window_height)
                temp_filename = "pic\\processed_subImg2.jpg"
                cv2.imwrite(temp_filename, resized_image)
            return match
    return []

# a = match_one_element('D:\\Users\\meituan.jpg',[
#         'D:\\Users\\sub4.jpg',
#         'D:\\Users\\sub5.jpg',
#         'D:\\Users\\sub6.jpg',
#         'D:\\Users\\sub8.jpg',
#         'D:\\Users\\sub7.jpg'
#     ],True)
# print(a)