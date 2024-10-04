import os
from bs4 import BeautifulSoup
import random
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import re

SPACE_WIDTH = 1.17   # 띄어쓰기
CHAR_WIDTH = 3.457839105  # 글자 하나 (알파벳, 숫자 등)
SYMBOL_WIDTH = 0.85  # 기호

def extract_width_from_style(style):
    """style 속성에서 width 값을 추출하는 함수"""
    if 'width:' in style:
        width_str = style.split('width:')[1].split('mm')[0].strip()
        return float(width_str)
    return None
    
def calculate_width(div):
    total_width = 0.0
    
    # 모든 span과 div 요소들을 순차적으로 처리
    for element in div.find_all(['span', 'div']):
        if element.name == 'span':
            # span 요소에 style 속성이 있는지 확인
            style = element.get('style')
            if style and 'width:' in style:
                # style 속성에서 width 값을 추출하여 사용
                width = extract_width_from_style(style)
                total_width += width
            else:
                # style이 없으면 텍스트 길이를 계산 (cs2의 경우는 폰트 크기 0pt라 무시)
                if 'cs2' not in element['class']:
                    # text_length = len(element.get_text(strip=True))
                    # width = text_length * CHAR_WIDTH
                    # total_width += width
                    text = element.get_text()
                    for char in text:
                        if char.isspace():  # 띄어쓰기
                            total_width += SPACE_WIDTH
                        elif char.isalnum():  # 문자 (알파벳, 숫자 등)
                            total_width += CHAR_WIDTH
                        else:  # 그 외 기호
                            total_width += SYMBOL_WIDTH
        
        elif element.name == 'div':
            # div 요소의 width 스타일 속성 값을 추출하여 더함
            style = element.get('style')
            if style and 'width:' in style:
                width = extract_width_from_style(style)
                total_width += width + SPACE_WIDTH

    return total_width
    
def calculate_height(div):
    _, height = get_page_dimensions(div)
    return height

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


def get_accumulated_coordinates(element, page_width, page_height):
    accumulated_left = 0
    accumulated_top = 0
    current_element = element
    first_div_height = 0

    while current_element:
        style = current_element.get('style', '')
        if style:
            attributes = extract_style_attributes(style, page_width, page_height)
            accumulated_left += attributes['left']
            accumulated_top += attributes['top']
            if first_div_height == 0:
                first_div_height = attributes['height']
        current_element = current_element.find_parent()

    accumulated_top += first_div_height

    if page_width != 0 and page_height != 0:
        accumulated_left_ratio = accumulated_left / page_width
        accumulated_top_ratio = accumulated_top / page_height
        return accumulated_left_ratio, accumulated_top_ratio, first_div_height
    return 0, 0, 0

def find_problem_coordinates_and_height(soup, page_width, page_height):
    problems = []

    pattern = re.compile(r'^\d+\)')

    flag = False
    divs = soup.find_all('div', class_='hls')
    cur_problem = None
    cur_width = 0
    for div in divs:
        span = div.find('span', string=pattern)
        if span:
            if flag:
                cur_height -= 8
                cur_height_ratio =  cur_height / page_height
                cur_width_ratio = cur_width / page_width
                cur_problem['y2'] = cur_problem['y1'] + cur_height_ratio
                cur_problem['x2'] = cur_problem['x1'] + cur_width_ratio
                problems.append(cur_problem)
                cur_width = 0

            accumulated_left_ratio, accumulated_top_ratio, height = get_accumulated_coordinates(div, page_width, page_height)
            
            flag = True
            cur_height = 0
            cur_problem = {
                'x1': accumulated_left_ratio, 
                'y1': accumulated_top_ratio
            }
        
        if flag:
            cur_width = max(cur_width, calculate_width(div))
            cur_height += calculate_height(div) + 1.77

    if cur_problem is not None:
        cur_height -= 4
        cur_height_ratio =  cur_height / page_height
        cur_width_ratio = cur_width / page_width
        cur_problem['y2'] = cur_problem['y1'] + cur_height_ratio
        cur_problem['x2'] = cur_problem['x1'] + cur_width_ratio
        problems.append(cur_problem)
    return problems

def get_endnote_positions(soup):
    positions = []
    for div in soup.body.find_all('div', recursive=False):
        page_width, page_height = get_page_dimensions(div)
        problems = find_problem_coordinates_and_height(div, page_width, page_height)
        positions.append([[problem['x1'], problem['y1'], problem['x2'], problem['y2']] for problem in problems])

    return [position for position in positions if len(position) > 0]


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
