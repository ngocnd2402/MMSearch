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
cd preprocessing
```

```bash
python cut_frame.py
```

Once completed, your video data will be efficiently divided into frames.

### Build & Run Each Component
1. Semantic-based Module
- Commencing the process, we employ the BLIP image encoder to derive precise visual feature vectors for every image within the keyframe database. These vectors are subsequently stored in the .np format through the execution of the following command:
```bash
python backend/module/getBlipFeat.py
```
- After this process, you will obtain a database vector containing distinctive features for each image in the keyframe database.
2. OCR-based Module
```bash

```
3. ASR-based Module
```bash

```
4. Object-based Module
```bash

```
5. Sketch-based Module
```bash

```
6. Pose-based Module
```bash

```

## MMSearch UI
Run the following commands to install frontend dependencies:
```bash
cd frontend
```

```bash
npm install
```