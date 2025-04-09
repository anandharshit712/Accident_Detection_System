import os
import cv2

VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov')
SEQUENCE_LENGTH = 16  # Number of frames to extract

def extract_frames_from_video(video_path, output_dir, sequence_length=SEQUENCE_LENGTH):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames == 0:
        print(f"⚠️ Skipping empty video: {video_path}")
        return

    # Sample 16 evenly spaced frame indices
    frame_indices = [
        int(i * total_frames / sequence_length)
        for i in range(sequence_length)
    ]

    os.makedirs(output_dir, exist_ok=True)

    for idx, frame_index in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = cap.read()
        if not success:
            print(f"❌ Failed to read frame {frame_index} from {video_path}")
            continue

        frame_file = os.path.join(output_dir, f"frame_{idx:03d}.jpg")
        cv2.imwrite(frame_file, frame)

    cap.release()

def process_folder(folder_path):
    print(f"\n📂 Processing: {folder_path}")
    for file in os.listdir(folder_path):
        if file.endswith(VIDEO_EXTENSIONS):
            video_path = os.path.join(folder_path, file)
            video_name = os.path.splitext(file)[0]
            output_dir = os.path.join(folder_path, video_name)

            # Skip if already extracted
            if os.path.exists(output_dir):
                print(f"✅ Skipping already extracted: {video_name}")
                continue

            print(f"🔄 Extracting: {video_name}")
            extract_frames_from_video(video_path, output_dir)


def main():
    base_dataset = "F:/Major_project_accident_detection/input/accident/Video-Accident-Dataset"  # Change this if your folder name is different

    for subfolder in ["accident", "no_accident"]:
        full_path = os.path.join(base_dataset, subfolder)
        if os.path.exists(full_path):
            process_folder(full_path)
        else:
            print(f"❌ Folder not found: {full_path}")

if __name__ == "__main__":
    main()
