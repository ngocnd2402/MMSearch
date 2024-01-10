import os
import json
import librosa
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from tqdm import tqdm
from natsort import natsorted

def transcribe_audio(audio_path, processor, model):
    audio, sampling_rate = librosa.load(audio_path, sr=16000)
    input_features = processor(audio, sampling_rate=sampling_rate, return_tensors="pt").input_features
    input_features = input_features.to('cuda')
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0] 

def process_batch(batch_path, output_json, processor, model):
    data = []
    id_counter = 1

    for root, dirs, files in os.walk(batch_path):
        sorted_dirs = natsorted(dirs)
        dirs[:] = sorted_dirs  
        sorted_files = natsorted(files)
        for file in tqdm(sorted_files, desc=f"Processing {root}"):
            if file.endswith(".mp3"):
                audio_path = os.path.join(root, file)
                text = transcribe_audio(audio_path, processor, model)

                frame_start, frame_end = file.replace('.mp3', '').split('-')
                video_folder, video_file = os.path.basename(root).split('_')
                video_id = video_folder + '_' + video_file

                data.append({
                    "id": id_counter,
                    "frame_start": f"{video_folder}/{video_id}/{int(float(frame_start)):06d}.jpg",
                    "frame_end": f"{video_folder}/{video_id}/{int(float(frame_end)):06d}.jpg",
                    "text": text
                })
                id_counter += 1

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

processor = WhisperProcessor.from_pretrained("openai/whisper-large")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large")
model.config.forced_decoder_ids = None
model = model.to('cuda')

root_path = "/YOUR_DATA_ROOT_PATH/"
json_path = "/YOUR_OUTPUT_PATH/"

for batch in os.listdir(root_path):
    batch_audio_path = os.path.join(root_path, batch, "Audio")
    output_json = f"{json_path}/asr_{batch}.json"
    process_batch(batch_audio_path, output_json, processor, model)
print("Processing completed for all batches.")