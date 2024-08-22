import os
import re
import json
from tqdm import tqdm
from datasets import load_dataset

from path import json_folder, pages_path, pages_metadata_path, dataset_dir, pdf_file_folder, pdf_folder, problems_metadata_path, problems_path
from utils import get_basename, list_all_files
from pdf_to_image import convert_pdf_pages_to_images, aspect_ratio_preserving_resize_and_crop
from pdf_to_image import read_pdf, extract_areas, save_images

def load_filename_to_postions():
    with open(os.path.join(dataset_dir, 'positions.jsonl'), 'r', encoding='utf-8') as file:
        positions = file.readlines()

    filename_to_postions = {}
    for position in positions:
        cur_postion = json.loads(position)
        filename_to_postions[cur_postion['file_name']] = cur_postion['positions']

    return filename_to_postions

def load_filename_to_uuid_to_eqn():
    with open(os.path.join(dataset_dir, 'uuid_to_eqn.jsonl'), 'r', encoding='utf-8') as file:
        uuid_to_eqns = file.readlines()

    filename_to_uuid_to_eqn = {}
    for uuid_to_eqn in uuid_to_eqns:
        cur_uuid_to_eqn = json.loads(uuid_to_eqn)
        filename_to_uuid_to_eqn[cur_uuid_to_eqn['file_name']] = cur_uuid_to_eqn['uuid_to_eqn']

    return filename_to_uuid_to_eqn

def load_response(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        response = json.loads(file.readline())
    return response['choices'][0]['message']['content']

def get_file_key(file_path):
    basename = get_basename(file_path)
    file_key, idx = basename.split('_page_')
    return file_key, int(idx)

def get_problems(response, uuid_to_eqn):
    if "<div" in response:
        raise

    for uuid_, eqn in uuid_to_eqn.items():
        response = response.replace(uuid_, eqn)
    return json.loads(response)

def replace_quotes(text):
    if not isinstance(text, str):
        text = str(text)

    parts = re.split(r'(\$.*?\$)', text)
    for i, part in enumerate(parts):
        if part.startswith('$') and part.endswith('$'):
            parts[i] = part.replace("'", " prime ")
        else:
            parts[i] = part.replace("'", '"')
    return ''.join(parts)

def save_metadata(metadata_path, problems, idx, p_no=None):
    metadata_dir = os.path.dirname(metadata_path)
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)

    if p_no is None:
        metadata_row = {
            'file_name': f'image_{idx}.png',
            'ground_truth': replace_quotes({'gt_parse': problems})
        }
    elif p_no is not None:
        metadata_row = {
            'file_name': f'image_{idx}_{p_no}.png',
            'ground_truth': replace_quotes({'gt_parse': problems})
        }

    row = json.dumps(metadata_row, ensure_ascii=False)
    file_mode = 'a' if os.path.exists(metadata_path) else 'w'
    with open(metadata_path, file_mode, encoding='utf-8') as file:
        file.write(row.replace(r'\\ue04d', '|').replace(r'\\\\u3000', ' ').replace(r'\\U000f005a', '') + '\n')

def pages_data_creater(filename_to_postions, filename_to_uuid_to_eqn):
    json_file_list = list_all_files(json_folder)
    pdf_file_list = list_all_files(pdf_file_folder)
    pdf_file_name_to_path = {get_basename(path): path for path in pdf_file_list}

    for idx, file_path in tqdm(enumerate(json_file_list), total=len(json_file_list)):
        file_key, page_num = get_file_key(file_path)

        response = load_response(file_path)
        positions = filename_to_postions[file_key]
        uuid_to_eqn = filename_to_uuid_to_eqn[file_key]
        try:
            problems = get_problems(response, uuid_to_eqn)
        except:
            continue

        save_metadata(pages_metadata_path, problems, idx)
        convert_pdf_pages_to_images(pdf_file_name_to_path[file_key], pages_path, idx, page_num)


def problems_data_creater(filename_to_postions, filename_to_uuid_to_eqn):
    target_width = 480
    target_height = 480

    json_file_list = list_all_files(json_folder)
    pdf_file_list = list_all_files(pdf_folder)
    pdf_file_name_to_path = {get_basename(path): path for path in pdf_file_list}

    for idx, file_path in tqdm(enumerate(json_file_list), total=len(json_file_list)):
        file_key, page_num = get_file_key(file_path)

        response = load_response(file_path)
        uuid_to_eqn = filename_to_uuid_to_eqn[file_key]
        try:
            problems = get_problems(response, uuid_to_eqn)
        except:
            continue

        pdf_file_path = pdf_file_name_to_path[file_key]
        pdf_root_path, ext = os.path.splitext(pdf_file_path)
        pdf_file_path_ = pdf_root_path + '_' + ext

        doc = read_pdf(pdf_file_path)
        doc = doc.load_page(page_num)

        doc_ = read_pdf(pdf_file_path_)
        doc_ = doc_.load_page(page_num)

        positions = filename_to_postions[file_key][page_num]
        for p_no, (problem, position) in enumerate(zip(problems['problems'], positions)):
            if position[1] - position[-1] > 0.015:
                continue

            try:
                images = extract_areas(doc, [position])
                images = [aspect_ratio_preserving_resize_and_crop(image, target_width, target_height) for image in images]

                position[1] -= 0.01
                images_ = extract_areas(doc_, [position])
                images_ = [aspect_ratio_preserving_resize_and_crop(image, target_width, target_height) for image in images_]
            except:
                continue

            save_metadata(problems_metadata_path, problem, idx, p_no)
            problem['content'] = re.sub(r'^\d+\.\s*', '', problem['content'])
            save_metadata(problems_metadata_path, problem, idx, f"{p_no}_")
            cur_image_path = os.path.join(problems_path, f'image_{idx}')
            save_images(images, cur_image_path, p_no)
            save_images(images_, cur_image_path, f"{p_no}_")

if __name__ == '__main__':
    filename_to_postions = load_filename_to_postions()
    filename_to_uuid_to_eqn = load_filename_to_uuid_to_eqn()

    # pages_data_creater(filename_to_postions, filename_to_uuid_to_eqn)
    problems_data_creater(filename_to_postions, filename_to_uuid_to_eqn)
