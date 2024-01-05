import os
import numpy as np
from natsort import natsorted

def calculate_relative_distances(vector):
    num_points = len(vector) // 2
    distances = []
    angles = []

    for i in range(1, num_points):
        pivot_x, pivot_y = vector[0], vector[1]
        current_x, current_y = vector[i * 2], vector[i * 2 + 1]
        distances.extend([current_x - pivot_x, current_y - pivot_y])

        for j in range(1, i):
            prev_x, prev_y = vector[j * 2], vector[j * 2 + 1]
            distances.extend([current_x - prev_x, current_y - prev_y])
            angle = np.arctan2(current_y - prev_y, current_x - prev_x)
            angles.append(angle)

    return np.concatenate([distances, angles])

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
                all_frame_vectors = []

                for vf in vector_files:
                    vector = np.load(os.path.join(frame_pose_path, vf))
                    relative_distance_vector = calculate_relative_distances(vector)
                    all_frame_vectors.append(relative_distance_vector)

                if all_frame_vectors:
                    concatenated_vector = np.vstack(all_frame_vectors)
                    frame_human_path = os.path.join(video_human_path, frame_folder + '.npy')
                    np.save(frame_human_path, concatenated_vector)

pose_path = 'Features/Pose'
human_path = 'Features/Vector_Pose'
concatenate_and_save_vectors(pose_path, human_path)
