from faiss_class import (
    BlipTextEmbedding,
    BlipImageEmbedding,
    VectorIndexer,
    VectorSearchEngine,
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
from math import ceil, floor
import asyncio
import csv

# GLOBAL VARIABLES

blip_text_embedd = BlipTextEmbedding()
blip_image_embedd = BlipImageEmbedding()

KEYFRAME_PATH = "Data/Reframe"
MAPFRAME_PATH = "Data/Mapframe"
METADATA_PATH = "Data/Metadata"
FEATURES_PATH = "Features/Bvecs"
frontend_mapping_folder = "Data/Mapframe"
inverted_file = "JSON/inverted_file.json"

vector_indexer = VectorIndexer(FEATURES_PATH, KEYFRAME_PATH)
vector_search_engine = VectorSearchEngine(vector_indexer)
ocr_search_engine = Meilisearch('OCR')
asr_search_engine = Meilisearch('ASR')
obj_search_engine = ObjectRetrieval(inverted_file)
rerank_images = RerankImages(alpha=1, beta=1, gamma=1)