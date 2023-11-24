import numpy as np
from towhee import pipe, ops
from scipy.spatial.distance import cosine
import os
import torch
from natsort import natsorted
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_image = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='image', device=device)

img_pipe = (
    pipe.input('path')  
    .map('path', 'img', ops.image_decode.cv2_rgb())
    .map('img', 'vec', model_image)
    .output('vec')  
)

def to_batches(files, batch_size):
    for i in range(0, len(files), batch_size):
        yield files[i:i+batch_size]

def process_files(files, root, img_pipe):
    for file in files:
        if file.endswith('.jpg'):
            img_path = os.path.join(root, file)
            output_img = img_pipe(img_path)
            img_embedd = output_img.get()
            img_vec = np.array(img_embedd).reshape(-1)
            img_name = os.path.basename(img_path).split('.')[0]
            out_save_path = os.path.join('Evaluation/Flickr8K/Bvecs', f'{img_name}.npy')
            np.save(out_save_path, img_vec)

def count_images(folder):
    count = 0
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.jpg'):
                count += 1
    return count

def main():
    keyframes_folder = '/home/visedit/WorkingSpace/AIC2023/Data/Reframe/L01/L01_V001'
    batch_size = 32

    total_images = count_images(keyframes_folder)
    print(f'Total images in {keyframes_folder}: {total_images}')

    for root, dirs, files in os.walk(keyframes_folder):
        sorted_dirs = natsorted(dirs)
        dirs[:] = sorted_dirs 
        sorted_files = natsorted(files)
        files[:] = sorted_files

        for batch_files in tqdm(to_batches(files, batch_size), desc="Processing Batches", unit="batch"):
            process_files(batch_files, root, img_pipe)

if __name__ == "__main__":
    main()
