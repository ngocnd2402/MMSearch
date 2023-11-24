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
from towhee import pipe, ops
import clip
from concurrent.futures import ThreadPoolExecutor
    
class BlipTextEmbedding:
    def __init__(self):
        self.device = "cuda"
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

class ClipTextEmbedding:
    def __init__(self):
        self.device = "cuda"
        self.clip_model, _ = clip.load("ViT-B/32", device=self.device)

    def __call__(self, text: str) -> np.ndarray:
        text_inputs = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            text_feature = self.clip_model.encode_text(text_inputs)[0]
        return text_feature.detach().cpu().numpy()

class ClipImageEmbedding:
    def __init__(self):
        self.device = "cuda"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)

    def __call__(self, image_path: str) -> np.ndarray:
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            image = Image.open(image_path).convert("RGB")
        image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_feature = self.clip_model.encode_image(image_input)[0]
        return image_feature.detach().cpu().numpy()

    
class VectorIndexer:
    def __init__(self, features_path: str, images_folder: str):
        self.index, self.image_mapping = self.indexing_methods(features_path, images_folder)

    def indexing_methods(self, features_path: str, images_folder: str):
        npy_files = natsorted([file for file in os.listdir(features_path) if file.endswith(".npy")])
        features_list = []
        image_mapping = {}

        for feat_npy in tqdm(npy_files):
            feat = np.load(os.path.join(features_path, feat_npy))
            feat /= np.linalg.norm(feat)  
            features_list.append(feat)
            image_name = os.path.splitext(feat_npy)[0] + '.jpg'
            image_mapping[len(features_list) - 1] = os.path.join(images_folder, image_name)

        feature_vectors = np.vstack(features_list).astype('float32')
        features_list = None
        n, d = feature_vectors.shape
        index = faiss.IndexFlatIP(d) 
        index.add(feature_vectors)
        feature_vectors = None
        return index, image_mapping


class VectorSearchEngine:
    def __init__(self, indexer: VectorIndexer):
        self.indexer = indexer

    def search(self, query_arr: np.ndarray, topk: int) -> List[dict]:
        index, image_mapping = self.indexer.index, self.indexer.image_mapping
        query_arr /= np.linalg.norm(query_arr)
        distances, indices = index.search(np.expand_dims(query_arr, axis=0), topk)

        search_results = []
        for i in range(topk):
            index_to_find = indices[0][i]
            distance = 1 - distances[0][i]
            image_path = image_mapping.get(index_to_find)
            search_results.append({"image": image_path, "cosine_similarity": distance})

        return search_results
