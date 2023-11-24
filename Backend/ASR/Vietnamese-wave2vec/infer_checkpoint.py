from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import soundfile as sf
import torch
import os

# load model and tokenizer
processor = Wav2Vec2Processor.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h")
model = Wav2Vec2ForCTC.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h").to('cuda:0')

# define function to read in sound file
def map_to_array(batch: dict):
    speech, _ = sf.read(batch["file"])
    batch["speech"] = speech
    return batch

# transcribe an audio (.wav) file into Vietnamese transcription
def transcribe(audio_path: str):
    ds = map_to_array({
        "file": audio_path
    })
    # tokenize
    input_values = processor(ds["speech"], return_tensors="pt", padding="longest").input_values.to('cuda:0')  # Batch size 1
    # retrieve logits
    logits = model(input_values).logits
    # take argmax and use greedy decoding method
    predicted_ids = torch.argmax(logits, dim=-1)
    # final output. Example: ['Bản tin hôm nay sẽ có những nội dung chính như sau']
    transcription = processor.batch_decode(predicted_ids)

    return transcription[0]

TRANSCRIPTION_CHECKPOINT_PATH = 'transcription_checkpoint (Batch3).txt'
CHECKPOINT_PATH = 'checkpoint (Batch3).txt'
VIDEO_SEGMENTS_PATH = '/home/visedit/AIC2023/Backend/ASR/video_segments_16kHz_Batch3'
START_LINE_INDEX = 0  # Change this to the desired starting line index

# Đọc danh sách dòng thông tin từ tệp checkpoint
with open(CHECKPOINT_PATH, 'r') as checkpoint_file:
    checkpoint_lines = checkpoint_file.readlines()[START_LINE_INDEX:]

# Mở tệp transcription_checkpoint để ghi kết quả
with open(TRANSCRIPTION_CHECKPOINT_PATH, 'a') as f:
    for audio_path in checkpoint_lines:
        audio_path = audio_path.strip()  # Remove leading/trailing whitespaces and newline characters

        # Transcribe audio, skipping empty transcriptions
        if (transcription := transcribe(audio_path)) and len(transcription) >= 20:
            # Write to the transcription file in the desired format
            audio_name = os.path.basename(audio_path).split('.')[0]
            line = f"{audio_name}\t{transcription}\n"
            f.write(line)

            print(f"Transcribed: {audio_name}")
