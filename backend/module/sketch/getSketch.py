import os
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from natsort import natsorted
from torchvision import transforms

# Update the path to your SKETCHLVM clone
sys.path.append('PATH_TO_YOUR_SKETCHLVM_CLONE')
from src.model_LN_prompt import Model

CKPT_PATH = 'THE_SKETCHLVM_CKPT_PATH'
model = Model()
model_checkpoint = torch.load(CKPT_PATH)
model.load_state_dict(model_checkpoint['state_dict'])
model.eval()

def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

class ImageEmbedding:
    def __init__(self, device="cuda"):
        self.device = device

    def __call__(self, image_path: str) -> np.ndarray:
        image = Image.open(image_path).convert("RGB")
        transform = get_transform()
        image_tensor = transform(image).unsqueeze(0).to(model.device)

        with torch.no_grad():
            image_feat = model(image_tensor, dtype='image')
            image_feat = image_feat.cpu().numpy()
            image_feat /= np.linalg.norm(image_feat)
            image_vec = np.array(image_feat).reshape(-1)
        return image_vec

keyframes_folder = 'Data/Reframe'
image_embedding = ImageEmbedding()

start_index = 1  # START INDEX
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
                    img_embedd = np.array(image_embedding(image_path))
                    vectors.append(np.array(img_embedd).reshape(-1))
                    print(f"Processed image {image_name} ({image_idx + 1}/{len(image_paths)})")

                vectors = np.array(vectors)
                output_folder = os.path.join('Features/Sketch', folder_name)
                os.makedirs(output_folder, exist_ok=True)  # Create folder if not exists
                output_file_path = os.path.join(output_folder, f'{subfolder_name}.npy')
                np.save(output_file_path, vectors)
                print(f"Saved vectors to {output_file_path}")
        print(f"Finished processing folder {folder_name} ({idx + 1}/{len(os.listdir(keyframes_folder))})")
