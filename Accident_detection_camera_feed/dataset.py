import os
from PIL import Image
import torch
from torch.utils.data import Dataset

class ImageSequenceDataset(Dataset):
    def __init__(self, root_dir, sequence_length=16, transform=None):
        self.samples = []
        self.sequence_length = sequence_length
        self.transform = transform

        for label_name, label in [('no_accident', 0), ('accident', 1)]:
            class_dir = os.path.join(root_dir, label_name)
            for entry in os.listdir(class_dir):
                entry_path = os.path.join(class_dir, entry)
                if os.path.isdir(entry_path):
                    self.samples.append((entry_path, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        folder_path, label = self.samples[idx]
        frame_files = sorted(os.listdir(folder_path))[:self.sequence_length]
        frames = []

        for fname in frame_files:
            frame_path = os.path.join(folder_path, fname)
            image = Image.open(frame_path).convert("RGB")
            if self.transform:
                image = self.transform(image)
            frames.append(image)

        while len(frames) < self.sequence_length:
            frames.append(frames[-1])  # Pad with last frame if needed

        sequence_tensor = torch.stack(frames)  # Shape: [T, C, H, W]
        return sequence_tensor, torch.tensor([label], dtype=torch.float32)
