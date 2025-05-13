import cv2
import numpy as np
from PIL import Image

def resize_with_padding(image, target_size=1024):
    h, w = image.shape[:2]
    scale = target_size / max(h, w)
    new_h, new_w = int(h * scale), int(w * scale)
    image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    top_pad = left_pad = right_pad = bot_pad = 0
    if new_h > new_w:
        total_pad = target_size - new_w
        left_pad = total_pad // 2
        right_pad = total_pad - left_pad
    else:
        total_pad = target_size - new_h
        top_pad = total_pad // 2
        bot_pad = total_pad - top_pad
    result = cv2.copyMakeBorder(image, top=top_pad, bottom=bot_pad, left=left_pad, right=right_pad, borderType=cv2.BORDER_CONSTANT, value=0)
    return Image.fromarray(result)

def make_canny(image):
    image = np.array(image)
    image = cv2.Canny(image, 100, 200)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    return resize_with_padding(image)