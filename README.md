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
    - `video`
    - `audio`

## Getting Started
### Requirements
* [Anaconda](https://www.anaconda.com/download)
* [Node.js](https://nodejs.org/en)

To create required conda environment, run this command:
```bash
pip install -r env/server.txt
```

Our pretrained weights of OCR can be found here [Google Drive](https://drive.google.com/drive/folders/1ptwkEELYkYewb-667hSoftiWj4cv6I1J)

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
#### 1. Semantic-based Module
Navigate to the semantic module directory:
```bash
cd backend/module/semantic
```
Use the BLIP image encoder to extract visual feature vectors from images in the keyframe database. These vectors are saved in the .np format:
```bash
python getBlipFeat.py
```
#### 2. OCR-based Module
Switch to the OCR module directory:
```bash
cd backend/module/ocr
```
Set up and use DBNET in the mmocr framework and the PARSeq model. Create the openmmlab environment and run the scripts for the OCR module:
```bash
bash install_mmocr.sh
bash run.sh
```
#### 3. ASR-based Module
Change to the ASR module directory:
```bash
cd backend/module/asr
```
Utilize Whisper Large for audio-to-text conversion. Execute this after segmenting the audio in the previous step:
```bash
python getASR.py
```
#### 4. Object-based Module
Go to the object module directory:
```bash
cd backend/module/object
```
First, detect objects in every frame:
```bash
python detr.py
```
Then, create an inverted index database from the resulting JSON file:
```bash
python inverted_file.py
```
#### 5. Sketch-based Module
Go to the sketch module directory:
```bash
cd backend/module/sketch
```
First, clone the original repository:
```bash
git clone https://github.com/aneeshan95/Sketch_LVM
```
Download the pretrained_weight and put it in the right folder. Then, extract sketch feature vectors for all images in your keyframe database:
```bash
python getSketch.py
```
#### 6. Pose-based Module
Get to the pose module directory:
```bash
cd backend/module/pose
```
To obtain pose features from every frame, run:
```bash
python backend/module/pose/getPoseFeat.py
```
#### 7. Add data to MeiliSearch
After completing the OCR and ASR steps in the previous section to generate the JSON index, proceed to add the index to Meilisearch using the following command:
```bash
python add_meili.py
```
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
