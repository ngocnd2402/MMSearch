# import numpy as np

# # Đường dẫn đến tệp .npy
# npy_file_path = 'Features/Bvecs/L01_V001.npy'

# # Đọc dữ liệu từ tệp .npy
# data = np.load(npy_file_path)[2]

# # Xem 5 dòng đầu tiên trong dữ liệu
# print(data.shape)

import os
from natsort import natsorted

def find_image_position(folder_name, image_name):
    files = natsorted(os.listdir(folder_name))
    try:
        position = files.index(image_name)
        return position
    except ValueError:
        return -1
    
def get_video_name(image_path):
    parts = image_path.split('/')
    video_name = parts[-2]
    return video_name

def split_path(input_path):
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    return directory, filename


img_path = '/mmlabworkspace/Students/visedit/AIC2023/Data/Reframe/L07/L07_V001/000364.jpg'
vid = get_video_name(img_path)
print(vid)

position = find_image_position(split_path(img_path)[0], split_path(img_path)[1])
print(f"Position of {split_path(img_path)[1]}: {position}")
