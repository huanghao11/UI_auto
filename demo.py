import time

import uiautomator2 as u2

from compare_location import compare_text2pic, compare_text2text
from match_subpic import subimage_exists, match_one_element
from ocr import has_text, words_ith_location
from utils import ith_subpic

d = u2.connect() # connect to device
print(d.info)
d.app_start("com.sankuai.meituan")
time.sleep(2)
d.screenshot('test1.png')
if has_text("外卖","test1.png"):
   x,y = words_ith_location("外卖","test1.png",2)
   d.click(x,y)
time.sleep(3)
d.screenshot('test2.png')
time.sleep(2)
if subimage_exists("test2.png",["D:\\Users\\chaoshi.jpg"]):
    x,y = ith_subpic("test2.png","D:\\Users\\chaoshi.jpg",(100, 500),(100, 500),1)
    d.click(int(x),int(y))
    time.sleep(3)
    d.screenshot('test3.png')
    time.sleep(2)
    a = compare_text2text('test3.png',"全部","饺子","left",1000,1,1)
    print(a)

d.app_clear("com.sankuai.meituan")
d.app_stop("com.sankuai.meituan") 

