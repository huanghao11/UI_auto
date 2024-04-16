from ocr import words_ith_location, get_ocr_state
from utils import ith_subpic


def isPic(image_path):
    if "jpg" in image_path or "png" in image_path:
        return True
    else:
        return False


# 这里拿文本和文本进行比较
def compare_text2text(image_path, obj1, obj2, direction, diff, num1, num2, device=get_ocr_state()):
    if not isPic(obj1) and not isPic(obj2):
        x1, y1 = words_ith_location(obj1, image_path, num1, device)
        x2, y2 = words_ith_location(obj2, image_path, num2, device)
    else:
        raise ValueError("只能输入文本与文本比较")

    if direction == 'down':
        return (y1 > y2) and (abs(y1 - y2) < diff)
    elif direction == 'up':
        return (y1 < y2) and (abs(y2 - y1) < diff)
    elif direction == 'left':
        return (x1 < x2) and (abs(x2 - x1) < diff)
    elif direction == 'right':
        return (x2 < x1) and (abs(x1 - x2) < diff)
    else:
        raise ValueError("方向只能选up，down，left.right")


# 这里拿图片和图片进行位置比较
def compare_pic2pic(image_path, obj1, obj2, width_range1, height_range1, width_range2, height_range2, direction, diff,
                    num1, num2):
    if isPic(obj1) and isPic(obj2):
        x1, y1 = ith_subpic(image_path, obj1, width_range1, height_range1, num1)
        x2, y2 = ith_subpic(image_path, obj2, width_range2, height_range2, num2)
    else:
        raise ValueError("只能输入图像与图像比较")

    if direction == 'down':
        return (y1 > y2) and (abs(y1 - y2) < diff)
    elif direction == 'up':
        return (y1 < y2) and (abs(y2 - y1) < diff)
    elif direction == 'left':
        return (x1 < x2) and (abs(x2 - x1) < diff)
    elif direction == 'right':
        return (x2 < x1) and (abs(x1 - x2) < diff)
    else:
        raise ValueError("方向只能选up，down，left.right")


# 这里只能拿文本和图片比较！文字在前图像在后
def compare_text2pic(image_path, obj1, obj2, width_range, height_range, direction, diff, num1, num2,device="local"):
    if not isPic(obj1) and isPic(obj2):
        x1, y1 = words_ith_location(obj1, image_path, num1,device)
        x2, y2 = ith_subpic(image_path, obj2, width_range, height_range, num2)
    else:
        raise ValueError("只能输入文本与图像比较")

    if direction == 'down':
        return (y1 > y2) and (abs(y1 - y2) < diff)
    elif direction == 'up':
        return (y1 < y2) and (abs(y2 - y1) < diff)
    elif direction == 'left':
        return (x1 < x2) and (abs(x2 - x1) < diff)
    elif direction == 'right':
        return (x2 < x1) and (abs(x1 - x2) < diff)
    else:
        raise ValueError("方向只能选up，down，left.right")


# a = compare_text2text('D:\\Users\\demo1.jpg', "夏雪儿", "商家自配", "up", 1500, 1, 2, "local")
# print(a)
# b = compare_text2pic('D:\\Users\\demo1.jpg', "夏雪", 'D:\\Users\\sub2.jpg', (0, 100), (0, 100), "left", 500, 1, 1,"local")
# print(b)
