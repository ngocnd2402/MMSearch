import faiss
import os
import numpy as np
from tqdm import tqdm
from PIL import Image
import torch
import glob
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
from lavis.models import load_model_and_preprocess
import sys 
sys.path.append('/mmlabworkspace/Students/visedit/AIC2023/Sketch_LVM')
from src.model_LN_prompt import Model
from torchvision import transforms
    
class Blip1Embedding:
    def __init__(self):
        self.device = "cpu"
        self.text_model = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='text', device=self.device)
        self.image_model = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='image', device=self.device)
        self.text_pipe = (
            pipe.input('text')
            .map('text', 'vec', self.text_model)
            .output('vec')
        )
        self.img_pipe = (
            pipe.input('img')
            .map('img', 'vec', self.image_model)  
            .output('vec')
        )
        
    def embed_text(self, text: str) -> np.ndarray:
        output_text = self.text_pipe(text)
        text_embedd = output_text.get()
        text_vec = np.array(text_embedd).reshape(-1)
        return text_vec
    
    def embed_image(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")

        output_image = self.img_pipe(image)
        image_embedd = output_image.get()
        image_vec = np.array(image_embedd).reshape(-1)
        return image_vec   

    
class Blip2Embedding:
    def __init__(self):
        self.device = 'cuda'
        self.model, self.vis_processors, self.txt_processors = load_model_and_preprocess(name="blip2_feature_extractor", model_type="coco", is_eval=True, device=self.device)
    
    def embed_text(self, text: str) -> np.ndarray:
        text_processed = self.txt_processors["eval"](text)
        sample = {"text_input": [text_processed]}
        text_emb = self.model.extract_features(sample, mode="text").text_embeds[0,0,:]
        text_emb_np = text_emb.cpu().detach().numpy()
        text_emb = np.array(text_emb_np).reshape(-1)
        return text_emb

    def embed_image(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")
        image_processed = self.vis_processors["eval"](image).unsqueeze(0).to(self.device)
        sample = {"image": image_processed}
        image_emb = self.model.extract_features(sample, mode="image").image_embeds[0,0,:]
        image_emb_np = image_emb.cpu().detach().numpy()
        image_emb = np.array(image_emb_np).reshape(-1)
        return image_emb

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

class PoseIndexer:
    def __init__(self, features_path: str):
        self.index, self.pose_frame_mapping = self.indexing_methods(features_path)

    def indexing_methods(self, features_path: str) -> faiss.Index:
        pose_feature_list = []
        pose_frame_mapping = {}

        for batch_folder in tqdm(os.listdir(features_path)):
            batch_path = os.path.join(features_path, batch_folder)

            for video_folder in os.listdir(batch_path):
                video_path = os.path.join(batch_path, video_folder)

                for frame_npy in os.listdir(video_path):
                    frame_path = os.path.join(video_path, frame_npy)
                    if os.path.isfile(frame_path) and frame_path.endswith('.npy'):
                        frame_vectors = np.load(frame_path)
                        for vec in frame_vectors:
                            pose_feature_list.append(vec)
                            frame_path_jpg = frame_path.replace('.npy', '.jpg').split('/')[-3:]
                            frame_path_jpg = "/".join(frame_path_jpg)
                            pose_frame_mapping[len(pose_feature_list) - 1] = frame_path_jpg

        pose_features = np.vstack(pose_feature_list).astype('float32')
        index = faiss.IndexFlatL2(pose_features.shape[1])
        index.add(pose_features)
        return index, pose_frame_mapping

class PoseSearchEngine:
    def __init__(self, indexer: PoseIndexer):
        self.indexer = indexer

    @staticmethod
    def calculate_relative_distances(vector):
        num_points = len(vector) // 2
        distances = []
        if num_points < 2:
            return np.array(distances)

        for i in range(1, num_points):
            pivot_x, pivot_y = vector[0], vector[1]
            current_x, current_y = vector[i * 2], vector[i * 2 + 1]
            distances.extend([abs(current_x - pivot_x), abs(current_y - pivot_y)])

            for j in range(1, i):
                prev_x, prev_y = vector[j * 2], vector[j * 2 + 1]
                distances.extend([abs(current_x - prev_x), abs(current_y - prev_y)])

        return np.array(distances)

    def search(self, query_list: List[float], topk: int) -> List[Dict]:
        query_arr = np.array(query_list, dtype='float32')
        relative_query_arr = self.calculate_relative_distances(query_arr).reshape(1, -1)
        index, pose_frame_mapping = self.indexer.index, self.indexer.pose_frame_mapping
        distances, indices = index.search(relative_query_arr, topk)

        return [
            {
                "frame": pose_frame_mapping.get(index),
                "distance": float(distances[0][i])
            }
            for i, index in enumerate(indices[0]) if index in pose_frame_mapping
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
