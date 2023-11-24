import os
from PIL import Image

# Đường dẫn đến thư mục gốc (root folder)
root_folder = 'Frontend/Reframe'

# Hàm kiểm tra xem một tệp có định dạng JPG hay không
def is_jpg(filename):
    return filename.lower().endswith(".jpg")

# Sử dụng biến này để đếm số lượng hình ảnh JPG
jpg_count = 0

# Duyệt qua tất cả các tệp trong thư mục gốc và các thư mục con
for root, dirs, files in os.walk(root_folder):
    for file in files:
        file_path = os.path.join(root, file)
        if is_jpg(file_path):
            jpg_count += 1

print(f"Số lượng hình ảnh JPG trong thư mục gốc: {jpg_count}")


# import numpy as np
# file_path = "Features/Svecs/L01_V001.npy"  # Thay đổi đường dẫn tới tệp .npy của bạn
# data = np.load(file_path)
# # In hình dạng của toàn bộ mảng
# print("Shape of the entire array:", data.shape)

# # Duyệt qua từng vector và in hình dạng của nó
# for vector in data:
#     print("Shape of a vector:", vector.shape)
