# Pen2Pixel — Handwriting Prediction Using Machine Learning

A web application that recognizes handwritten characters and words from images using deep learning. Built with a CNN-BiLSTM-CTC architecture.

## Overview

Pen2Pixel converts handwritten text in images into editable digital text. The system uses image preprocessing (grayscale, thresholding, denoising, normalization) followed by deep learning models — a CNN for character/digit classification and a CNN-BiLSTM-CTC for word recognition.

## Project Structure

```
handwriting-recognition/
├── dataset/                 # Raw + processed MNIST/IAM
│   ├── mnist/
│   └── iam/
├── preprocessing/           # Preprocessing, segmentation, augmentation
│   ├── preprocess.py
│   ├── segmentation.py
│   └── augment.py
├── models/                  # Model architectures + saved weights
│   ├── cnn_model.py
│   ├── crnn_ctc_model.py
│   └── saved/
├── backend/                 # FastAPI app + inference
│   ├── app.py
│   └── inference.py
├── frontend/                # Web UI (HTML/CSS/JS)
│   ├── index.html
│   ├── style.css
│   └── script.js
├── api/                     # API route definitions
│   └── routes.py
├── utils/                   # Metrics (CER, WER), helpers
│   └── metrics.py
├── notebooks/               # Experimentation (both)
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Setup

```bash
cd handwriting-recognition
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Download Datasets

- **MNIST**: Automatically downloaded via `torchvision` or `tensorflow.keras.datasets`
- **IAM Handwriting Database**: Requires free registration at [fki.tic.heia-fr.ch/databases/iam-handwriting-database](http://www.fki.tic.heia-fr.ch/databases/iam-handwriting-database). Place files in `dataset/iam/`

### 3. Train Models

```bash
# Train CNN on MNIST
python models/cnn_model.py

# Train CNN-BiLSTM-CTC on IAM
python models/crnn_ctc_model.py
```

## Datasets

| Dataset | Use | Notes |
|---------|-----|-------|
| MNIST | Digit classification | 70k images, clean, fast to train |
| IAM Handwriting DB | Word/line recognition | Requires free registration; writer-independent split |
| EMNIST (optional) | Letter classification | Same format as MNIST, easy drop-in |

## Model Architecture

- **CNN**: Convolutional layers for feature extraction → fully connected layers → character class probabilities
- **CNN-BiLSTM-CTC**: CNN backbone → Bidirectional LSTM sequence modeling → CTC loss for transcription

## License

MIT
