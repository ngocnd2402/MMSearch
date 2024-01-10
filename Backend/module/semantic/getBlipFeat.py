import numpy as np
from towhee import pipe, ops
from scipy.spatial.distance import cosine
import os
import torch
from natsort import natsorted

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_image = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='image', device=device)

img_pipe = (
    pipe.input('path')  
    .map('path', 'img', ops.image_decode.cv2_rgb())
    .map('img', 'vec', model_image)
    .output('vec')  
)

keyframes_folder = 'KEYFRAME_INPUT'
start_index = 0  # START INDEX
end_index = 35  # END INDEX

for idx, folder_name in enumerate(natsorted(os.listdir(keyframes_folder))):
    if idx < start_index - 1:
        continue 
    if idx > end_index:
        break

    folder_path = os.path.join(keyframes_folder, folder_name)
    if os.path.isdir(folder_path):
        print(f"Processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")

        for subfolder_name in natsorted(os.listdir(folder_path)):
            subfolder_path = os.path.join(folder_path, subfolder_name)
            if os.path.isdir(subfolder_path):
                vectors = []
                print(f"Processing subfolder {subfolder_name}")
                image_paths = natsorted([f for f in os.listdir(subfolder_path) if f.endswith('.jpg')])
                
                for image_idx, image_name in enumerate(image_paths):
                    image_path = os.path.join(subfolder_path, image_name)

                    output_img = img_pipe(image_path)
                    img_embedd = output_img.get()
                    vectors.append(np.array(img_embedd).reshape(-1))
                    print(f"Processed image {image_name} ({image_idx + 1}/{len(image_paths)})")

                vectors = np.array(vectors)

                output_folder = os.path.join('Features/Bvecs')
                os.makedirs(output_folder, exist_ok=True)

                output_file_path = os.path.join(output_folder, f'{subfolder_name}.npy')
                np.save(output_file_path, vectors)
                print(f"Saved vectors to {output_file_path}")

        print(f"Finished processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")
