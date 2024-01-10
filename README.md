# MMSearch - A Multi-Media System For Videos Retrieval From Visual Data
The MMSearch system composed by **several components**:

* **Semantic**-based Module
* **OCR**-based Module
* **ASR**-based Module
* **Object**-based Module
* **Sketch**-based Module
* **Pose**-based Module
* **Reranking** by User Feedback

We offer a web-based application for managing the MMSearch tool:
* Frontend: [Next.js](https://nextjs.org/)
* Backend: [FastAPI](https://fastapi.tiangolo.com/)

## Suggested Folder Structure

The following structure is recommended for organizing the various components of the MMSearch system:
- `root`
  - `backend`
    - `module` - This contains the complete implementation of functions for each module.
      - `semantic`
      - `ocr`
      - `asr`
      - `object`
      - `sketch`
      - `pose`
  - `frontend` - All the methods for creating an efficient user interface.
  - `features` - The directory for storing all extracted features from each module.
    - `bvecs` - Folder containing BLIP features.
    - `pvecs` - Folder containing Pose features.
    - `sketch` - Folder containing Sketch features.
  - `json` - This directory stores JSON database for some modules.
  - `data` - This includes the keyframe database following the preprocessing of the video data and its metadata.
    - `keyframe`
    - `mapping`

## Getting Started
### Requirements
* [Anaconda](https://www.anaconda.com/download)
* [Node.js](https://nodejs.org/en)

To create required conda environment, run this command:
```bash
pip install -r env/server.txt
```

### Preprocessing your data
To prepare your data, start by segmenting the video database into individual frames using the following command:
```bash
python preprocessing/cut_frame.py
```
Next, for audio retrieval purposes, extract audio in MP3 format from the video database with the following command:
```bash
python preprocessing/cut_audio.py
```
Generate mapping metadata with key details like frame numbers and timestamps to accurately position frames in videos for many purpose. Execute the following command:
```bash
python preprocessing/make_mapping.py
```

### Build & Run Each Component
1. Semantic-based Module
Commencing the process, we employ the BLIP image encoder to derive precise visual feature vectors for every image within the keyframe database. These vectors are subsequently stored in the .np format through the execution of the following command:
```bash
python backend/module/semantic/getBlipFeat.py
```
After this process, you will obtain a database vector containing distinctive features for each image in the keyframe database.
2. OCR-based Module
In this module, we use DBNET in mmocr framework and PARSeq model. First, you need to create the openmmlab enviroment. Then run the script to do all thing for this module
```bash
cd ocr 
bash install_mmocr.sh
bash run.sh
fuckkkkk
```
Then địt con mẹ mày
3. ASR-based Module
```bash

```
4. Object-based Module
- To begin, you should detect the objects in every frame by using the following command:
```bash
python backend/module/object/detr.py
```
- After obtaining the result JSON file, you can create the inverted index database by executing:
```bash
python backend/module/object/inverted_file.py
```
5. Sketch-based Module
```bash
```
6. Pose-based Module
To obtain pose features from every frame, run:
```bash
python backend/module/pose/getPoseFeat.py
```
The result will be saved as `features/pvecs`.

### Create Frontend Enviroment 
Run the following commands to install frontend dependencies:
```bash
cd frontend
```

```bash
npm install
```

## Running MMSearch on Localhost
```bash
bash bash/start.sh
```
If all went smoothly, your MMSearch should now be up and running. Simply go to http://localhost:8888 and have fun. Thhese are the default settings, so if you made any changes, please adjust the address as needed.

Furthermore, the Core API specification is accessible (by default) at https://localhost:7777/docs/ .