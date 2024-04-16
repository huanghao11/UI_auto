from mutli_match import mutli_match

# 可返回在图片中第num个子图的中心坐标（纵坐标从上到下）
def ith_subpic(image_path, subimage_path, width_range, height_range,num):
    matched_regions = mutli_match(image_path, subimage_path, width_range,height_range,num)

    # 返回第num个区域的中心坐标
    if num <= len(matched_regions):
        selected_region = matched_regions[num - 1]
        x_min, y_min = selected_region[0]
        x_max, y_max = selected_region[1]
        center_coord = ((x_min + x_max) // 2, (y_min + y_max) // 2)
        return center_coord
    else:
        return None


# a = ith_subpic('D:\\Users\\demo2.jpg','D:\\Users\\sub.jpg',
#                (0, 100),(0, 100),1)
# print(a)