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
    - `metadata`
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
If you possess your own dataset containing videos, please preprocess the data according to our guidelines:

```bash
python preprocessing/cut_frame.py
```

Once completed, your video data will be efficiently divided into frames.

### Build & Run Each Component
1. Semantic-based Module
- Commencing the process, we employ the BLIP image encoder to derive precise visual feature vectors for every image within the keyframe database. These vectors are subsequently stored in the .np format through the execution of the following command:
```bash
python backend/module/semantic/getBlipFeat.py
```
- After this process, you will obtain a database vector containing distinctive features for each image in the keyframe database.
2. OCR-based Module
```bash

```
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
## MMSearch UI
Run the following commands to install frontend dependencies:
```bash
cd frontend
```

```bash
npm install
```