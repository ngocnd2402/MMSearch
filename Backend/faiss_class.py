import faiss
import os
import numpy as np
from tqdm import tqdm
from PIL import Image
import torch
from typing import List, Dict
import os
import numpy as np
from tqdm import tqdm
from natsort import natsorted
import time
import requests
from io import BytesIO
import base64
from towhee import pipe, ops
import sys 
sys.path.append('/mmlabworkspace/Students/visedit/AIC2023/Sketch_LVM')
from src.model_LN_prompt import Model
from torchvision import transforms
    
class BlipTextEmbedding:
    def __init__(self):
        self.device = "cpu"
        self.model = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='text', device=self.device)
        self.text_pipe = (
            pipe.input('text')
            .map('text', 'vec', self.model)
            .output('vec')
        )

    def __call__(self, text: str) -> np.ndarray:
        output_text = self.text_pipe(text)
        text_embedd = output_text.get()
        text_vec = np.array(text_embedd).reshape(-1)
        return text_vec

class BlipImageEmbedding:
    def __init__(self):
        self.device = "cpu"
        self.model = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='image', device=self.device)
        self.img_pipe = (
            pipe.input('img')
            .map('img', 'vec', self.model)  
            .output('vec')
        )

    def __call__(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")

        output_image = self.img_pipe(image)
        image_embedd = output_image.get()
        image_vec = np.array(image_embedd).reshape(-1)
        return image_vec   

class SketchEmbedding:
    def __init__(self, device="cuda", CKPT_PATH="/mmlabworkspace/Students/visedit/AIC2023/Sketch_LVM/saved_models/LN_prompt/last.ckpt"):
        self.device = device
        self.model = Model()
        self.model_checkpoint = torch.load(CKPT_PATH, map_location=self.device)
        self.model.load_state_dict(self.model_checkpoint['state_dict'])
        self.model.to(self.device)
        self.model.eval()

    @staticmethod
    def get_transform():
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def convert_to_image(self, sketch_data: str) -> Image.Image:
        if sketch_data.startswith("http://") or sketch_data.startswith("https://"):
            response = requests.get(sketch_data)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            base64_data = sketch_data.split(",")[1]
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data)).convert("RGB")
        return image

    def __call__(self, sketch_data: str) -> np.ndarray:
        image = self.convert_to_image(sketch_data)
        transform = self.get_transform()
        image_tensor = transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            image_feat = self.model(image_tensor, dtype='sketch')
            image_feat_numpy = image_feat.cpu().numpy()
            image_norm = (image_feat_numpy) / (np.linalg.norm(image_feat_numpy))
            image_vec = np.array(image_norm).reshape(-1)
        return image_vec

    
class VectorIndexer:
    def __init__(self, features_path: str, keyframe_folder: str):
        self.index, self.video_frame_mapping = self.indexing_methods(features_path, keyframe_folder)

    def indexing_methods(self, features_path: str, keyframe_folder: str) -> faiss.Index:
        npy_files = natsorted([file for file in os.listdir(features_path) if file.endswith(".npy")])
        features_list = []
        video_frame_mapping = {}

        for feat_npy in tqdm(npy_files):
            feats_arr = np.load(os.path.join(features_path, feat_npy))
            video_name = os.path.splitext(feat_npy)[0]
            prefix = video_name.split('_')[0]
            mapping = sorted(os.listdir(os.path.join(keyframe_folder, prefix, video_name)))

            for id, feat in enumerate(feats_arr):
                feat /= np.linalg.norm(feat)
                features_list.append(feat)
                video_frame_mapping[len(features_list) - 1] = os.path.join(prefix, video_name, mapping[id])

        photo_features = np.vstack(features_list).astype('float32')
        features_list = None
        n, d = photo_features.shape
        index = faiss.IndexFlatIP(d)
        index.add(photo_features)
        photo_features = None
        return index, video_frame_mapping


class VectorSearchEngine:
    def __init__(self, indexer: VectorIndexer):
        self.indexer = indexer

    def search(self, query_arr: np.array, topk: int) -> List[dict]:
        index, video_frame_mapping = self.indexer.index, self.indexer.video_frame_mapping
        query_arr /= np.linalg.norm(query_arr)
        distances, indices = index.search(np.expand_dims(query_arr, axis=0), topk)
        
        return [
            {
                "frame": video_frame_mapping.get(index),
                "cosine_similarity": 1 - distances[0][i]
            }
            for i, index in enumerate(indices[0]) if index in video_frame_mapping
        ]

class RerankImages:
    def __init__(self, alpha: float, beta: float, gamma: float):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def reformulate(self, query_vector: np.ndarray, relevant_vectors: List[np.ndarray], irrelevant_vectors: List[np.ndarray]) -> np.ndarray:
        if query_vector is None or not query_vector.size:
            text_query = np.zeros_like(relevant_vectors[0] if relevant_vectors else irrelevant_vectors[0])
        else:
            text_query = query_vector
        sum_relevant = np.sum(relevant_vectors, axis=0) if relevant_vectors else np.zeros_like(text_query)
        norm_relevant = sum_relevant / np.linalg.norm(sum_relevant) if np.linalg.norm(sum_relevant) != 0 else np.zeros_like(text_query)
        sum_irrelevant = np.sum(irrelevant_vectors, axis=0) if irrelevant_vectors else np.zeros_like(text_query)
        norm_irrelevnt = sum_irrelevant / np.linalg.norm(sum_irrelevant) if np.linalg.norm(sum_irrelevant) != 0 else np.zeros_like(text_query)
        modified_query = self.alpha * text_query + self.beta * norm_relevant - self.gamma * norm_irrelevnt
        return modified_query
