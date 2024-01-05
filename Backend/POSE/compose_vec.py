import os
import numpy as np
from natsort import natsorted

def concatenate_and_save_vectors(pose_path, human_path):
    for batch_folder in natsorted(os.listdir(pose_path)):
        batch_pose_path = os.path.join(pose_path, batch_folder)
        batch_human_path = os.path.join(human_path, batch_folder)
        os.makedirs(batch_human_path, exist_ok=True)

        for video_folder in natsorted(os.listdir(batch_pose_path)):
            video_pose_path = os.path.join(batch_pose_path, video_folder)
            video_human_path = os.path.join(batch_human_path, video_folder)
            os.makedirs(video_human_path, exist_ok=True)

            for frame_folder in natsorted(os.listdir(video_pose_path)):
                frame_pose_path = os.path.join(video_pose_path, frame_folder)
                vector_files = natsorted(os.listdir(frame_pose_path))
                vectors = [np.load(os.path.join(frame_pose_path, vf)) for vf in vector_files]

                if vectors:
                    concatenated_vector = np.vstack(vectors)
                    frame_human_path = os.path.join(video_human_path, frame_folder + '.npy')
                    np.save(frame_human_path, concatenated_vector)

pose_path = 'Features/Pose'
human_path = 'Features/Human'
concatenate_and_save_vectors(pose_path, human_path)