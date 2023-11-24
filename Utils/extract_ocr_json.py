import os
import json
from collections import OrderedDict

INFERENCE_PATH = "/mmlabworkspace/Students/ngocnd/Backend/inference-result"
JSON_FILE_PATH = "ocr_final.json"
JSON_LIST = []
count = 0

# loop
for batch in sorted(os.listdir(INFERENCE_PATH)):
    batch_full_path = os.path.join(INFERENCE_PATH, batch)
    
    for video_txt in sorted(os.listdir(batch_full_path)):
        video = video_txt.split('.')[0].split('_')[-1]
        
        # Reading from video txt file
        with open(os.path.join(batch_full_path, video_txt), 'r') as f:
            lines = f.readlines()

        current_img_name = None
        current_ocr_text = ""

        for line in lines:
            img, ocr_text = line.split('\t')
            img_name = img.split('.')[0].split('_')[0]

            if img_name != current_img_name:
                if current_img_name is not None:
                    JSON_LIST.append({
                        "id": count,
                        "frame": f"{batch}/{video}/{current_img_name}",
                        "ocr_text": current_ocr_text
                    })
                    count += 1

                # Reset values for a new image
                current_img_name = img_name
                current_ocr_text = ""
            
            current_ocr_text += f" {ocr_text[:-1]}"

        # Add the last image's data
        if current_img_name is not None:
            JSON_LIST.append({
                "id": count,
                "frame": f"{batch}/{video}/{current_img_name}",
                "ocr_text": current_ocr_text
            })
            count += 1

# Write JSON data to file
with open(JSON_FILE_PATH, 'w') as json_file:
    json.dump(JSON_LIST, json_file, ensure_ascii=False, indent=4)
