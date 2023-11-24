import numpy as np
import sys
import os
from tqdm import tqdm
from natsort import natsorted
import sys 
sys.path.append('/home/visedit/WorkingSpace/AIC2023/Backend')
from CLIP.CLIP_QUERY import ModelManager, ClipImageEmbedding


def to_batches(files, batch_size):
    for i in range(0, len(files), batch_size):
        yield files[i:i+batch_size]

def process_files(files, root, clip_image_embedd):
    for file in files:
        if file.endswith('.jpg'):
            img_path = os.path.join(root, file)
            img_embedd = np.array(clip_image_embedd(img_path))
            img_name = os.path.basename(img_path).split('.')[0]
            out_save_path = os.path.join('Evaluation/Flickr8K/Cvecs', f'{img_name}.npy')
            np.save(out_save_path, img_embedd)
            
def count_images(folder):
    count = 0
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.npy'):
                count += 1
    return count

def main():
    model_manager = ModelManager()
    clip_image_embedd = ClipImageEmbedding(model_manager)
    print(clip_image_embedd.device)
    keyframes_folder = 'Evaluation/Flickr8K/Images'
    batch_size = 16  
    total_images = count_images(keyframes_folder)
    print(f'Total images in {keyframes_folder}: {total_images}')
    
    for root, dirs, files in os.walk(keyframes_folder):
        sorted_dirs = natsorted(dirs)
        dirs[:] = sorted_dirs 
        sorted_files = natsorted(files)
        files[:] = sorted_files

        for batch_files in tqdm(to_batches(files, batch_size), desc="Processing Batches", unit="batch"):
            process_files(batch_files, root, clip_image_embedd)

if __name__ == "__main__":
    main()
