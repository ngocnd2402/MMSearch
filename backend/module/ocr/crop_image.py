import numpy as np
import cv2
import os
import glob
import json 
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'raw', type=str, help='Raw images.'
    )
    parser.add_argument(
        'polygons', type=str, help='Polygons'
    )
    parser.add_argument(
        'cropped', type=str, help='Path to folder to contain cropped images'
    )
    parser.add_argument(
        'dropped', type=str, help='Path to folder to contain dropped cropped images'
    )

    args = parser.parse_args()
    return args

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

# Calculate the area of the polygon
def find_area(polygon):
    polygon = np.array(polygon)
    x = polygon[:, 0]
    y = polygon[:, 1]

    S1 = np.sum(x*np.roll(y,-1))
    S2 = np.sum(y*np.roll(x,-1))

    area = .5*np.absolute(S1 - S2)

    return area

def relu(x):
    return x if x >= 0 else 0


args = parse_args()
count_drop = 0
count_used = 0
count_undetected = 0
threshold = 0.6

for path in glob.glob(os.path.join(args.polygons, "*.json")):
    with open(path) as f:
        content = json.load(f)
    
    poly_scr_pairs = content['boundary_result']
    img_name = os.path.basename(path).split('_')[1].split('.')[0]
    count = 0
    img = cv2.imread(f'{args.raw}/{img_name}.jpg')

    if len(poly_scr_pairs) == 0: # No polygon is detected in image
        count_undetected += 1
        croped_path = f'{args.cropped_output}/{img_name}_{count:04n}.jpg'
        cv2.imwrite(croped_path, img)
    else:
        # poly_scr_pairs: list of bounding boxes
        # poly_scr_pair : a single bounding box
        for poly_scr_pair in poly_scr_pairs:
            length = len(poly_scr_pair) - 1 # Drop score
            scr = poly_scr_pair[-1]
            polygon = [[relu(round(poly_scr_pair[i])), relu(round(poly_scr_pair[i + 1]))] for i in range(0, len(poly_scr_pair) - 1, 2) ]        
                
            # Crop image
            cropped_img = crop_image(img, polygon)
            if scr >= threshold:
                croped_path = f'{args.cropped}/{img_name}_{count:04n}.jpg'
                count_used += 1
            else:
                croped_path = f'{args.dropped}/{img_name}_{count:04n}.jpg'
                count_drop += 1

            cv2.imwrite(croped_path, cropped_img)

            count += 1

print('Total: ', count_drop + count_used + count_undetected)
print('No used images: ', count_used) # images which will be used to pass into parseq
print('No dropped images: ', count_drop) # images which will be dropped
print('No undetected images: ', count_undetected) # images which are not detected by dbnetpp