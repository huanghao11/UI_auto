import os
import shutil

def del_file(path):
    try:
        os.remove(path)
        # print(f"文件{path}删除成功")
    except OSError as e:
        print(f"删除文件{path}失败：{e}")

def copy_pircture(source,dest,new_name):
    destination_path = os.path.join(dest,new_name)
    try:
        shutil.copy2(source,destination_path)
        # print(f"图片复制成功,新文件位于：{destination_path}")
    except Exception as e:
        print(f"图片复制失败:{e}")

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)