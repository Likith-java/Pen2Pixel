"""
Download EMNIST dataset using torchvision and save as numpy arrays.
Runs automatically via torchvision.datasets.EMNIST (no manual download needed).
"""

import numpy as np
from pathlib import Path
import torchvision
import torchvision.transforms as transforms

SAVE_DIR = Path(__file__).resolve().parent.parent / "dataset" / "emnist"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

transform = transforms.Compose([
    transforms.ToTensor(),
])

print("Downloading EMNIST 'balanced' split (47 classes: digits + letters)...")
train_dataset = torchvision.datasets.EMNIST(
    root=SAVE_DIR / "raw",
    split="balanced",
    train=True,
    download=True,
    transform=transform,
)
test_dataset = torchvision.datasets.EMNIST(
    root=SAVE_DIR / "raw",
    split="balanced",
    train=False,
    download=True,
    transform=transform,
)

X_train = np.array([img.numpy().squeeze() for img, _ in train_dataset])
y_train = np.array([label for _, label in train_dataset])
X_test = np.array([img.numpy().squeeze() for img, _ in test_dataset])
y_test = np.array([label for _, label in test_dataset])

np.savez_compressed(SAVE_DIR / "emnist_train.npz", images=X_train, labels=y_train)
np.savez_compressed(SAVE_DIR / "emnist_test.npz", images=X_test, labels=y_test)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")
print(f"Classes: {len(np.unique(y_train))}")
print(f"Saved to {SAVE_DIR}")