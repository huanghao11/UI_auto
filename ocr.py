import base64
import time

import requests
import json
import cv2
import paddlehub as hub

from config_tools import read_yaml
from picture_tools import edit_picture, get_picture_path, get_picture_name, black_out_rectangle
from file_tools import del_file

img_path = "D:\\Users\\demo222.jpg"


def get_ocr_state():
    ocr_state = read_yaml("ocr_state")
    return ocr_state


class OCRModel:
    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is None:
            self.model = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=True)

    def recognize_text(self, img_path):
        if self.model is None:
            self.load_model()
        result = self.model.recognize_text(images=[cv2.imread(img_path)])
        return result


# 服务端要求转换格式
def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tobytes()).decode('utf8')


def ocr_post(img_path):
    # 发送HTTP请求
    data = {'images': [cv2_to_base64(cv2.imread(img_path))]}
    headers = {"Content-type": "application/json"}
    url = "http://172.24.200.207:8866/predict/ch_pp-ocrv3"
    r = requests.post(url=url, headers=headers, data=json.dumps(data))
    return r


ocr_model = OCRModel()


# 本地ocr获取识别的text
def get_ocr_text_local(img_path):
    result = ocr_model.recognize_text(img_path)
    # ocr = hub.Module(name="ch_pp-ocrv3", enable_mkldnn=True)  # mkldnn加速仅在CPU下有效
    # result = ocr.recognize_text(images=[cv2.imread(img_path)])
    return result


# def get_ocr_response(access_token,img_path):
#
#     url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general?access_token="+access_token
#
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Accept": "application/json"
#     }
#
#     image = get_file_content_as_base64(img_path)
#     payload = "image="+image+"&detect_direction=false&detect_language=false&vertexes_location=false&paragraph=false&probability=false"

#     response_str = requests.request("POST",url,headers=headers,data=payload)
#
#     print(response_str.text)
#     return response_str

def str2json(str):
    try:
        data_json = json.loads(str)
        return data_json
    except:
        print("response的str不能转为json")


# def get_file_content_as_base64(path,urlencoded=True):
#     with open(path,"rb") as f:
#         content = base64.b64encode(f.read()).decode("utf-8")
#         if urlencoded:
#             content = urllib.parse.quote_plus(content)
#     return content
#
# def extract_token_text():
#     token_respnse = get_token()
#     if token_respnse.status_code == 200:
#         token_text = token_respnse.text
#         return token_text
#     else:
#         print("token返回失败")
#         return ""
#
# def extract_access_token(token_text):
#     token_json = str2json(token_text)
#     if token_json is not None:
#         access_token = token_json['access_token']
#         expires = token_json['expires_in']
#         if expires > 0:
#             return access_token
#         else:
#             refresh_token_response = extract_token_text()
#             refresh_access_token = extract_access_token(refresh_token_response)
#             return refresh_access_token

# 服务端发送请求获取ocr结果
def get_ocr_text_remote(img_path):
    res = ocr_post(img_path)
    if res is not None and res != "":
        if res.status_code == 200:
            ocr_result_text = res.text
            return ocr_result_text
        else:
            print("OCR识别失败")
    else:
        return ""


# 本地获取ocr_list
def get_ocr_list_local(ocr_result_text):
    if judge_null(ocr_result_text):
        text_list = ocr_result_text[0]['data']
        return text_list


# 服务端获取ocr_list
def get_ocr_list_remote(ocr_result_text):
    if judge_null(ocr_result_text):
        # ocr_result= ocr_result_text[0]
        ocr_result = str2json(ocr_result_text)
        # ocr_list_json = str2json(ocr_result_text)
        # words_result_num = ocr_list_json['words_result_num']
        words_result = ocr_result['msg'][0]['data']
        return words_result
    else:
        print("OCR获取文字list失败")
        return []


# 获取text第一个出现的位置坐标
def words_first_locations(text, ocr_list):
    if judge_null(ocr_list):
        for word_textAndLoc in ocr_list:
            if isinstance(word_textAndLoc, dict):
                if text in word_textAndLoc["text"]:
                    if judge_null(word_textAndLoc["text_box_position"]):
                        center = get_location_center(word_textAndLoc['text_box_position'])
                        return center
                    else:
                        print("location不能正确推理出坐标信息")
            else:
                print(word_textAndLoc + "不是dict")
        print(text + "在图片中无法被识别")
    else:
        print("ocr_list列表为空")


