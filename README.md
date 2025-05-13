# 🧥 Fine-tune SDXL for Fashion Image Generation

This project focuses on fine-tuning **Stable Diffusion XL (SDXL)** on **fashion-related datasets** using **LoRA** with Hugging Face's `diffusers` library, and deploying a simple **Streamlit app** to demonstrate the results.

---

## 📌 Project Overview

### 🔍 1. Data Collection
- Scraped fashion images and raw captions from various online sources.
- Cleaned and organized the dataset for training.

### 🛠️ 2. Preprocessing
- Resized and formatted images.
- Refined and standardized text prompts.
- Prepared dataset in Hugging Face format (`datasets.Dataset` or similar).

### 🧠 3. Fine-tuning SDXL with LoRA
- Used Hugging Face `diffusers` with **LoRA (Low-Rank Adaptation)** to fine-tune the model.
- Only trained a small number of parameters for faster and more efficient learning.

### 🌐 4. Streamlit App Demo
- A user interface to input text prompts and generate fashion images.
- Demonstrates the capabilities of the fine-tuned SDXL model.

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/your-username/fashion-sdxl.git
cd fashion-sdxl
```
### 2. Create environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```
### 3. Launch the demo
```bash
streamlit run src/app.py
```