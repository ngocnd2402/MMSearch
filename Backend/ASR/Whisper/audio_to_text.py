import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

processor = WhisperProcessor.from_pretrained("openai/whisper-large")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large")
model.config.forced_decoder_ids = None


audio_file_path = '/mmlabworkspace/Datasets/AIC2023/Batch2/Audio/L11_V002/1286.0-1340.0.mp3'
audio, sampling_rate = librosa.load(audio_file_path, sr=16000)
input_features = processor(audio, sampling_rate=sampling_rate, return_tensors="pt").input_features


predicted_ids = model.generate(input_features)
transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

print(transcription)