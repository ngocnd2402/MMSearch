from initialize import *

app = FastAPI(
    title="MMSearch - MMLAB",
    description="This is the API we are using at HCMC AI Challenge, please do not use for other purposes.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frame", StaticFiles(directory=KEYFRAME_PATH), name="frame")
app.mount("/mapframe", StaticFiles(directory=MAPFRAME_PATH), name="mapframe")
app.mount("/metadata", StaticFiles(directory=METADATA_PATH), name="metadata")

class RequestMock:
    def __init__(self, body):
        self._body = body

    async def json(self):
        return self._body

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content="<h1>InferaSearch API</h1><p>Welcome to the InferaSearch MMLAB API.</p>")

@app.post("/query_search")
async def blip_search(query: str = Form(...), topk: int = Form(...)):
    print("Received query:", query) 
    text_feat_arr = blip_text_embedd(query)
    topk_results = vector_search_engine.search(text_feat_arr, topk)
    return topk_results

@app.post("/image_search")
async def image_search(image_path: str = Form(...), topk: int = Form(...)):
    base_dir = '/mmlabworkspace/Students/visedit/AIC2023/Data/Reframe'
    feats_dir = '/mmlabworkspace/Students/visedit/AIC2023/Features/Bvecs'
    img_path = f'{base_dir}/{image_path}'
    image_feat_arr = get_feature_vector(feats_dir, img_path)
    topk_results = vector_search_engine.search(image_feat_arr, topk)
    return topk_results


@app.post("/ocr_search")
async def ocr_search(query: str = Form(...), topk: int = Form(...)):
    print("Received query:", query) 
    topk_results = ocr_search_engine.query(query, topk)
    for res in topk_results:
        res['frame'] += '.jpg'
    return topk_results

@app.post("/asr_search")
async def asr_search(query: str = Form(...), topk: int = Form(...)):
    print("Received query:", query) 
    asr_results = asr_search_engine.query(query, topk)
    formatted_results = []
    unique_frames = set()

    for result in asr_results:
        frame_start_path = result["frame_start"]
        frame_end_path = result["frame_end"]

        video_folder, start_frame = split_path(frame_start_path)
        _, end_frame = split_path(frame_end_path)
        video_folder_path = os.path.join(KEYFRAME_PATH, video_folder)

        start_frame_index = find_image_position(video_folder_path, start_frame)
        end_frame_index = find_image_position(video_folder_path, end_frame)

        if start_frame_index != -1 and end_frame_index != -1:
            for frame_number in range(start_frame_index, end_frame_index + 1):
                frame_name = natsorted(os.listdir(video_folder_path))[frame_number]
                frame_res_relative = os.path.join(video_folder, frame_name)

                if frame_res_relative not in unique_frames:
                    unique_frames.add(frame_res_relative)
                    formatted_results.append({"frame": frame_res_relative})
                    
    final_results = formatted_results[:topk]
    return final_results


@app.post("/object_search")
async def object_query(request: Request):
    body = await request.json()
    query_input = body['query_input']
    topk = body.get('topk', 10)
    results = obj_search_engine.search_image(query_input, topk)
    return results

@app.post("/sketch_search")
async def sketch_search(query: str = Form(...), topk: int = Form(...)):
    sketch_vector = sketch_embedd(query)
    search_results = sketch_search_engine.search(sketch_vector, topk)
    return search_results


@app.post("/combine_search")
async def combine_search(request: Request):
    body = await request.json()
    query_list = body.get("query", [])
    methods = body.get("methods", [])
    topk = body.get("topk", 10)

    if len(query_list) != len(methods):
        raise HTTPException(status_code=400, detail="The length of queries and methods must be equal.")

    combined_results = {}
    tasks = []

    async def search_and_update_results(method, query):
        if method == "query":
            result = await blip_search(query=query, topk=topk)
        elif method == "ocr":
            result = await ocr_search(query=query, topk=topk)
        elif method == "asr":
            result = await asr_search(query=query, topk=topk)
        elif method == "sketch":
            result = await sketch_search(query=query, topk=topk)
        elif method == "object":
            object_body = {'query_input': query, 'topk': topk}
            result = await object_query(RequestMock(object_body))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown search method: {method}")

        combined_results[method] = [r["frame"] for r in result if "frame" in r]

    for method, query in zip(methods, query_list):
        if method == "object":
            object_query_format = query 
            tasks.append(search_and_update_results(method, object_query_format))
        else:
            tasks.append(search_and_update_results(method, query))

    await asyncio.gather(*tasks)

    shared_results = set.intersection(*[set(results) for results in combined_results.values() if results])
    final_results = [{"frame": frame} for frame in shared_results][:topk]
    return final_results

@app.post("/rerank_search")
async def rerank_search(request: Request):

    body = await request.json()
    original_query = body.get('original_query')
    relevant_images = body['relevant_images']
    irrelevant_images = body['irrelevant_images']
    topk = body.get('topk', 10)

    base_dir = '/mmlabworkspace/Students/visedit/AIC2023/Data/Reframe'
    feats_dir = '/mmlabworkspace/Students/visedit/AIC2023/Features/Bvecs'
    sketchs_dir = "/mmlabworkspace/Students/visedit/AIC2023/Features/Sketch"

    def get_feature_vectors(images, directory):
        return [vec for img in images if (vec := get_feature_vector(directory, os.path.join(base_dir, img))) is not None]

    relevant_vectors = get_feature_vectors(relevant_images, sketchs_dir if original_query.startswith(("http://", "https://", "data:image/")) else feats_dir)
    irrelevant_vectors = get_feature_vectors(irrelevant_images, sketchs_dir if original_query.startswith(("http://", "https://", "data:image/")) else feats_dir)
    original_query_vector = sketch_embedd(original_query) if original_query.startswith(("http://", "https://", "data:image/")) else blip_text_embedd(original_query) if original_query else None
    modified_query_vector = rerank_images.reformulate(original_query_vector, relevant_vectors, irrelevant_vectors)
    search_engine = sketch_search_engine if original_query.startswith(("http://", "https://", "data:image/")) else vector_search_engine
    reranked_results = search_engine.search(modified_query_vector, topk)
    return reranked_results


    
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=7777, reload=False)
