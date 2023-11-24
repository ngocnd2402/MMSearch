import numpy as np

# Đường dẫn đến tệp .npy
npy_file_path = 'Features/Bvecs/L01_V001.npy'

# Đọc dữ liệu từ tệp .npy
data = np.load(npy_file_path)

# Xem 5 dòng đầu tiên trong dữ liệu
print(data.shape)
