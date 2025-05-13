#!/bin/bash

export HUGGINGFACE_HUB_TOKEN=<your_hf_token>
export WANDB_API_KEY=<your_wandb_key>

git clone https://github.com/huggingface/diffusers
cd diffusers
pip install -e .

cd examples/text_to_image
pip install hf_xet
pip install -r requirements_sdxl.txt

huggingface-cli login --token $HUGGINGFACE_HUB_TOKEN
pip install wandb
wandb login $WANDB_API_KEY

accelerate config default

accelerate launch train_text_to_image_lora_sdxl.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --pretrained_vae_model_name_or_path="madebyollin/sdxl-vae-fp16-fix" \
  --dataset_name="mvkhanh/FarfetchText-to-Image" \
  --validation_prompt="A unisex bomber jacket made of premium suede material, in navy blue color, featuring an embroidered golden phoenix design on the back, with ribbed cuffs and hem in black knitted fabric; modern style with a touch of 90s retro, captured under professional studio lighting with a softly blurred background." \
  --num_validation_images=4 \
  --validation_epochs=1 \
  --output_dir="sdxl-farfetch-model" \
  --resolution=1024 \
  --center_crop \
  --random_flip \
  --train_text_encoder \
  --train_batch_size=1 \
  --num_train_epochs=10 \
  --checkpointing_steps=500 \
  --gradient_accumulation_steps=4 \
  --learning_rate=1e-04 \
  --lr_warmup_steps=0 \
  --report_to="wandb" \
  --dataloader_num_workers=8 \
  --allow_tf32 \
  --mixed_precision="fp16" \
  --push_to_hub \
  --hub_model_id="SDXL-LoRA" \
  --resume_from_checkpoint="latest"