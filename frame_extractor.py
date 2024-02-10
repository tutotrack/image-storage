import cv2
import os
import numpy as np

def extract_frames_on_scene_change(video_path, save_path=None, change_threshold=0.5, font_size=1, font_color=(0, 255, 255)):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return None

    if save_path and not os.path.exists(save_path):
        os.makedirs(save_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    prev_frame = None
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale and resize for faster processing
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.resize(gray_frame, (320, 240))

        if prev_frame is not None:
            # Calculate frame difference
            frame_diff = cv2.absdiff(gray_frame, prev_frame)
            non_zero_count = np.count_nonzero(frame_diff)
            norm_diff = non_zero_count / (320 * 240)

            if norm_diff > change_threshold:
                timestamp = frame_count / fps
                hours, rem = divmod(timestamp, 3600)
                minutes, seconds = divmod(rem, 60)
                timestamp_str = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
                filename_timestamp_str = "{:0>2}h{:0>2}m{:0>2}s".format(int(hours), int(minutes), int(seconds))

                # Add timestamp to the frame
                cv2.putText(frame, timestamp_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, 2)

                # Save the frame
                frame_filename = f'scene_change_{frame_count}_{filename_timestamp_str}.jpg'
                frame_save_path = os.path.join(save_path, frame_filename)
                cv2.imwrite(frame_save_path, frame)

        prev_frame = gray_frame
        frame_count += 1

    cap.release()
    return save_path if save_path else os.getcwd()

