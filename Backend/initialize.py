from faiss_class import (
    BlipTextEmbedding,
    BlipImageEmbedding,
    SketchEmbedding,
    VectorIndexer,
    VectorSearchEngine,
    PoseIndexer,
    PoseSearchEngine,
    RerankImages
)
from meili import Meilisearch
from OBJ.obj_query import ObjectRetrieval
import os
from fastapi import FastAPI, Form, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any
import traceback
from PIL import Image
from math import ceil, floor
import asyncio
import numpy as np
import csv
import json
from natsort import natsorted
from fastapi import File, UploadFile, Form, HTTPException
from fastapi.param_functions import File

# GLOBAL VARIABLES

blip_text_embedd = BlipTextEmbedding()
blip_image_embedd = BlipImageEmbedding()
sketch_embedd = SketchEmbedding()

KEYFRAME_PATH = "Data/Reframe"
MAPFRAME_PATH = "Data/Mapframe"
METADATA_PATH = "Data/Metadata"
FEATURES_PATH = "Features/Bvecs"
SKETCH_PATH = "Features/Sketch"
POSE_PATH = "Features/Pvecs"
frontend_mapping_folder = "Data/Mapframe"
inverted_file = "JSON/inverted_file.json"

vector_indexer = VectorIndexer(FEATURES_PATH, KEYFRAME_PATH)
sketch_indexer = VectorIndexer(SKETCH_PATH, KEYFRAME_PATH)
pose_indexer = PoseIndexer(POSE_PATH)
vector_search_engine = VectorSearchEngine(vector_indexer)
sketch_search_engine = VectorSearchEngine(sketch_indexer)
pose_search_engine = PoseSearchEngine(pose_indexer)
ocr_search_engine = Meilisearch('OCR')
asr_search_engine = Meilisearch('ASR')
obj_search_engine = ObjectRetrieval(inverted_file)
rerank_images = RerankImages(alpha=1, beta=1, gamma=1)

def find_image_position(folder_name, image_name):
    files = natsorted(os.listdir(folder_name))
    try:
        position = files.index(image_name)
        return position
    except ValueError:
        return -1

def split_path(input_path):
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    return directory, filename

def get_video_name(image_path):
    parts = image_path.split('/')
    video_name = parts[-2]
    return video_name

def get_feature_vector(feats_dir, image_path):
    directory, filename = split_path(image_path)
    video_name = get_video_name(image_path)
    feat_path = os.path.join(feats_dir, f'{video_name}.npy')
    position = find_image_position(directory, filename)
    if position != -1:
        return np.load(feat_path)[position]
    else:
        return None

def calculate_relative_distances(vector):
    num_points = len(vector) // 2
    distances = []
    for i in range(1, num_points):
        pivot_x, pivot_y = vector[0], vector[1]
        current_x, current_y = vector[i * 2], vector[i * 2 + 1]
        distances.extend([abs(current_x - pivot_x), abs(current_y - pivot_y)])
        for j in range(1, i):
            prev_x, prev_y = vector[j * 2], vector[j * 2 + 1]
            distances.extend([abs(current_x - prev_x), abs(current_y - prev_y)])
    return np.array(distances)