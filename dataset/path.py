import os

data_dir = "mock_exam_data"
hwp_data_dir = "hwp"
pdf_data_dir = "pdf"
dataset_dir = os.path.join(os.getcwd(), 'dataset')
tmp_dir = os.path.join(dataset_dir, "tmp")
hwp_dir = os.path.join(dataset_dir, data_dir, hwp_data_dir)
pdf_file_folder = os.path.join(dataset_dir, data_dir, pdf_data_dir)

pdf_dir = "pdf"
json_dir = "json"
pages_dir = "pages"
problems_dir = "problems"
endnotes_dir = "endnotes"
metadata_jsonl = 'metadata.jsonl'
endnote_dataset_dir = os.path.join(dataset_dir, 'dataset', endnotes_dir)
math_dir = os.path.join(dataset_dir, 'math')
pages_path = os.path.join(math_dir, pages_dir)
problems_path = os.path.join(math_dir, problems_dir)
endnotes_path = os.path.join(math_dir, endnotes_dir)

pdf_folder = os.path.join(dataset_dir, 'dataset', pdf_dir)
json_folder =  os.path.join(dataset_dir, 'dataset', json_dir)
endnote_pdf_folder = os.path.join(endnote_dataset_dir, pdf_dir)
pages_metadata_path = os.path.join(pages_path, metadata_jsonl)
problems_metadata_path = os.path.join(problems_path, metadata_jsonl)
endnotes_metadata_path = os.path.join(endnotes_path, metadata_jsonl)
