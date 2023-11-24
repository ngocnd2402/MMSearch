from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import soundfile as sf
import torch
import os

# load model and tokenizer
processor = Wav2Vec2Processor.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h")
model = Wav2Vec2ForCTC.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h")

# define function to read in sound file
def map_to_array(batch:dict):
    speech, _ = sf.read(batch["file"])
    batch["speech"] = speech
    return batch

# transcribe an audio (.wav) file into Vietnamese transcription
def transcribe(audio_path:str):
    ds = map_to_array({
        "file": audio_path
    })
    # tokenize
    input_values = processor(ds["speech"], return_tensors="pt", padding="longest").input_values  # Batch size 1
    # retrieve logits
    logits = model(input_values).logits
    # take argmax and use greedy decoding method
    predicted_ids = torch.argmax(logits, dim=-1)
    # final output. Example: ['Bản tin hôm nay sẽ có những nội dung chính như sau']
    transcription = processor.batch_decode(predicted_ids)

    return transcription[0]


TRANSCRIPTION_PATH = 'transcriptions.txt'
VIDEO_SEGEMENTS_PATH = '/mmlabworkspace/Students/ngoc_AIC2023/Backend/ASR/video_segments_16kHz'

with open(TRANSCRIPTION_PATH, 'w') as f:

    for video in sorted(os.listdir(VIDEO_SEGEMENTS_PATH)):
        video_path = os.path.join(VIDEO_SEGEMENTS_PATH,video)

        for audio in sorted(os.listdir(video_path)):
            audio_name = audio.split('.')[0]
            audio_path = os.path.join(video_path,audio)

            # Transcribe audio, skipping empty transcriptions
            transcription = transcribe(audio_path)
            
            if len(transcription) < 20:
                continue

            # Write to the transcription file in the desired format
            line = f"{audio_name}\t{transcription}\n"
            f.write(line)

            print(f"Transcribed: {audio_name}")

