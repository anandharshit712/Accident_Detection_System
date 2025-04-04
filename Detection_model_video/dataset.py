import os
import cv2
import torch
import random
import numpy as np
from torch.utils.data import Dataset
from torchvision import transforms

class AccidentDataset(Dataset):
    def __init__(self, root_dir, sequence_length=16, transform=None):
        self.samples = []
        self.sequence_length = sequence_length
        self.transform = transform

        for label_name, label in [('no_accident', 0), ('accident', 1)]:
            folder = os.path.join(root_dir, label_name)
            for fname in os.listdir(folder):
                if fname.endswith(('.mp4', '.avi', '.mov')):
                    self.samples.append((os.path.join(folder, fname), label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        frames = self._extract_frames(path)
        return frames, torch.tensor([label], dtype=torch.float32)

    def _extract_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_idxs = self._sample_frames(total_frames)

        frames = []
        for i in frame_idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, frame = cap.read()
            if not success:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.transform:
                frame = self.transform(frame)
            frames.append(frame)

        cap.release()
        # Pad if not enough frames
        while len(frames) < self.sequence_length:
            frames.append(frames[-1])
        return torch.stack(frames)  # [T, C, H, W]

    def _sample_frames(self, total_frames):
        if total_frames <= self.sequence_length:
            return list(range(total_frames))
        start = random.randint(0, total_frames - self.sequence_length)
        return list(range(start, start + self.sequence_length))
