import json
import random
import cv2
import os

json_path = '/home/visedit/WorkingSpace/AIC2023/JSON/object.json'

with open(json_path) as f:
    data = json.load(f)
sample_images = random.sample(list(data.keys()), 50)

for img_path in sample_images:

    image_path = '/home/visedit/WorkingSpace/AIC2023/Data/Reframe/' + img_path
    img = cv2.imread(image_path)

    if img is None:
        continue
    if data[img_path]:
        for obj, bboxes in data[img_path].items():
            for bbox in bboxes:
                x, y, w, h = bbox
                x = int(x * img.shape[1])
                y = int(y * img.shape[0])
                w = int(w * img.shape[1])
                h = int(h * img.shape[0])
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    save_path = '/home/visedit/WorkingSpace/AIC2023/Backend/OBJECT/test_plot/' + os.path.basename(img_path)
    cv2.imwrite(save_path, img)
