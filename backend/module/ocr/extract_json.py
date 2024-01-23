import os
import json

START_ID = 198138 + 1
FOLDER_LV0 = 'Backend/OCR/infer-new'
OUTPUT_FILE = 'JSON/ocr_Batch3.json'
RANGE = ['L21', 'L35']

def extract_for_1_video(file_path):
    frame_objs = []
    mapping = {}
    with open(file_path, 'r', encoding='utf-8') as rf:
        lines = rf.readlines()
    for line in lines:
        text = line.split('\t')[1].strip()
        frame = line.split('_')[0]
        if frame not in mapping:
            frame_obj = {
                'id': len(frame_objs),
                'frame': frame,
                'ocr_text': text
            }
            mapping[frame] = len(frame_objs)
            frame_objs.append(frame_obj) 
        else:
            frame_objs[mapping[frame]]['ocr_text'] += ' ' + text

    return frame_objs

if __name__ == '__main__':
    start_id = START_ID
    frame_objs = []

    for folder_lv1 in sorted(os.listdir(FOLDER_LV0)):
        if folder_lv1 < RANGE[0] or folder_lv1 > RANGE[1]:
            continue
        
        dir_lv1 = os.path.join(FOLDER_LV0, folder_lv1)

        for txt_file in sorted(os.listdir(dir_lv1)):
            # Extract for 1 video
            video_name = txt_file.split('.')[0]
            print(video_name)
            txt_path = os.path.join(dir_lv1, txt_file)
            temp_frame_objs = extract_for_1_video(txt_path)

            # Make temp_frame_objs compatible with frame_objs
            for frame_obj in temp_frame_objs:
                frame_obj['id'] += start_id
                frame_obj['frame'] = os.path.join(folder_lv1, video_name, frame_obj['frame'])
            
            # Update frame_objs, start_id
            frame_objs = frame_objs + temp_frame_objs
            start_id = start_id + len(temp_frame_objs)

    # Wrtie to json file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as wf:
        json.dump(frame_objs, wf, ensure_ascii=False, indent=4)
