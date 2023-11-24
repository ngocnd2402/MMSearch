import numpy as np
from towhee import pipe, ops
from scipy.spatial.distance import cosine
import os
import torch
from natsort import natsorted

# Initialize GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_image = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='image', device=device)

# Tạo một pipeline để xử lý hình ảnh và trích xuất vector một lần
img_pipe = (
    pipe.input('path')  # Sử dụng 'path' thay vì 'url'
    .map('path', 'img', ops.image_decode.cv2_rgb())
    .map('img', 'vec', model_image)
    .output('vec')  # Chỉ cần đầu ra là vector
)

# Path to the folder containing keyframes
keyframes_folder = 'Data/Reframe'

# Set the index to start from (L11)
start_index = 21
end_index = 28

# Loop through each Lxx folder starting from L11
for idx, folder_name in enumerate(natsorted(os.listdir(keyframes_folder))):
    if idx < start_index - 1:
        continue  # Skip folders until L11
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

                    output_img = img_pipe(image_path)
                    img_embedd = output_img.get()

                    # Add vector to the vectors list for the current keyframe
                    vectors.append(np.array(img_embedd).reshape(-1))
                    print(f"Processed image {image_name} ({image_idx + 1}/{len(image_paths)})")

                # Transform the vectors list into a numpy array
                vectors = np.array(vectors)

                # Save the numpy array to a .npy file
                output_file_path = os.path.join('Features/Bvecs', f'{subfolder_name}.npy')
                np.save(output_file_path, vectors)
                print(f"Saved vectors to {output_file_path}")

        print(f"Finished processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")