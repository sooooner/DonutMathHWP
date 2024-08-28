import os
import torch
import argparse
import gradio as gr

from dataset.utils import list_all_files
from tutorial_utils import Image2Text


def demo_process(input_img):
    global image_to_text
    contents, _, _ = image_to_text.get_text(input_img, num_beams=4)
    return '\n'.join(contents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretrained_path", type=str, default="models/donut_nougat_aug")
    args, _ = parser.parse_known_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    image_to_text = Image2Text(args.pretrained_path, device)
    
    demo = gr.Interface(
        fn=demo_process,
        inputs="image",
        outputs="text",
        title=f"Donut 🍩",
        examples=list_all_files('sample'),
    )
    demo.launch()