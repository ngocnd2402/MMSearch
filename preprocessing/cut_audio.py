import os
import pandas as pd
from moviepy.editor import VideoFileClip
from natsort import natsorted

def process_video(video_path, mapframe_path, output_root):
    df = pd.read_csv(mapframe_path)
    video = VideoFileClip(video_path)
    audio = video.audio

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join(output_root, video_name)

    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
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

        audio_clip = audio.subclip(start_time, end_time)
        output_filename = os.path.join(output_folder, f"{start_frame}-{end_frame}.mp3")
        audio_clip.write_audiofile(output_filename, codec='mp3')

        # Update variable i
        i = end

# Root paths
video_root = "YOUR_VIDEO_PATH"
mapframe_root = "/home/visedit/WorkingSpace/AIC2023/Data/Mapframe"
output_root = "/mmlabworkspace/Datasets/AIC2023/AudioOutput"

for batch in os.listdir(video_root):
    if os.path.isdir(os.path.join(video_root, batch)):
        video_batch_path = os.path.join(video_root, batch, "Videos")
        for root, dirs, files in os.walk(video_batch_path):
            files = natsorted(files)
            for file in files:
                if file.endswith(".mp4"):
                    video_path = os.path.join(root, file)
                    mapframe_path = os.path.join(mapframe_root, os.path.splitext(file)[0] + ".csv")
                    if os.path.exists(mapframe_path):
                        process_video(video_path, mapframe_path, output_root)
                    else:
                        print(f"No mapframe found for {file}")

print("Processing completed for all videos!")