import asyncio
import torch
from collections import deque, Counter
from torchvision import transforms
from model import AccidentDetector
from receive_frames import get_frames
import time
import numpy as np

# Config
SEQUENCE_LENGTH = 10
INTERVAL_SECONDS = 5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "saved_model/accident_model.pth"

# Transform
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def load_model():
    model = AccidentDetector().to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    return model

# Check and clean frames
def preprocess_sequence(frames):
    cleaned = [f for f in frames if f is not None]
    if len(cleaned) < SEQUENCE_LENGTH:
        raise ValueError(f"Only {len(cleaned)} valid frames available; need {SEQUENCE_LENGTH}.")
    processed = [transform(frame) for frame in cleaned]
    tensor = torch.stack(processed).unsqueeze(0)  # Shape: [1, seq_len, C, H, W]
    return tensor.to(DEVICE)

def predict(model, frames):
    input_tensor = preprocess_sequence(frames)
    with torch.no_grad():
        output = model(input_tensor)
        prob = output.item()
        label = "Accident" if prob > 0.5 else "Non Accident"
        return label, prob

async def stream_predict():
    print("🚀 Starting real-time prediction stream...")
    model = load_model()

    buffer = deque(maxlen=SEQUENCE_LENGTH)
    last_interval = time.time()
    predictions = []

    async for frame in get_frames():
        if frame is None:
            continue  # skip invalid frames

        buffer.append(frame)

        if len(buffer) == SEQUENCE_LENGTH:
            try:
                label, confidence = predict(model, list(buffer))
                predictions.append((label, confidence))
            except Exception as e:
                print(f"⚠️ Prediction error: {e}")

        current_time = time.time()
        if current_time - last_interval >= INTERVAL_SECONDS:
            if predictions:
                labels = [label for label, _ in predictions]
                label_counts = Counter(labels)
                most_common = label_counts.most_common(1)[0][0]
                avg_conf = np.mean([conf for _, conf in predictions])

                print(f"\n🕔 {time.strftime('%H:%M:%S')} - Prediction Summary (Last 5s):")
                print(f"🧠 Final Label: {most_common} | Avg Confidence: {avg_conf:.2f}\n")
            else:
                print(f"\n🕔 {time.strftime('%H:%M:%S')} - No valid predictions in last 5 seconds.")

            last_interval = current_time
            predictions = []

if __name__ == "__main__":
    asyncio.run(stream_predict())
