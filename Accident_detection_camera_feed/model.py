import torch
import torch.nn as nn
import torchvision.models as models

class AccidentDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = models.resnet18(pretrained=True)
        self.cnn.fc = nn.Identity()  # Use raw features from last layer
        self.lstm = nn.LSTM(input_size=512, hidden_size=128, batch_first=True)
        self.fc = nn.Linear(128, 1)

    def forward(self, x):  # x: [B, T, C, H, W]
        B, T, C, H, W = x.shape
        x = x.view(B * T, C, H, W)
        features = self.cnn(x)  # [B*T, 512]
        features = features.view(B, T, -1)  # [B, T, 512]
        lstm_out, _ = self.lstm(features)
        final_output = self.fc(lstm_out[:, -1, :])
        return torch.sigmoid(final_output)
