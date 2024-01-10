import os
from natsort import natsorted
import csv
from tqdm import tqdm

image_folder = "KEYFRAME_PATH"
output_folder = "Data/Mapframe"
os.makedirs(output_folder, exist_ok=True)

total_folders = sum(1 for root, dirs, files in os.walk(image_folder) if not dirs)
with tqdm(total=total_folders, desc="Processing folders") as pbar:
    for root, dirs, files in os.walk(image_folder):
        if not dirs:
            folder_name = os.path.basename(root)
            csv_file_name = os.path.join(output_folder, f"{folder_name}.csv")
            image_files = natsorted([f for f in files if f.endswith(".jpg")])

            with open(csv_file_name, "w", newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["n", "pts_time", "fps", "frame_idx"])
                total_images = len(image_files)

                with tqdm(total=total_images, desc=f"Processing {folder_name}") as pbar2:
                    for idx, image_file in enumerate(image_files):
                        frame_idx = int(image_file.split(".jpg")[0])
                        pts_time = frame_idx / 25.0
                        csv_writer.writerow([idx + 1, pts_time, 25.0, frame_idx])
                        pbar2.update(1)
                pbar2.close()
            pbar.update(1)

print("Successfully created CSV files and saved them in the 'map_keyframe' folder!")
