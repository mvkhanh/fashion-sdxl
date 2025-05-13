import streamlit as st
from diffusers import StableDiffusionXLControlNetXSPipeline, ControlNetXSAdapter, AutoencoderKL, StableDiffusionXLPipeline
from diffusers.utils import load_image
import torch
from utils import make_canny
from PIL import Image

@st.cache_resource
def get_model_with_control():
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    controlnet = ControlNetXSAdapter.from_pretrained(
        "UmerHA/Testing-ConrolNetXS-SDXL-canny", torch_dtype=torch.float16
    )
    pipe = StableDiffusionXLControlNetXSPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", controlnet=controlnet, vae=vae, torch_dtype=torch.float16
    )
    device = 'mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu'
    pipe.to(device)
    if device == 'cuda':
        pipe.enable_model_cpu_offload()
        pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
    return pipe

@st.cache_resource
def get_model():
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", vae=vae, torch_dtype=torch.float16
    )
    device = 'mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu'
    pipe.to(device)
    if device == 'cuda':
        pipe.enable_model_cpu_offload()
        pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
    return pipe
    
def update_bar(self, step: int, timestep: int, callback_kwargs: dict):
    # Tính phần trăm tiến độ
    global curr_img
    progress = (step + 1) / steps
    progress_bar.progress(progress, text=f"🔄 In progress {progress * 100:.0f}%")
    return {}

images = None
controlnet_conditioning_scale = 0.5

st.title('Text-to-Image Application')
tab1, tab2 = st.tabs(['SDXL', 'SDXL+ControlNetXS'])

with tab1:
    with st.form(key='main_form1'):
        prompt = st.text_input('Prompt:', placeholder="Describe anything you want, user short sentences, separated by commas.")
        with st.expander('Add negative prompt'):
            neg_prompt = st.text_input('Negative prompt:', placeholder="Type what you don't want to see in the image.")
        steps = st.slider(label='Number of steps:', min_value=1, max_value=50, value=20, help='More steps typically improve image quality but also increase processing time.')
        col1, col2 = st.columns(2)
        size = col1.selectbox(label='Width x Height (px):', options=[1024, 768, 512])
        image_nums = col2.radio(label='Number of images:', options=[1, 2, 3], horizontal=True)
        guidance = st.slider(label='Guidance scale:', min_value=1.0, max_value=20.0, step=0.1, value=7.5, help='Higher guidance scale encourages to generate images that are closely linked to the text prompt, usually at the expense of lower image quality.')
        submitted = st.form_submit_button('Generate', type='primary')
        
        if submitted:
            if not prompt:
                st.error('Prompt is missing!')
            else:
                progress_bar = st.progress(0, text="🔄 Initilize...")
                pipe = get_model()
                images = pipe(prompt, negative_prompt=neg_prompt, num_inference_steps=steps,
                    width=size, height=size, num_images_per_prompt=image_nums, guidance_scale=guidance, callback_on_step_end=update_bar, controlnet_conditioning_scale=controlnet_conditioning_scale).images
                for i, img in enumerate(images):
                    img.save(f'tmp{i+1}.png')
                
with tab2:
    with st.form(key='main_form2'):
        prompt = st.text_input('Prompt:', placeholder="Describe anything you want, user short sentences, separated by commas.")
        with st.expander('Add negative prompt'):
            neg_prompt = st.text_input('Negative prompt:', placeholder="Type what you don't want to see in the image.")
        steps = st.slider(label='Number of steps:', min_value=1, max_value=50, value=20, help='More steps typically improve image quality but also increase processing time.')
        col1, col2 = st.columns(2)
        size = col1.selectbox(label='Width x Height (px):', options=[1024, 768, 512])
        image_nums = col2.radio(label='Number of images:', options=[1, 2, 3], horizontal=True)
        guidance = st.slider(label='Guidance scale:', min_value=1.0, max_value=20.0, step=0.1, value=7.5, help='Higher guidance scale encourages to generate images that are closely linked to the text prompt, usually at the expense of lower image quality.')
        file = st.file_uploader('Control image:', type=['jpg', 'jpeg', 'png'], help='An input guidance image for the model, such as a sketch, Canny edge map, or depth map.')
        submitted = st.form_submit_button('Generate', type='primary')
        
        if submitted:
            if not prompt:
                st.error('Prompt is missing!')
            elif not file:
                st.error('Control image is missing!')
            else:
                progress_bar = st.progress(0, text="🔄 Initilize...")
                pipe = get_model_with_control()
                control_image = make_canny(load_image(Image.open(file)))
                images = pipe(prompt, negative_prompt=neg_prompt, num_inference_steps=steps,
                    width=size, height=size, num_images_per_prompt=image_nums, guidance_scale=guidance, callback_on_step_end=update_bar, controlnet_conditioning_scale=controlnet_conditioning_scale, image=control_image).images
                for i, img in enumerate(images):
                    img.save(f'tmp{i+1}.png')
            
if images:
    curr_img = 0
    progress_bar.empty()
    st.success("✅ Success!")
    st.divider()
    captions = [f'Image {i + 1}' for i in range(len(images))]
    st.image(images, caption=captions)
