import torch
import torchvision.transforms as transforms
from collections import deque
import cv2
from model import AccidentDetector
from receive_frames import get_frames
import asyncio

# Config
BUFFER_SIZE = 16
IMG_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = AccidentDetector().to(DEVICE)
model.load_state_dict(torch.load("accident_model.pth", map_location=DEVICE))
model.eval()

# Transform
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Buffer to hold last N frames
frame_buffer = deque(maxlen=BUFFER_SIZE)

async def detect_from_stream():
    async for frame in get_frames():  # Receive frame from receive_frame.py
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor = transform(frame_rgb)
        frame_buffer.append(tensor)

        if len(frame_buffer) == BUFFER_SIZE:
            input_tensor = torch.stack(list(frame_buffer)).unsqueeze(0).to(DEVICE)  # Shape: [1, 16, C, H, W]
            with torch.no_grad():
                output = model(input_tensor)
                prediction = (output.item() > 0.5)
                print("🚨 Accident Detected" if prediction else "✅ No Accident")

# Run detection loop
asyncio.run(detect_from_stream())
