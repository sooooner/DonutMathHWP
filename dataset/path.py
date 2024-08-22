import os

data_dir = "mock_exam_data"
hwp_data_dir = "hwp"
pdf_data_dir = "pdf"
tmp_dir = os.path.join(os.getcwd(), "tmp")
hwp_dir = os.path.join(data_dir, hwp_data_dir)
pdf_file_folder = os.path.join(data_dir, pdf_data_dir)

pdf_dir = "pdf"
json_dir = "json"
pages_dir = "pages"
problems_dir = "problems"
metadata_jsonl = 'metadata.jsonl'
dataset_dir = os.path.join(os.getcwd(), 'dataset')
math_dir = os.path.join(os.getcwd(), 'math')
pages_path = os.path.join(math_dir, pages_dir)
problems_path = os.path.join(math_dir, problems_dir)

pdf_folder = os.path.join(dataset_dir, pdf_dir)
json_folder =  os.path.join(dataset_dir, json_dir)
metadata_path = os.path.join(dataset_dir, metadata_jsonl)
pages_metadata_path = os.path.join(pages_path, metadata_jsonl)
problems_metadata_path = os.path.join(problems_path, metadata_jsonl)
