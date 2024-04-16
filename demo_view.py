# import cv2
# import numpy as np
#
# # 读取图像
# image = cv2.imread('D:\\Users\\demo1.jpg')
#
# # 显示原始图像
# # cv2.imshow('Original', image)
# # cv2.waitKey(0)
#
# # 将图像转换为灰度图像
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
# # 显示灰度图像
# # cv2.imshow('Gray', gray)
# # cv2.waitKey(0)
#
# # 提取边缘
# edges = cv2.Canny(gray, 10, 30)
#
# # 显示边缘图像
# cv2.imshow('Edges', edges)
# cv2.waitKey(0)
#
# # 进行膨胀操作，以连接相邻的边缘
# dilated = cv2.dilate(edges, None, iterations=4)
#
# # 显示膨胀后的图像
# cv2.imshow('Dilated', dilated)
# cv2.waitKey(0)
#
# # 找到轮廓
# contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
# # 绘制轮廓
# contour_img = np.zeros_like(image)
# cv2.drawContours(contour_img, contours, -1, (0, 0, 255), 2)
#
# # 显示轮廓图像
# cv2.imshow('Contours', contour_img)
# cv2.waitKey(0)
#
# # 遍历轮廓，筛选出白色卡片的位置
# white_cards = []
# for contour in contours:
#     # 计算轮廓的面积
#     area = cv2.contourArea(contour)
#     # 设置面积的阈值，根据实际情况调整
#     if area > 1000:
#         # 计算轮廓的外接矩形
#         x, y, w, h = cv2.boundingRect(contour)
#         # 绘制外接矩形
#         cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
#         # 添加白色卡片的位置到列表中
#         white_cards.append((x, y, w, h))
#
# # 显示结果图像
# cv2.imshow('Result', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#
# # 输出白色卡片的位置
# print("White cards positions:")
# for card in white_cards:
#     print(card)
# #
import cv2

def process_image(image_path, area_threshold=2, width_threshold=150,height_threshold=10):
    # 读取图像
    image = cv2.imread(image_path)

    # 将图像转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 提取边缘
    edges = cv2.Canny(gray, 20, 30)

    # 进行膨胀操作，以连接相邻的边缘
    dilated = cv2.dilate(edges, None, iterations=4)

    # 找到轮廓
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 遍历轮廓，筛选出大的资源位的位置
    large_areas = []
    for contour in contours:
        # 计算轮廓的面积
        area = cv2.contourArea(contour)
        # 计算轮廓的外接矩形
        x, y, w, h = cv2.boundingRect(contour)
        # 筛选出大面积且宽度超过阈值的轮廓
        if area > area_threshold and h>height_threshold:
            large_areas.append((x, y, w, h))
            # 绘制外接矩形
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # 显示结果图像
    # cv2.imshow('Result', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    temp_filename = "pic\\processed_image.jpg"
    cv2.imwrite(temp_filename, image)

    # 返回大的资源位的位置
    return large_areas

# image_path = 'D:\\Users\\demo1.jpg'
# large_areas = process_image(image_path)
# print("Large resource areas positions:")
# for area in large_areas:
#     print(area)
