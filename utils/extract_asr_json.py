import os
import json

# Đọc nội dung từ file txt
TRANSCRIPTION_CHECKPOINT_PATH = "/home/visedit/AIC2023/Backend/ASR/Vietnamese-wave2vec/transcription_checkpoint (Batch2).txt"
MAPFRAME_PATH = "/home/visedit/AIC2023/Trash/Mapping"
with open(TRANSCRIPTION_CHECKPOINT_PATH, 'r') as txt_file:
    txt_lines = txt_file.readlines()

# Chuyển đổi nội dung từ txt thành định dạng JSON yêu cầu
json_data = []
count = 70250
for line in txt_lines:
    line = line.strip()
    
    video_info, asr_text = line.split('\t')
    video, frame_range = video_info.split('-')
    frame_start, frame_end = frame_range.split('_')

    csv_file_path = os.path.join(MAPFRAME_PATH, f"{video}.csv")

    frame_idx_mapping = {}

    if os.path.exists(csv_file_path):
        # Đọc file CSV và ánh xạ từ "n" sang "frame_idx"
        with open(csv_file_path, 'r') as csv_file:
            csv_lines = csv_file.readlines()
        for csv_line in csv_lines[1:]:
            parts = csv_line.strip().split(',')
            frame_n = int(parts[0])
            frame_idx = int(parts[3])
            frame_idx_mapping[frame_n] = frame_idx

    json_data.append({
        "id":count,
        "video": video,
        "frame_start": frame_idx_mapping[int(frame_start)],
        "frame_end": frame_idx_mapping[int(frame_end)],
        "asr_text": asr_text
    })

    count+=1

# Ghi dữ liệu vào file JSON
with open('/home/visedit/AIC2023/JSON/asr_batch2.json', 'w') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