# 获取text出现的所有坐标列表
def words_all_locations(text, ocr_list):
    loc_list = []
    if judge_null(ocr_list):
        for word_textAndLoc in ocr_list:
            if isinstance(word_textAndLoc, dict):
                if text in word_textAndLoc["text"]:
                    if judge_null(word_textAndLoc["text_box_position"]):
                        center = get_location_center(word_textAndLoc['text_box_position'])
                        loc_list.append(center)
                    else:
                        print("location不能正确推理出坐标信息")
            else:
                print(word_textAndLoc + "不是dict")
        if ocr_list == []:
            print(text + "在图片中无法被识别")
    else:
        print("ocr_list列表为空")
    return loc_list


# 返回图片中第num个text的中心坐标，num起始为1
def words_ith_location(text, img_path, num, device=get_ocr_state()):
    if device == "remote":
        ocr_text = get_ocr_text_remote(img_path)
        ocr_list = get_ocr_list_remote(ocr_text)
    elif device == "local":
        ocr_text = get_ocr_text_local(img_path)
        ocr_list = get_ocr_list_local(ocr_text)
    loc_list = []
    if judge_null(ocr_list):
        for word_textAndLoc in ocr_list:
            if isinstance(word_textAndLoc, dict):
                if text in word_textAndLoc["text"]:
                    if judge_null(word_textAndLoc["text_box_position"]):
                        center = get_location_center(word_textAndLoc['text_box_position'])
                        loc_list.append(center)
                    else:
                        print("location不能正确推理出坐标信息")
            else:
                print(word_textAndLoc + "不是dict")
        if ocr_list == []:
            print(text + "在图片中无法被识别")
    else:
        print("ocr_list列表为空")
    loc_list.sort(key=lambda x: x[1])
    if num <= len(loc_list):
        selectd_text = loc_list[num - 1]
        return selectd_text
    return None


def judge_null(text):
    if text is not None and text != "":
        return True
    else:
        return False


# 获取第num个text出现的左上角坐标
def get_ith_leftTop(text, img_path, num, device=get_ocr_state()):
    if device == "remote":
        ocr_text = get_ocr_text_remote(img_path)
        ocr_list = get_ocr_list_remote(ocr_text)
    elif device == "local":
        ocr_text = get_ocr_text_local(img_path)
        ocr_list = get_ocr_list_local(ocr_text)
    loc_list = []
    if judge_null(ocr_list):
        for word_textAndLoc in ocr_list:
            if isinstance(word_textAndLoc, dict):
                if text in word_textAndLoc["text"]:
                    if judge_null(word_textAndLoc["text_box_position"]):
                        if isinstance(word_textAndLoc['text_box_position'], list):
                            left_top = word_textAndLoc['text_box_position'][0]
                            loc_list.append(left_top)
                    else:
                        print("location不能正确推理出坐标信息")
            else:
                print(word_textAndLoc + "不是dict")
    else:
        print("ocr_list列表为空")
    loc_list.sort(key=lambda x: x[1])
    if num <= len(loc_list):
        selectd_text = loc_list[num - 1]
        return selectd_text
    return None


def get_location_center(coords):
    # 计算矩形区域的左上角和右下角顶点坐标
    top_left = coords[0]
    bottom_right = coords[2]
    # 计算矩形区域的中心坐标
    center_x = (top_left[0] + bottom_right[0]) / 2
    center_y = (top_left[1] + bottom_right[1]) / 2
    return (center_x, center_y)


# 输出第一个匹配文本的中心坐标
def text_to_first_location(text, img_path, device=get_ocr_state()):
    if device == "remote":
        ocr_text = get_ocr_text_remote(img_path)
        ocr_list = get_ocr_list_remote(ocr_text)
    elif device == "local":
        ocr_text = get_ocr_text_local(img_path)
        ocr_list = get_ocr_list_local(ocr_text)
    all_text_loc = words_first_locations(text, ocr_list)
    return all_text_loc


# 输出所有匹配文本的中心坐标列表
def text_to_all_location(text, img_path, device=get_ocr_state()):
    if device == "remote":
        ocr_text = get_ocr_text_remote(img_path)
        ocr_list = get_ocr_list_remote(ocr_text)
    elif device == "local":
        ocr_text = get_ocr_text_local(img_path)
        ocr_list = get_ocr_list_local(ocr_text)
    all_text_loc = words_all_locations(text, ocr_list)
    return all_text_loc


