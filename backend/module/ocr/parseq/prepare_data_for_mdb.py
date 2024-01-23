# This code prepares data to make mdb file for parseq
import os 
import glob
import cv2
import numpy as np
import json 

IMG_PATH = '../uaic22-data/uaic2022_training_data_parseq/images'
CROPPED_IMG_PATH = 'data/cropped-images'
LABEL_PATH = '../uaic22-data/uaic2022_training_data_parseq/labels'
TRAIN_PATH = 'data/train_gt_file.txt'
VAL_PATH = 'data/val_gt_file.txt'

# Crop bbox
def crop_image(img , polygon):
    ## (1) Crop the bounding rect
    polygon = np.array(polygon)
    rect = cv2.boundingRect(polygon)
    x,y,w,h = rect
    croped = img[y:y+h, x:x+w].copy()
    ## (2) make mask
    polygon = polygon - polygon.min(axis=0)
    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [polygon], -1, (255, 255, 255), -1, cv2.LINE_AA)
    ## (3) do bit-op
    dst = cv2.bitwise_and(croped, croped, mask=mask)

    return dst

train_file = open(TRAIN_PATH, 'w')
val_file = open(VAL_PATH, 'w')

paths = glob.glob(f'{LABEL_PATH}/*')
num_imgs = len(paths)
val_ratio = 0.2

val_idx_end = int(num_imgs*(val_ratio))
failed_text = []

for i, path in enumerate(paths):
    with open(path) as f:
        words = json.load(f)

    img_name = os.path.basename(path).split('.')[0]
    img = cv2.imread(f'{IMG_PATH}/{img_name}.jpg')
    n_words = len(words)

    for id in range(n_words):
        text = words[id]['text']
        cropped_img_name = f'{img_name}_{id:04n}'

        # Skip ### text
        if text == '###':
            continue
            
        # Mark empty text
        if text == '':
            failed_text.append(cropped_img_name)

        polygon = words[id]['points']

        if i < val_idx_end:
            val_file.write(f'{cropped_img_name}.jpg\t{text}\n')
        else:
            train_file.write(f'{cropped_img_name}.jpg\t{text}\n')
        cropped_img_path = f'{CROPPED_IMG_PATH}/{cropped_img_name}.jpg'
        cropped_img = crop_image(img, polygon)
        cv2.imwrite(cropped_img_path, cropped_img)

    if (i + 1) % 100 == 0:
        print(i + 1)

train_file.close()
val_file.close()

print(set(failed_text))