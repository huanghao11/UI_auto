from compare_location import compare_text2text, compare_text2pic, compare_pic2pic
from demo_view import process_image
from match_subpic import subimage_exists, match_one_element
from mutli_match import mutli_match
from ocr import has_text, has_text_region, has_text_outRegion, check_focus, words_ith_location
from ssim import detect_ui_issues, calculate_histogram_similarity, compare_layout

# 原图
img_origin1 = "D:\\UI_auto\\demo1.jpg"
img_origin2 = "D:\\UI_auto\\demo2.jpg"
# 待匹配子图
img_sub1 = "D:\\UI_auto\\sub1.jpg"
img_sub2 = "D:\\UI_auto\\sub2.jpg"
# 黑白屏图片
error1 = "D:\\UI_auto\\error1.jpg"
error2 = "D:\\UI_auto\\error2.jpg"
# 图片色调
compare = "D:\\UI_auto\\compare.jpg"
# 图片结构对比
structure1 = "D:\\UI_auto\\structure1.jpg"
structure2 = "D:\\UI_auto\\structure2.jpg"

print("===================文字功能：=======================")

# 文字在图片中是否存在
exist_text = has_text("超市", img_origin1)
print("文字在图片中是否存在：", exist_text)

# 文字在选定区域中是否存在
exist_region_text = has_text_region("超市", img_origin1, 0, 0, 1000, 1000)
print("文字在图片选定区域中是否存在：", exist_region_text)

# 文字在选定区域之外是否存在
exist_outRegion_text = has_text_outRegion("超市", img_origin1, 0, 0, 100, 100)
print("文字在图片选定区域之外是否存在：", exist_outRegion_text)

# 校验文字列表tab是否锚定
focus = check_focus("推荐", img_origin2, 1)
print("推荐是否锚定:", focus)

# 返回图片中第num个text的中心坐标，num起始为1
ith_center_location = words_ith_location("商家", img_origin1, 2)
print("第2个商家的坐标是：", ith_center_location)

print("===================图片功能：=======================")

# 传入多张子图，如果原图中存在其一，断言返回True，若均不存在，返回False
subImg_exist = subimage_exists(img_origin1, [img_sub1], True)
print("传入的多个子图断言均在其一：", subImg_exist)

# 这里的坐标会输出第一个匹配的子图中心坐标以及宽度高度
subImg_first_location = match_one_element(img_origin1, [img_sub2], True)
print("传入的多个子图断言匹配的第一个坐标是：", subImg_first_location)

# 演示一下元素分割
print("========演示一下元素分割=======")
process_image(img_origin1)

width_range = (50, 200)
height_range = (50, 200)
tmp_folder = 'D:\\UI_auto\\tmp'

# 图片中存在多个一样的子图，返回所有子图的坐标
matched_regions = mutli_match(img_origin1, img_sub2, width_range, height_range, 0,tmp_folder)
for region in matched_regions:
    print("图片中存在的所有子图坐标为:", region)
print("==============综合图片和文字的位置比较==========")
  # 比较任意的文字与文字的位置
compare1 = compare_text2text(img_origin1, "夏雪儿", "商家自配", "up", 1500, 1, 2, "local")
print("文字与文字的位置比较为：", compare1)

# 比较任意的文字与图片的位置
compare2 = compare_text2pic(img_origin1, "夏雪", img_sub2, (0, 100), (0, 100), "left", 500, 1, 1, "local")
print("文字与图片的位置比较为：", compare2)

# 比较任意的图片与图片的位置
compare3 = compare_pic2pic(img_origin1, img_sub1, img_sub2, (0, 100), (0, 100), (0, 100), (0, 100), "up", 2000, 1, 2)
print("图片与图片的位置比较为：", compare3)

print("==============异常检测===============")
# 识别图片中的黑屏，白屏，灰屏等矩形区域并返回区域坐标，矩形区域阈值可以传参设置
ui_normal1 = detect_ui_issues(img_origin1)
print("这张图片存在黑白灰屏幕：",ui_normal1)

ui_normal2 = detect_ui_issues(error1)
print("这张图片存在黑白灰屏幕：",ui_normal2)

ui_normal3 = detect_ui_issues(error2)
print("这张图片存在黑白灰屏幕：",ui_normal3)

# 两张图片结构相似度，与颜色无关
histogram_result = calculate_histogram_similarity(compare,img_origin1)
print("两张图片结构相似度为：",histogram_result)

# 判断两张图片的结构是否一样
layout = compare_layout(structure1,structure2)
print("两张图片的结构是否一样：",layout)