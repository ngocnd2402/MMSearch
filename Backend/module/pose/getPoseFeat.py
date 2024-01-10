import numpy as np
import cv2
import torch
from super_gradients.training import models
from pathlib import Path
from natsort import natsorted
import os

yolo_nas_pose = models.get("yolo_nas_pose_l", pretrained_weights="coco_pose").cuda()

def visual(keypoints, input_file, pose_idx, img_width, img_height):
    image = cv2.imread(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = '/mmlabworkspace/Students/visedit/AIC2023/Backend/POSE/'
    img_path = os.path.join(output_dir, f'{base_name}_pose{pose_idx}.jpg')
    normalized_keypoints = [[[x / img_width, y / img_height] for x, y, c in pose] for pose in keypoints]

    connections = [
        (1, 2), (1, 3), (2, 4), (3, 5), (4, 6),
        (1, 7), (2, 8), (7, 8), (7, 9), (8, 10), (9, 11), (10, 12),
        (0, 13) 
    ]

    for pose in normalized_keypoints:
        for start_idx, end_idx in connections:
            if start_idx < len(pose) and end_idx < len(pose) and pose[start_idx] and pose[end_idx]:
                start_point = (int(pose[start_idx][0] * img_width), int(pose[start_idx][1] * img_height))
                end_point = (int(pose[end_idx][0] * img_width), int(pose[end_idx][1] * img_height))
                cv2.line(image, start_point, end_point, (0, 255, 0), 2)  # Green line with thickness 2

        for x, y in pose:
            x_abs = int(x * img_width)
            y_abs = int(y * img_height)
            cv2.circle(image, (x_abs, y_abs), 5, (255, 0, 0), -1)  # Blue circle with radius 5

    cv2.imwrite(img_path, image)
    print(f"Visualized image saved to {img_path}")

def save_keypoints(keypoints, input_file, pose_idx, img_width, img_height):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = 'Backend/POSE/'
    txt_path = os.path.join(output_dir, f'{base_name}_pose{pose_idx}.txt')
    normalized_keypoints = [[[x/img_width, y/img_height] for x, y, _ in pose] for pose in keypoints]

    with open(txt_path, 'w') as txt_file:
        for pose in normalized_keypoints:
            for x, y in pose:
                txt_file.write(f'{x}, {y}\n')
            txt_file.write('\n')
    print('Done')

def filter_keypoints(keypoints):
    indices = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    filtered_keypoints = []
    for pose in keypoints:
        filtered_pose = [pose[idx] for idx in indices if idx < len(pose)]
        midpoint = [round((pose[5][0] + pose[6][0]) / 2, 3), round((pose[5][1] + pose[6][1]) / 2, 3), round((pose[5][2] + pose[6][2]) / 2, 3)]
        filtered_pose.append(midpoint)
        filtered_keypoints.append(filtered_pose)
    return filtered_keypoints

def make_prediction(folder_path, start_index=0, end_index=None, confidence=0.55):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    yolo_nas_pose.to(device)
    base_path = Path(folder_path)
    output_base_path = Path("Features/Pose")

    sorted_folders = natsorted(base_path.iterdir())
    if end_index is None:
        end_index = len(sorted_folders)

    for idx, l_folder in enumerate(sorted_folders):
        if idx < start_index or idx >= end_index:
            continue  # Skip folders outside the specified range

        if l_folder.is_dir():
            for v_folder in natsorted(l_folder.iterdir()):
                if v_folder.is_dir():
                    for img_file in natsorted(v_folder.glob("*.jpg")):
                        process_image(img_file, output_base_path, confidence)
                        
def process_image(img_path, output_base_path, confidence):
    prediction = yolo_nas_pose.predict(str(img_path), conf=confidence)
    image = cv2.imread(str(img_path))
    height, width = image.shape[:2]

    for idx, image_prediction in enumerate(prediction._images_prediction_lst):
        keypoints = image_prediction.prediction.poses
        if keypoints.size == 0:  
            continue  

        filtered_keypoints = filter_keypoints(keypoints)
        relative_path = img_path.relative_to(Path("Data/Reframe"))
        person_dir = output_base_path.joinpath(relative_path.parent, relative_path.stem)

        person_dir.mkdir(parents=True, exist_ok=True)

        for id, pose in enumerate(filtered_keypoints):
            save_person_keypoints(pose, person_dir, id, width, height)


def save_person_keypoints(pose, person_dir, person_id, img_width, img_height):
    flattened_keypoints = [coord / img_width if i % 2 == 0 else coord / img_height for keypoint in pose for i, coord in enumerate(keypoint[:2])]
    expected_length = 28
    if len(flattened_keypoints) != expected_length:
        print(f"Skipping person {person_id} due to incomplete keypoints.")
        return

    npy_path = person_dir.joinpath(f"{person_id}.npy")
    np_vec = np.array(flattened_keypoints)
    np.save(str(npy_path), np_vec)
    print(f"Keypoints for person {person_id} saved to {npy_path}")

input_path = "Data/Reframe"
make_prediction(input_path, start_index=0, end_index=10)