# 输入需要裁剪图片的原路径，会在config对应的文件下生成一个路径为pic_new_path的裁剪后的图片，裁剪后的区域对应原图的left,upper,right,lower
# ocr识别算法可以对区域内的图像进行文字识别，减少其余区域文字的干扰
# 输出为原图上对应的文字中心坐标
def text_region_location(text, left, upper, right, lower, img_path):
    edit_picture(img_path, left, upper, right, lower)
    pic_new_path = get_picture_path(img_path)
    region_loc = text_to_first_location(text, pic_new_path)
    source_pic_x = left + region_loc[0]
    source_pic_y = upper + region_loc[1]
    del_file(pic_new_path)
    return [source_pic_x, source_pic_y]


def text_black_out_location(text, left, upper, right, lower, img_path):
    black_out_rectangle(img_path, left, upper, right, lower)
    pic_new_path = get_picture_path(img_path)
    region_loc = text_to_first_location(text, pic_new_path)
    source_pic_x = left + region_loc[0]
    source_pic_y = upper + region_loc[1]
    del_file(pic_new_path)
    return [source_pic_x, source_pic_y]


# 输入文本，判断在图片中是否存在
def has_text(text, img_path, device=get_ocr_state()):
    if device == "remote":
        ocr_text = get_ocr_text_remote(img_path)
        ocr_list = get_ocr_list_remote(ocr_text)
    elif device == "local":
        ocr_text = get_ocr_text_local(img_path)
        ocr_list = get_ocr_list_local(ocr_text)
    if judge_null(ocr_list):
        for word_textAndLoc in ocr_list:
            if isinstance(word_textAndLoc, dict):
                if text in word_textAndLoc['text']:
                    return True
    return False


# 输入文本，判断在选定区域中是否存在
def has_text_region(text, img_path, left, upper, right, lower, device=get_ocr_state()):
    edit_picture(img_path, left, upper, right, lower)
    pic_new_path = get_picture_path(img_path)
    if device == "remote":
        ocr_text = get_ocr_text_remote(pic_new_path)
        ocr_list = get_ocr_list_remote(ocr_text)
    elif device == "local":
        ocr_text = get_ocr_text_local(pic_new_path)
        ocr_list = get_ocr_list_local(ocr_text)
    if judge_null(ocr_list):
        for word_textAndLoc in ocr_list:
            if isinstance(word_textAndLoc, dict):
                if text in word_textAndLoc['text']:
                    del_file(pic_new_path)
                    return True
    del_file(pic_new_path)
    return False


# 输入文本，判断在选定区域之外是否存在
def has_text_outRegion(text, img_path, left, upper, right, lower, device=get_ocr_state()):
    black_out_rectangle(img_path, left, upper, right, lower)
    pic_new_path = get_picture_path(img_path)
    if device == "remote":
        ocr_text = get_ocr_text_remote(pic_new_path)
        ocr_list = get_ocr_list_remote(ocr_text)
    elif device == "local":
        ocr_text = get_ocr_text_local(pic_new_path)
        ocr_list = get_ocr_list_local(ocr_text)
    if judge_null(ocr_list):
        for word_textAndLoc in ocr_list:
            if isinstance(word_textAndLoc, dict):
                if text in word_textAndLoc['text']:
                    del_file(pic_new_path)
                    return True
    del_file(pic_new_path)
    return False


# 校验文字列表tab是否锚定
def check_focus(text, img_path, num, device=get_ocr_state()):
    left = 0
    top = 0
    if device == "local":
        left_tmp, top_tmp = get_ith_leftTop(text, img_path, num, "local")
        left = left_tmp
        top = top_tmp
    elif device == "remote":
        left_tmp, top_tmp = get_ith_leftTop(text, img_path, num, "remote")
        left = left_tmp
        top = top_tmp
    image = cv2.imread(img_path)

    pixel = image[top, left]

    if all(pixel == [255, 255, 255]):
        return True
    else:
        return False

# start = time.time()
# print("=====")
# x = check_focus("推荐",img_path,2)
# print(x)
# end = time.time()
# print(end-start)
# y = check_focus("规格",img_path,1)
# hh = time.time()
# print(y)
# print(hh-end)
# z= check_focus("规格",img_path,1,"local")
# zz = time.time()
# print(zz-hh)
# z= check_focus("规格",img_path,1,"local")
# zz = time.time()
# print(zz-hh)
# z= check_focus("规格",img_path,1,"local")
# zz = time.time()
# print(zz-hh)
# z= check_focus("规格",img_path,1,"local")
# zz = time.time()
# print(zz-hh)
