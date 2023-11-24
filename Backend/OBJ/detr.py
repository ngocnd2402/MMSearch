from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import os
import json
from tqdm import tqdm
from natsort import natsorted

image_folder = "/home/visedit/WorkingSpace/AIC2023/Data/Reframe"
json_output_path = '/home/visedit/WorkingSpace/AIC2023/JSON/object.json'
device = "cuda"
batch_size = 8  
def obj_detect_batch(image_paths, processor, model):
    images = [Image.open(image_path) for image_path in image_paths]

    inputs = processor(images=images, return_tensors="pt").to(device)
    outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1] for image in images])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)

    detections_list = []

    for result, image in zip(results, images):
        detections_dict = {}
        for score, label, box in zip(result["scores"], result["labels"], result["boxes"]):
            box_data = box.tolist()
            image_width, image_height = image.size
            x_tl, y_tl, x_br, y_br = box_data
            w_norm = x_br - x_tl
            h_norm = y_br - y_tl
            x_tl_norm = x_tl / image_width
            y_tl_norm = y_tl / image_height
            w_norm /= image_width
            h_norm /= image_height
            normalized_box = [round(x_tl_norm, 4), round(y_tl_norm, 4), round(w_norm, 4), round(h_norm, 4)]

            class_name = model.config.id2label[label.item()]

            if class_name not in detections_dict:
                detections_dict[class_name] = []

            detections_dict[class_name].append(normalized_box)

        detections_list.append(detections_dict)

    return detections_list


def to_batches(iterable, batch_size):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]

all_results = {}

processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm").to(device)

subdirectories = natsorted([f.path for f in os.scandir(image_folder) if f.is_dir()])

for subdirectory in tqdm(subdirectories, desc="Processing subdirectories"):
    image_paths = [os.path.join(root, file) for root, dirs, files in os.walk(subdirectory) for file in natsorted(files) if file.lower().endswith(('.jpg'))]

    for batch in tqdm(list(to_batches(image_paths, batch_size)), desc="Processing batches", leave=False):
        results_batch = obj_detect_batch(batch, processor, model)

        for image_path, results in zip(batch, results_batch):
            image_name = os.path.relpath(image_path, image_folder)
            all_results[image_name] = results

with open(json_output_path, "w") as json_file:
    json.dump(all_results, json_file, indent=4)
