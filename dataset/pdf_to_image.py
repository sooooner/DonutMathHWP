import os
import fitz
import random

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def read_pdf(file_path):
    return fitz.open(file_path)

def convert_to_pixel_coordinates(page, coords, endnote=False):
    page_width = page.rect.width
    page_height = page.rect.height
    if endnote:
        return [(
            int((x1 - random.uniform(0.005, 0.01)) * page_width),
            int((y1 + 0.0015) * page_height),
            int((x2 + random.uniform(0.01, 0.015)) * page_width),
            int((y2 + random.uniform(0.005, 0.01)) * page_height)
        ) for x1, y1, x2, y2 in coords]
    else:
        return [(
            int((x1 - random.uniform(0.005, 0.01)) * page_width),
            int((y1 - random.uniform(0.005, 0.015)) * page_height),
            int((x2 + random.uniform(0.005, 0.01)) * page_width),
            int((y2 + random.uniform(0.005, 0.015)) * page_height)
        ) for x1, y1, x2, y2 in coords]

def extract_areas(page, coordinates, endnote=False):
    extracted_images = []
    pixel_coords = convert_to_pixel_coordinates(page, coordinates, endnote=endnote)
    for rect in pixel_coords:
        x1, y1, x2, y2 = rect
        clip = fitz.Rect(x1, y1, x2, y2)
        matrix = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=matrix, clip=clip)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        extracted_images.append(img)
    return extracted_images

def save_images(images, base_file_path, idx, ignore_p_no=None):
    if len(images) == 1:
        if not ignore_p_no:
            images[0].save(f"{base_file_path}_{idx}.png")
    elif len(images) > 1:
        for i, img in enumerate(images):
            if i in ignore_p_no:
                continue
            img.save(f"{base_file_path}_{i}.png")
    else: 
        pass


def aspect_ratio_preserving_resize_and_crop(image, target_width, target_height):
    # 현재 이미지의 크기
    width, height = image.size

    # 가로와 세로 중 더 많이 차이나는 쪽을 기준으로 비율 유지하면서 조정
    width_ratio = width / target_width
    height_ratio = height / target_height

    if width > target_width and height > target_height:
        if width_ratio > height_ratio:
            new_width = target_width
            new_height = int(new_width / (width / height))
        else:
            new_height = target_height
            new_width = int(new_height * (width / height))
    elif width > target_width:
        new_width = target_width
        new_height = int(new_width / (width / height))
    elif height > target_height:
        new_height = target_height
        new_width = int(new_height * (width / height))
    else:
        new_width, new_height = width, height

    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # 패딩 추가
    padded_image = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # 중앙 패딩 계산
    offset_x = (target_width - new_width) // 2
    offset_y = (target_height - new_height) // 2

    padded_image.paste(resized_image, (offset_x, offset_y))

    return padded_image

def convert_pdf_pages_to_images_(input_pdf, output_folder, page_cnt=None, target_height=1754, target_width=1240, dpi=300):
    # PDF 문서 열기
    doc = fitz.open(input_pdf)
    if page_cnt is not None:
        num_pages = page_cnt
    else:
        num_pages = len(doc)
    
    # 각 페이지를 이미지로 변환
    for page_cnt in range(num_pages):
        page = doc[page_cnt]
        original_width, original_height = page.rect.width, page.rect.height
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = min(scale_x, scale_y)
        
        # DPI 설정
        new_dpi = dpi * scale
        
        # 페이지를 Pixmap으로 변환
        pix = page.get_pixmap(matrix=fitz.Matrix(new_dpi / 72, new_dpi / 72))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 이미지 크기 조정 (비율 유지)
        img.thumbnail((target_width, target_height), Image.LANCZOS)
        
        # 파일 이름 생성 및 저장
        file_name = os.path.basename(input_pdf)
        file_name, _ = os.path.splitext(file_name)
        output_path = os.path.join(output_folder, f"{file_name.replace(' ', '_')}_page_{page_cnt}.png")
        
        img.save(output_path)
    
    doc.close()
    return page_cnt + 1

def convert_pdf_pages_to_images(input_pdf, output_folder, idx, page_num, target_height=1754, target_width=1240, dpi=300):
    # PDF 문서 열기
    doc = fitz.open(input_pdf)
    page = doc[int(page_num)]

    original_width, original_height = page.rect.width, page.rect.height
    scale_x = target_width / original_width
    scale_y = target_height / original_height
    scale = min(scale_x, scale_y)
    
    # DPI 설정
    new_dpi = dpi * scale
    
    # 페이지를 Pixmap으로 변환
    pix = page.get_pixmap(matrix=fitz.Matrix(new_dpi / 72, new_dpi / 72))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # 이미지 크기 조정 (비율 유지)
    img.thumbnail((target_width, target_height), Image.LANCZOS)
    
    # 파일 이름 생성 및 저장
    file_name = os.path.basename(input_pdf)
    file_name, _ = os.path.splitext(file_name)
    output_path = os.path.join(output_folder, f"image_{idx}.png")
    
    img.save(output_path)
    
    doc.close()