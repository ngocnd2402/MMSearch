import os

CHECKPOINT_PATH = 'checkpoint (Batch3).txt'
VIDEO_SEGMENTS_PATH = '/home/visedit/AIC2023/Backend/ASR/video_segments_16kHz_Batch3'

# Make sure to open the checkpoint file in append mode ('a') so that existing content is not overwritten.
with open(CHECKPOINT_PATH, 'a') as checkpoint_file:
    for video in sorted(os.listdir(VIDEO_SEGMENTS_PATH)):
        video_path = os.path.join(VIDEO_SEGMENTS_PATH, video)

        for audio in sorted(os.listdir(video_path)):
            audio_path = os.path.join(video_path, audio)

            # Write the audio path to the checkpoint file
            checkpoint_file.write(audio_path + '\n')

# The checkpoint file will be automatically closed when the 'with' block exits.


