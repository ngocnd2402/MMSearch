import os
from natsort import natsorted
import csv
from tqdm import tqdm

# Đường dẫn đến thư mục chứa hình ảnh
image_folder = "Data/Reframe"

# Đường dẫn đến thư mục chứa các tệp CSV
output_folder = "Data/Mapframe"  # Đổi đường dẫn này thành "map_keyframe"

# Tổng số thư mục cấp 3
total_folders = sum(1 for root, dirs, files in os.walk(image_folder) if not dirs)

# Tiến trình tqdm
with tqdm(total=total_folders, desc="Processing folders") as pbar:
    # Lặp qua tất cả các thư mục cấp 3
    for root, dirs, files in os.walk(image_folder):
        if not dirs:  # Đảm bảo chúng ta đang ở thư mục cuối cùng
            folder_name = os.path.basename(root)
            csv_file_name = os.path.join(output_folder, f"{folder_name}.csv")
            image_files = natsorted([f for f in files if f.endswith(".jpg")])

            # Mở tệp CSV để ghi
            with open(csv_file_name, "w", newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["n", "pts_time", "fps", "frame_idx"])

                # Tổng số hình ảnh
                total_images = len(image_files)

                # Tiến trình tqdm cho từng folder
                with tqdm(total=total_images, desc=f"Processing {folder_name}") as pbar2:
                    # Lặp qua các tệp hình ảnh và ghi thông tin vào tệp CSV
                    for idx, image_file in enumerate(image_files):
                        frame_idx = int(image_file.split(".jpg")[0])
                        pts_time = frame_idx / 25.0
                        csv_writer.writerow([idx + 1, pts_time, 25.0, frame_idx])
                        pbar2.update(1)
                pbar2.close()
            pbar.update(1)

print("Đã tạo các tệp CSV thành công và lưu vào thư mục 'map_keyframe'!")
