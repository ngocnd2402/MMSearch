import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import csv
from Indexer_Engine import (
    BlipTextEmbedding,
    VectorIndexer,
    VectorSearchEngine
)
import json

GT_PATH = "/mmlabworkspace/Students/visedit/AIC2023/Evaluation/Flickr8K/captions.txt"
KEYFRAME_PATH = "/mmlabworkspace/Students/visedit/AIC2023/Evaluation/Flickr8K/Images"
FEATURES_PATH = "/mmlabworkspace/Students/visedit/AIC2023/Evaluation/Flickr8K/Bvecs"

blip_text_embedd = BlipTextEmbedding()
vector_indexer = VectorIndexer(FEATURES_PATH, KEYFRAME_PATH)
vector_search_engine = VectorSearchEngine(vector_indexer)

class BLIPRetrieval:
    def __init__(self, gt_path, text_embedder):
        self.gt_path = gt_path
        self.text_embedder = text_embedder
        self.gt_data = self.load_gt()

    def load_gt(self):
        temp_gt = {}
        with open(self.gt_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                image, caption = row
                if caption not in temp_gt:
                    temp_gt[caption] = []
                if image not in temp_gt[caption]:
                    temp_gt[caption].append(image)

        gt = [{'query': caption, 'relevant_images': images} for caption, images in temp_gt.items()]
        return gt


    def evaluate(self, vector_search_engine, batch_size=64):
        precision_scores, recall_scores, mrr_scores, ap_scores = [], [], [], []

        for batch in tqdm(to_batches(self.gt_data, batch_size), desc="Evaluating & Calculating MAP"):
            for item in batch:
                query = item['query']
                relevant_images = set(os.path.basename(img) for img in item['relevant_images'])
                embedd = self.text_embedder(query)
                topk_retrieval = len(relevant_images)
                retrieved_images = vector_search_engine.search(embedd, topk=topk_retrieval)

                relevant_retrieved_images = set()
                precisions = []
                rel_count = 0

                for i, image in enumerate(retrieved_images):
                    retrieved_image_path = os.path.basename(image['image'])
                    if retrieved_image_path in relevant_images:
                        relevant_retrieved_images.add(retrieved_image_path)
                        rel_count += 1
                        precisions.append(rel_count / (i + 1))

                precision = len(relevant_retrieved_images) / len(retrieved_images) if retrieved_images else 0
                recall = len(relevant_retrieved_images) / len(relevant_images) if relevant_images else 0
                first_relevant_rank = next((i for i, img in enumerate(retrieved_images) if os.path.basename(img['image']) in relevant_images), None)
                mrr = 1.0 / (first_relevant_rank + 1) if first_relevant_rank is not None else 0
                ap = np.mean(precisions) if precisions else 0

                precision_scores.append(precision)
                recall_scores.append(recall)
                mrr_scores.append(mrr)
                ap_scores.append(ap)

        avg_precision = np.mean(precision_scores)
        avg_recall = np.mean(recall_scores)
        avg_mrr = np.mean(mrr_scores)
        map_score = np.mean(ap_scores)

        return avg_precision, avg_recall, avg_mrr, map_score

def to_batches(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

blip_retrieval = BLIPRetrieval(GT_PATH, blip_text_embedd)
avg_precision, avg_recall, avg_mrr, map_score = blip_retrieval.evaluate(vector_search_engine)

print(f"Average Precision: {avg_precision}")
print(f"Average Recall: {avg_recall}")
print(f"Mean Reciprocal Rank: {avg_mrr}")
print(f"Mean Average Precision (MAP): {map_score}")