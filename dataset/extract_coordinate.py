import os
from bs4 import BeautifulSoup
import random
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import re

def extract_style_attributes(style, page_width=0, page_height=0):
    attributes = {
        'left': 0,
        'top': 0,
        'width': 0,
        'height': 0
    }
    for attr in style.split(';'):
        if 'left' in attr:
            attributes['left'] = float(attr.split(':')[1].strip().replace('mm', ''))
        elif 'top' in attr:
            attributes['top'] = float(attr.split(':')[1].strip().replace('mm', ''))
        elif 'width' in attr:
            value = attr.split(':')[1].strip()
            if value.endswith('%'):
                attributes['width'] = float(value.replace('%', '')) * page_width / 100
            else:
                attributes['width'] = float(value.replace('mm', ''))
        elif 'height' in attr:
            value = attr.split(':')[1].strip()
            if value.endswith('%'):
                attributes['height'] = float(value.replace('%', '')) * page_height / 100
            else:
                attributes['height'] = float(value.replace('mm', ''))
    return attributes

def get_page_dimensions(page):
    style = page.get('style', '')
    width = height = 0
    for attr in style.split(';'):
        if 'width' in attr:
            width = float(attr.split(':')[1].strip().replace('mm', ''))
        elif 'height' in attr:
            height = float(attr.split(':')[1].strip().replace('mm', ''))
    return width, height

def find_bottom_offset(start_element, stop_classes, n=3):
    consecutive_class_counts = {cls: 0 for cls in stop_classes}
    sibling = start_element.find_next_sibling()
    first_stop_class_element = None

    while sibling:
        sibling_classes = ' '.join(sibling.get('class', []))
        if sibling_classes in stop_classes:
            if consecutive_class_counts[sibling_classes] == 0:
                first_stop_class_element = sibling
            consecutive_class_counts[sibling_classes] += 1

            if consecutive_class_counts[sibling_classes] >= n:
                sibling_style = first_stop_class_element.get('style', '')
                sibling_attributes = extract_style_attributes(sibling_style)
                return sibling_attributes['top']
        else:
            first_stop_class_element = None
            consecutive_class_counts = {cls: 0 for cls in stop_classes}

        sibling = sibling.find_next_sibling()

    return 0


def calculate_position_and_dimensions(page, problem, stop_classes=['hls ps4'], n=3):
    current_element = problem
    total_left = total_top = 0
    max_right = 0 
    
    page_width, page_height = get_page_dimensions(page)

    while current_element and current_element.name != 'body':
        style = current_element.get('style', '')
        attributes = extract_style_attributes(style, page_width, page_height)
        total_left += attributes['left']
        total_top += attributes['top']
        current_element = current_element.find_parent()

    parent_element = problem.find_parent()
    parent_style = parent_element.get('style', '')
    parent_attributes = extract_style_attributes(parent_style, page_width, page_height)
    parent_width = parent_attributes['width']
    max_right = total_left + parent_width  

    sibling = parent_element.find_next_sibling()
    while sibling: 
        sibling_style = sibling.get('style', '')
        sibling_attributes = extract_style_attributes(sibling_style, page_width, page_height)
        sibling_left = sibling_attributes.get('left', 0)
        sibling_width = sibling_attributes.get('width', 0)
        sibling_right = total_left + sibling_left + sibling_width 
        if sibling_right > max_right: 
            max_right = sibling_right
        sibling = sibling.find_next_sibling() 

    left_ratio = total_left / page_width if page_width else 0
    top_ratio = total_top / page_height if page_height else 0
    right_ratio = max_right / page_width if page_width else 0  

    bottom_offset = find_bottom_offset(parent_element, stop_classes, n)
    bottom_ratio = (60 + bottom_offset) / page_height if page_height else 0

    return left_ratio, top_ratio, right_ratio, bottom_ratio

def extract_positions(soup, stop_classes):
    pages = soup.select('body > div')

    pages_positions = []

    for page in pages:
        problems = page.select('div.hhe')
        problem_positions = []
        for problem in problems:
            left_ratio, top_ratio, right_ratio, bottom_ratio = calculate_position_and_dimensions(page, problem, stop_classes)

            problem_positions.append((left_ratio, top_ratio, right_ratio, bottom_ratio))
        pages_positions.append(problem_positions)
    pages_positions = [position for position in pages_positions if len(position) > 0]
    return pages_positions


def draw_rectangle_and_display(image_path, coordinates):
    image = Image.open(image_path)
    
    draw = ImageDraw.Draw(image)
    
    width, height = image.size
    
    for coordinate in coordinates:
        random_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        x1_ratio, y1_ratio, x2_ratio, y2_ratio = coordinate
        x1_pixel = int(width * x1_ratio)
        y1_pixel = int(height * y1_ratio)
        x2_pixel = int(width * x2_ratio)
        y2_pixel = int(height * y2_ratio)
        
        draw.rectangle([x1_pixel, y1_pixel, x2_pixel, y2_pixel], outline=random_color, width=2)
    
    plt.figure(figsize=(20, 14))
    plt.imshow(image)
    plt.axis('off')
    
    plt.show()
