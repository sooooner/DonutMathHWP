import os
import json
from tqdm import tqdm
from dotenv import load_dotenv

from .hwp import Hwp
from .path import hwp_dir, tmp_dir, dataset_dir, endnote_dataset_dir
from .utils import list_all_files, get_basename, delect_all_files
from .prompt import text_extract_system
from .gpt_api import APIRequestManager
from .html_phaser import HtmlPhaser

def save_endnotes(save_dir, file_name, endnotes):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    row = {
        'file_name': file_name,
        'endnotes': endnotes
    }

    file_path =  os.path.join(save_dir, 'endnotes.jsonl')
    file_mode = 'a' if os.path.exists(file_path) else 'w'
    with open(file_path, file_mode, encoding='utf-8') as file:
        json_string = json.dumps(row, ensure_ascii=False)
        file.write(json_string + '\n')

    
def save_positions(save_dir, file_name, pages_positions):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    row = {
        'file_name': file_name,
        'positions': pages_positions
    }

    file_path =  os.path.join(save_dir, 'positions.jsonl')
    file_mode = 'a' if os.path.exists(file_path) else 'w'
    with open(file_path, file_mode, encoding='utf-8') as file:
        json_string = json.dumps(row, ensure_ascii=False)
        file.write(json_string + '\n')

def main():
    load_dotenv()
    # api_key = os.getenv('API_KEY')
    # metadata_processor = APIRequestManager(api_key=api_key)

    # 139 + 62 + 4 + 35 + 44
    hwp_path_list = list_all_files(hwp_dir)[139 + 62 + 4 + 35 + 44:]
    for hwp_path in tqdm(hwp_path_list):
        basename = get_basename(hwp_path)


        hwp_path = os.path.join(os.getcwd(), hwp_path)


        html_content, uuid_to_eqn = Hwp().extract_html(hwp_path, quit=True, visible=False)
        # pages, pages_positions = HtmlPhaser(html_content).extract_page_info(uuid_to_eqn)
        # save_positions(dataset_dir, basename, pages_positions)
        # metadata_processor.generate_responses(pages, basename, [text_extract_system])

        html_content_endnote, uuid_to_eqn_endnote, css_content = Hwp().extract_endnote_html(hwp_path, visible=False)
        endnotes, endnote_positions = HtmlPhaser(html_content_endnote, css_content).extract_endnote_info(uuid_to_eqn_endnote)
        save_endnotes(endnote_dataset_dir, basename, endnotes)
        save_positions(endnote_dataset_dir, basename, endnote_positions)

        delect_all_files(tmp_dir)


if __name__ == '__main__':
    main()
    # python -m dataset.hwp_processing