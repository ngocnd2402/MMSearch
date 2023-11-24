import streamlit as st
import random
import os
from PIL import Image

from blip_eval import BLIPRetrieval, blip_text_embedd, vector_search_engine

GT_PATH = "/mmlabworkspace/Students/visedit/AIC2023/Evaluation/Flickr8K/captions.txt"
KEYFRAME_PATH = "/mmlabworkspace/Students/visedit/AIC2023/Evaluation/Flickr8K/Images"

def load_captions(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

captions = load_captions(GT_PATH)
blip_retrieval = BLIPRetrieval(GT_PATH, blip_text_embedd)

st.title("BLIP Image Search")

query_option = st.selectbox("Choose a query option", ["Random Query", "Input Query"])
if query_option == "Random Query":
    query = random.choice(captions)
else:
    query = st.text_input("Enter your query")

if query:
    st.write("Query:", query)
    embedd = blip_text_embedd(query)
    retrieved_images = vector_search_engine.search(embedd, topk=10)  # Adjust topk as needed

    for img in retrieved_images:
        image_path = os.path.join(KEYFRAME_PATH, os.path.basename(img['image']))
        if os.path.exists(image_path):
            st.image(image_path)
        else:
            st.error(f"Image not found: {image_path}")