# Pen2Pixel — Handwriting Prediction Using Machine Learning

A web application that recognizes handwritten characters, words, and handwritten documents from images using deep learning. Built with a **CNN-BiLSTM-CTC architecture**, featuring a **React frontend** and a **Node.js + Express backend**.

---

## Overview

**Pen2Pixel** converts handwritten text in images into editable digital text. Users can upload an image of handwritten notes, and the application processes it through an image preprocessing pipeline (grayscale conversion, thresholding, denoising, normalization, and segmentation) before passing it to a deep learning model for text recognition.

The project uses:

* **CNN** for feature extraction
* **BiLSTM** for sequence modeling
* **CTC Loss** for handwritten text transcription
* **React** for the frontend
* **Node.js + Express** for the backend API
* **Python (TensorFlow/PyTorch)** for machine learning and inference

---

# Project Structure

```text
pen2pixel/
├── api/                      # Python inference API
│   └── routes.py
├── backend/                  # Python backend (FastAPI)
│   ├── app.py
│   └── inference.py
├── dataset/                  # Raw and processed datasets
│   ├── download_emnist.py
│   ├── mnist/
│   └── iam/
├── models/                   # Deep Learning models
│   ├── cnn_model.py
│   ├── crnn_ctc_model.py
│   └── saved/
├── preprocessing/            # Image preprocessing
│   ├── preprocess.py
│   └── augment.py
├── utils/                    # Shared utilities
│   └── metrics.py
├── frontend/                 # Web UI (HTML/CSS/JS)
│   ├── index.html
│   ├── style.css
│   └── script.js
├── notebooks/                # Experimentation
├── uploads/                  # Uploaded images
├── requirements.txt
└── README.md
```

---

# Tech Stack

### Frontend

* React
* JavaScript
* Axios
* CSS / Tailwind CSS (optional)

### Backend

* Node.js
* Express.js
* Multer (image uploads)

### Machine Learning

* Python
* TensorFlow / PyTorch
* OpenCV
* NumPy
* Pandas

---

# Quick Start

## Clone Repository

```bash
git clone [https://github.com/Likith-java/Pen2Pixel.git]]
cd pen2pixel
```

---

## Install Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Install Backend

```bash
cd backend
npm install
npm start
```

---

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# Download Datasets

### MNIST

Download from [Kaggle MNIST Dataset](https://www.kaggle.com/datasets/hojjatk/mnist-dataset) and place the IDX files inside:

```text
dataset/mnist/
```

Expected files: `train-images-idx3-ubyte`, `train-labels-idx1-ubyte`, `t10k-images-idx3-ubyte`, `t10k-labels-idx1-ubyte`

---

### EMNIST

Automatically downloaded using the provided script:

```bash
python dataset/download_emnist.py
```

Downloads via `torchvision.datasets.EMNIST` and saves numpy arrays to `dataset/emnist/`

---

### IAM Handwriting Database (optional)

Register for free and download. Store it inside:

```text
dataset/iam/
```

---

# Train Models

### CNN

```bash
python models/cnn_model.py
```

---

### CNN-BiLSTM-CTC

```bash
python models/crnn_ctc_model.py
```

---

# Datasets

| Dataset                  | Purpose                 | Description                    |
| ------------------------ | ----------------------- | ------------------------------ |
| MNIST                    | Digit Recognition       | 70,000 handwritten digits      |
| EMNIST                   | Character Recognition   | Handwritten letters and digits |
| IAM Handwriting Database | Word & Line Recognition | Real handwritten English text  |
| CVL (Optional)           | Generalization Testing  | Multiple handwriting styles    |

---

# Model Architecture

## CNN

* Image Input
* Convolution Layers
* ReLU
* Max Pooling
* Fully Connected Layers
* Softmax Output

---

## CNN-BiLSTM-CTC

* Image Input
* CNN Feature Extractor
* Feature Map Sequence
* Bidirectional LSTM
* Dense Layer
* CTC Loss
* Predicted Text

---

# Features

* Upload handwritten images
* Image preprocessing
* Automatic handwritten text recognition
* Real-time prediction
* Editable text output
* Copy recognized text
* Download extracted text
* Responsive React interface

---

# Future Enhancements

* Multi-language handwriting recognition
* PDF support
* Paragraph-level recognition
* Mobile application
* Cloud deployment
* Fine-tuning using custom datasets

---

# License

MIT License
