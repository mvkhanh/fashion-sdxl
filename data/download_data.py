# Download image, create caption, and refine caption using BLIP 2
import pandas as pd
import os
import torch
import requests
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration

USING_BLIP = False
data = pd.read_csv('clean_data.csv' if USING_BLIP else 'clean_data_no_blip.csv')
IMAGE_FOLDER = 'data'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

if USING_BLIP:
    processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
    model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-flan-t5-xl", torch_dtype=torch.float16, device_map="mps")
    question = "Generate a complete product description for this fashion image using the details: {raw_caption}. Include description of model if visible, the angle of the shot, and other visual aspects."
    device = 'mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu'

import csv

METADATA_PATH = os.path.join(IMAGE_FOLDER, 'metadata.csv')
if not os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['file_name', 'text'])

def save_data(image: Image, image_name: str, refine_caption: str):
    image.save(os.path.join(IMAGE_FOLDER, image_name))
    with open(os.path.join(IMAGE_FOLDER, 'metadata.csv'), 'a') as f:
        f.write(f'{image_name},{refine_caption}\n')
        
for row in data.values:
    image_url, image_name, raw_caption = row
    image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
    print(f'Get {image_url} successfully!')
    if USING_BLIP:
        inputs = processor(image, question.format(raw_caption=raw_caption), return_tensors="pt").to("mps", torch.float16)

        out = model.generate(**inputs)
        refine_caption = processor.decode(out[0], skip_special_tokens=True)
    else:
        refine_caption = raw_caption
    save_data(image, image_name, refine_caption)
    print(f'Save {image_url} successfully!')
    