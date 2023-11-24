import numpy as np
from CLIP_QUERY import ModelManager, ClipImageEmbedding
from scipy.spatial.distance import cosine
import os
import torch
from natsort import natsorted

# Initialize GPU if available
model_manager = ModelManager()
clip_image_embedd = ClipImageEmbedding(model_manager)
print(clip_image_embedd.device)

# Path to the folder containing keyframes
keyframes_folder = 'Data/Reframe'

# Set the index to start from (L11)
start_index = 1
end_index = 10

# Loop through each Lxx folder starting from L11
for idx, folder_name in enumerate(natsorted(os.listdir(keyframes_folder))):
    if idx < start_index - 1:
        continue  
    if idx > end_index:
        break

    folder_path = os.path.join(keyframes_folder, folder_name)
    if os.path.isdir(folder_path):
        print(f"Processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")

        # Loop through each Lxx_Vxxx subfolder
        for subfolder_name in natsorted(os.listdir(folder_path)):
            subfolder_path = os.path.join(folder_path, subfolder_name)
            if os.path.isdir(subfolder_path):
                vectors = []
                print(f"Processing subfolder {subfolder_name}")

                # Loop through each .jpg image file
                image_paths = natsorted([f for f in os.listdir(subfolder_path) if f.endswith('.jpg')])
                for image_idx, image_name in enumerate(image_paths):
                    image_path = os.path.join(subfolder_path, image_name)

                    img_embedd = clip_image_embedd(image_path)
        
                    # Add vector to the vectors list for the current keyframe
                    vectors.append(np.array(img_embedd))
                    print(f"Processed image {image_name} ({image_idx + 1}/{len(image_paths)})")

                # Transform the vectors list into a numpy array
                vectors = np.array(vectors)

                # Save the numpy array to a .npy file
                output_file_path = os.path.join('Features/Cvecs', f'{subfolder_name}.npy')
                np.save(output_file_path, vectors)
                print(f"Saved vectors to {output_file_path}")

        print(f"Finished processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")