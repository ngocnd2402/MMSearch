import faiss
import os
import numpy as np
from tqdm import tqdm
from PIL import Image
import torch
import clip
from typing import List, Dict
import os
import numpy as np
from tqdm import tqdm 
from natsort import natsorted
import time
from concurrent.futures import ThreadPoolExecutor
import requests
from io import BytesIO
from towhee import pipe, ops

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.device = "cuda"
            cls._instance.clip_model, cls._instance.clip_preprocess = clip.load("ViT-B/32", device=cls._instance.device)
        return cls._instance

class ClipTextEmbedding:
    def __init__(self, model_manager):
        self.device = model_manager.device
        self.clip_model = model_manager.clip_model

    def __call__(self, text: str) -> np.ndarray:
        text_inputs = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            text_feature = self.clip_model.encode_text(text_inputs)[0]
        return text_feature.detach().cpu().numpy()

class ClipImageEmbedding:
    def __init__(self, model_manager):
        self.device = model_manager.device
        self.clip_model = model_manager.clip_model
        self.clip_preprocess = model_manager.clip_preprocess

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
    
class BlipTextEmbedding:
    def __init__(self):
        self.device = "cpu"
        self.model_text = ops.image_text_embedding.blip(model_name='blip_itm_large_coco', modality='text', device=self.device)
        self.text_pipe = (
            pipe.input('text')
            .map('text', 'vec', self.model_text)
            .output('vec')
        )

    def __call__(self, text: str) -> np.ndarray:
        output_text = self.text_pipe(text)
        text_embedd = output_text.get()
        text_vec = np.array(text_embedd).reshape(-1)
        return text_vec
    
class FeatureIndexer:
    def __init__(self, features_path: str, model_type: str, keyframe_folder: str):
        self.index, self.video_frame_mapping = self.indexing_methods(features_path, model_type, keyframe_folder)

    def indexing_methods(self, features_path: str, model_type: str, keyframe_folder: str) -> faiss.Index:
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


class FeatureSearchEngine:
    def __init__(self, indexer: FeatureIndexer):
        self.indexer = indexer

    def search(self, query_arr: np.array, topk: int) -> List[dict]:
        index, video_frame_mapping = self.indexer.index, self.indexer.video_frame_mapping
        query_arr /= np.linalg.norm(query_arr)
        distances, indices = index.search(np.expand_dims(query_arr, axis=0), topk)

        def worker(i):
            index_to_find = indices[0][i]
            distance = 1 - distances[0][i]
            frame_path = video_frame_mapping.get(index_to_find)
            return {"frame": frame_path, "cosine_similarity": distance}

        search_result = []
        with ThreadPoolExecutor(max_workers=topk) as executor:
            futures = [executor.submit(worker, i) for i in range(topk)]
            for future in futures:
                result = future.result()
                search_result.append(result)
        return search_result