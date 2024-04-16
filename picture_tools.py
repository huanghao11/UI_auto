from PIL import Image,ImageDraw
import os

from config_tools import read_yaml

def get_center(picture):
    image = Image.open(picture)
    width, height = image.size
    center_x, center_y = width//2 ,height//2
    return center_x, center_y

def get_width(picture):
    return get_center(picture)[0]*2

def get_height(picture):
    return get_center(picture)[1]*2

def get_picture_name(picture):
    image_name = os.path.basename(picture)
    # print(f"图片名称为：{image_name}")
    return image_name

def get_picture_path(picture):
    pic_dirname = read_yaml("picture_path")
    pic_name = get_picture_name(picture)
    pic_new_path = pic_dirname + "\\" + pic_name
    return pic_new_path

#根据区域对图片进行裁剪
def edit_picture(source_pic_path,left,upper,right,lower):
    source_image = Image.open(source_pic_path)
    crop_coordinates = (left, upper, right, lower)
    cropped_image = source_image.crop(crop_coordinates)

    des_pic_path = get_picture_path(source_pic_path)

    cropped_image.save(des_pic_path)

    source_image.close()

def black_out_rectangle(image_path,left,uppper,right,lower):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    rectangle_coordinates = [(left,uppper),(right,lower)]
    draw.rectangle(rectangle_coordinates,fill="black")
    des_pic_path = get_picture_path(image_path)

    image.save(des_pic_path)
    image.close()