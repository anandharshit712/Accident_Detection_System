import os
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split
from dataset import ImageSequenceDataset
from model import AccidentDetector
from tqdm import tqdm

# Configs
DATA_DIR = "dataset"
BATCH_SIZE = 4
EPOCHS = 10
LEARNING_RATE = 1e-4
SEQUENCE_LENGTH = 16
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():
    print("🔄 Starting training process...")
    start_time = time.time()

    # Transforms for images
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    # Load dataset from image sequences
    print("📁 Loading dataset from image sequences...")
    full_dataset = ImageSequenceDataset(DATA_DIR, sequence_length=SEQUENCE_LENGTH, transform=transform)
    print(f"✅ Total samples found: {len(full_dataset)}")

    # Train/validation split
    print("🔀 Splitting dataset into training and validation sets...")
    train_indices, val_indices = train_test_split(list(range(len(full_dataset))), test_size=0.2, random_state=42)
    train_subset = torch.utils.data.Subset(full_dataset, train_indices)
    val_subset = torch.utils.data.Subset(full_dataset, val_indices)

    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    # Model
    print("🧠 Initializing model...")
    model = AccidentDetector().to(DEVICE)
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Training loop
    for epoch in range(EPOCHS):
        print(f"\n🚀 Starting Epoch {epoch+1}/{EPOCHS}...")
        model.train()
        running_loss = 0.0
        train_progress = tqdm(train_loader, desc=f"🔄 Training Epoch {epoch+1}", leave=False)
        for inputs, labels in train_progress:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            train_progress.set_postfix(loss=loss.item())

        avg_train_loss = running_loss / len(train_loader)
        print(f"\n📚 Epoch {epoch+1}/{EPOCHS} | Train Loss: {avg_train_loss:.4f}")

        # Validation
        print(f"🧪 Running validation for Epoch {epoch+1}...")
        model.eval()
        val_loss = 0.0
        correct = total = 0
        with torch.no_grad():
            for i, (inputs, labels) in enumerate(val_loader):
                print(f"   🔍 Validating batch {i+1}/{len(val_loader)}")
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                preds = (outputs > 0.5).float()
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        avg_val_loss = val_loss / len(val_loader)
        acc = correct / total
        print(f"🧪 Validation Loss: {avg_val_loss:.4f} | Accuracy: {acc:.4f}")

    # Save model
    torch.save(model.state_dict(), "accident_model.pth")
    print("\n✅ Model saved as accident_model.pth")

    total_time = time.time() - start_time
    minutes, seconds = divmod(total_time, 60)
    print(f"\n⏱️ Total training time: {int(minutes)}m {int(seconds)}s")

if __name__ == "__main__":
    main()
