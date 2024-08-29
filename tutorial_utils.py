import re
import torch
import numpy as np
from PIL import Image
from dataset.hwp import create_uuid_key
from optimum.onnxruntime import ORTModelForVision2Seq
from dataset.pdf_to_image import aspect_ratio_preserving_resize_and_crop
from transformers import DonutProcessor, VisionEncoderDecoderModel, VisionEncoderDecoderConfig

from EquationStyler import add_backtick


def check_only_eqn(s):
    pattern = r'EQN_[a-z0-9]{4}'
    return re.fullmatch(pattern, s) is not None

def split_by_eqn(part):
    pattern = r'(EQN_[a-z0-9]{4})'
    return re.split(pattern, part)

def replace_latex_with_uuid(text, uuid_dict):
    pattern = r'\$(.*?)\$'
    matches = re.findall(pattern, text)
    
    for match in matches:
        unique_id = create_uuid_key(uuid_dict)  
        uuid_dict[unique_id] = add_backtick(match)
        text = text.replace(f'${match}$', f'EQN_{unique_id}')
    
    return text, uuid_dict

def check_special_choices(s):
    chars_to_check = ["①", "②", "③", "④", "⑤"]
    found_chars = [char for char in chars_to_check if re.search(re.escape(char), s)]
    if found_chars:
        return found_chars
    else:
        return None

def extract_substring(text, pattern1, pattern2=None):
    start_index = text.find(pattern1)

    if start_index == -1:
        return None, text

    if not pattern2 or pattern2 not in text:
        extracted_text = text[start_index + len(pattern1):]
        remaining_text = text[:start_index]
        return extracted_text, remaining_text
    
    match = re.search(f'{re.escape(pattern1)}(.*?){re.escape(pattern2)}', text)
    
    if match:
        extracted_text = match.group(1)
        remaining_text = text[:start_index] + text[start_index + len(pattern1) + len(extracted_text) + len(pattern2) -1:]
        return extracted_text, remaining_text
    else:
        return None, text

def make_hwp_text(hwp, contents):
    choices = ["①", "②", "③", "④", "⑤", None]
    new_contents = []
    multiple_choice = {}
    for content in contents:   
        found_choices = check_special_choices(content)

        if found_choices is not None:
            for found_choice in found_choices:
                extracted_text, remaining_text = extract_substring(content, found_choice, pattern2=choices[choices.index(found_choice)+1])
                multiple_choice[found_choice] = extracted_text
                content = remaining_text.strip()

        if len(content)> 0:
            new_contents.append(content)

    uuid_dict = {}
    for content in new_contents:   
        content, uuid_dict = replace_latex_with_uuid(content, uuid_dict)
        if check_only_eqn(content):
            hwp.insert_text('    ')
            
        parts = split_by_eqn(content)
        for part in parts:
            if part.startswith("EQN_"):
                uuid_part = part[4:8]
                hwp.insert_equation(uuid_dict[uuid_part])
            else:
                hwp.insert_text(part)
        hwp.hwp.HAction.Run("BreakLine")

    uuid_dict = {}
    for idx, (choice, value) in enumerate(multiple_choice.items()):   
        hwp.insert_text(choice)
        hwp.hwp.HAction.Run("RightShiftBlock")
        hwp.hwp.HAction.Run("MoveLeft")
        content, uuid_dict = replace_latex_with_uuid(value, uuid_dict)
        parts = split_by_eqn(content)
        for part in parts:
            if part.startswith("EQN_"):
                uuid_part = part[4:8]
                hwp.insert_equation(uuid_dict[uuid_part])
            else:
                hwp.insert_text(part)
        hwp.hwp.HAction.Run("MoveRight")

    for _ in range(6):
        hwp.hwp.HAction.Run("BreakPara")


class Image2Text:
    def __init__(self, model_path, device):
        self.device = device
        self.model_path = model_path
        self.model, self.processor = self.load_model(self.model_path)
        self.decoder_input_ids = torch.tensor([[self.model.config.decoder_start_token_id]]).to(self.device)

    def load_model(self, model_path):        
        config = VisionEncoderDecoderConfig.from_pretrained(model_path)
        processor = DonutProcessor.from_pretrained(model_path)

        if ('onnx' in model_path) or ('quantized'in model_path):
            model = ORTModelForVision2Seq.from_pretrained(model_path, use_cache=True, config=config).to(self.device)
        else:
            model = VisionEncoderDecoderModel.from_pretrained(model_path, config=config).to(self.device)
            model.eval()
        return model, processor

    def load_img(self, img_path, width=480, height=480):
        if type(img_path) == np.ndarray:
            image = Image.fromarray(img_path)
        else:
            image = Image.open(img_path)
        image = aspect_ratio_preserving_resize_and_crop(image, target_width=width, target_height=height)
        img = self.processor(image.convert("RGB"), return_tensors="pt", size=(width, height)).pixel_values
        pixel_values = img.to(self.device)
        return image, pixel_values

    def generate(self, pixel_values, num_beams):
        outputs = self.model.generate(
                pixel_values,
                decoder_input_ids=self.decoder_input_ids,
                max_length=2048,
                early_stopping=True,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=num_beams,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )
        return outputs

    def correct_latex_expressions(self, text):
        corrected_text = re.sub(r'\$(.*?)\$?\s*([가-힣])', r'$\1$\2', text)
        return corrected_text

    def correct_math_expressions(self, lines):
        corrected_lines = []

        for line in lines:
            line = line.replace('ᄀ', 'ㄱ')
            line = line.replace('ᄂ', 'ㄴ')
            line = line.replace('ᄃ', 'ㄷ')
            line = line.replace('ᄅ', 'ㄹ')
            
            # line = re.sub(r'^\$(\s*)([가-힣])', r'\2', line) 
            # line = re.sub(r'([가-힣])(\s*)\$$', r'\1', line)  

            # line = self.correct_latex_expressions(line)

            # line = re.sub(r'\$\s*\$', '$', line)
        
            # line = re.sub(r'\$(.*?)\$', lambda m: f"${m.group(1).strip()}$", line)

            # line = re.sub(r'\s+', ' ', line).strip()

            # line = re.sub(r'([가-힣])(\s*)\$(\s*)([가-힣])', r'\1\2\3\4', line)
            # corrected_lines.append(line)
        return corrected_lines

    def postprocessing(self, outputs):
        seq = self.processor.batch_decode(outputs.sequences)[0]
        seq = seq.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token, "")
        seq = re.sub(r"<.*?>", "", seq, count=1).strip()  
        seq = self.processor.token2json(seq)
        contents = seq['content'].split('[newline]')
        # contents = self.correct_math_expressions(contents)
        return seq, contents

    def get_text(self, img_path, num_beams=16):
        image, pixel_values = self.load_img(img_path)
        outputs = self.generate(pixel_values, num_beams)
        seq, content = self.postprocessing(outputs)
        return content, image, seq
