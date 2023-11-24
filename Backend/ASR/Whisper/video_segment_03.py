import os
import pandas as pd
from moviepy.editor import *
from natsort import natsorted
from tqdm import tqdm

def process_video(video_path, mapframe_path, output_root):
    df = pd.read_csv(mapframe_path)
    video = VideoFileClip(video_path)
    audio = video.audio

    video_duration = video.duration
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(output_root, video_name)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    i = 0
    while i < (len(df) - 1):
        start = i
        end = i + 1
        start_frame = df.iloc[start]['frame_idx']
        end_frame = df.iloc[end]['frame_idx']
        start_time = df.iloc[start]['pts_time']
        end_time = df.iloc[end]['pts_time']

        while end_time - start_time < 5 and end < (len(df) - 1):
            end += 1
            end_frame = df.iloc[end]['frame_idx']
            end_time = df.iloc[end]['pts_time']

        if start_time < video_duration and end_time <= video_duration:
            try:
                audio_clip = audio.subclip(start_time, end_time)
                output_filename = f"{output_folder}/{start_frame}-{end_frame}.mp3"
                audio_clip.write_audiofile(output_filename, codec='mp3')
            except Exception as e:
                print(f"Không thể xử lý đoạn từ {start_time} đến {end_time} trong video {video_path}: {e}")

        i = end  # Cập nhật biến i

video_root = "/mmlabworkspace/Datasets/AIC2023/"
mapframe_root = "/home/visedit/WorkingSpace/AIC2023/Data/Mapframe"
output_root = "/mmlabworkspace/Datasets/AIC2023/Batch3/Audio"

for batch in ["Batch3"]:
    video_batch_path = os.path.join(video_root, batch, "Videos")
    for root, dirs, files in os.walk(video_batch_path):
        files = natsorted(files)
        for file in tqdm(files, desc=f"Processing {batch}"):
            if file.endswith(".mp4"):
                video_path = os.path.join(root, file)
                mapframe_path = os.path.join(mapframe_root, os.path.splitext(file)[0] + ".csv")
                if os.path.exists(mapframe_path):
                    process_video(video_path, mapframe_path, output_root)
                else:
                    print(f"Không tìm thấy mapframe cho {file}")

print("Đã hoàn thành xử lý tất cả video!")
