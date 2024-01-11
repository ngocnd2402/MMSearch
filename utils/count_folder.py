import os

folder_path = "/mmlabworkspace/Datasets/AIC2023/Batch2/Audio"

if os.path.exists(folder_path):
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    num_subfolders = len(subfolders)
    
    print(f"Số lượng subfolder trong '{folder_path}': {num_subfolders}")
else:
    print(f"Đường dẫn '{folder_path}' không tồn tại.")
