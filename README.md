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
handwriting-recognition/
├── dataset/                  # Raw and processed datasets
│   ├── mnist/                # MNIST digits
│   ├── emnist/               # EMNIST characters
│   ├── iam/                  # IAM Handwriting Database
│   └── download_emnist.py    # EMNIST download script
│
├── preprocessing/            # Image preprocessing
│   ├── preprocess.py
│   ├── segmentation.py
│   └── augment.py
│
├── models/                   # Deep Learning models
│   ├── cnn_model.py
│   ├── crnn_ctc_model.py
│   └── saved/                # Trained model weights
│
├── backend/                  # FastAPI backend
│   ├── app.py
│   └── inference.py
│
├── frontend/                 # Web UI
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── api/                      # Python inference API routes
│   └── routes.py
│
├── utils/                    # Metrics and helpers
│   └── metrics.py
│
├── notebooks/                # Experimentation notebooks
│
├── uploads/                  # Uploaded images
│
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
git clone https://github.com/Likith-java/Pen2Pixel.git
cd Pen2Pixel/handwriting-recognition
```

---

## Install Frontend

```bash
cd frontend
# Open index.html in browser or serve with live-server
```

---

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# Download Datasets

### MNIST

Automatically downloaded using

```python
torchvision.datasets
```

or

```python
tensorflow.keras.datasets
```

---

### IAM Handwriting Database

Register for free and download the dataset.

Store it inside

```text
handwriting-recognition/dataset/iam/
```

---

### EMNIST

```bash
python dataset/download_emnist.py
```

---

### Optional

* EMNIST
* CVL Handwriting Database

---

# Train Models

Make sure you're in the `handwriting-recognition/` directory and the virtual environment is activated:

```bash
cd handwriting-recognition
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux
```

### CNN

```bash
python models/cnn_model.py
```

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
