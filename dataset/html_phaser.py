import re
import html
from bs4 import BeautifulSoup
from bs4.element import Tag
from .extract_coordinate import extract_positions, get_endnote_positions

attributes_to_remove = ['style', 'src', 'alt', 'border', 'data-formula-baseunit', 
                        'data-formula-color', 'data-formula-linemode', 'height', 
                        'hspace', 'vspace', 'width', 'viewbox', 'd',
                        'id', 'fill', 'x', 'y', 'patternunits', 'xlink', 'preserveaspectratio', 'patterncontentunits']

def split_problems(data):
    problems = []
    current_problem = []
    
    for line in data:
        if re.match(r'^\d+\)', line):
            if current_problem:
                problems.append(current_problem)
            current_problem = [line]  
        else:
            if current_problem:
                current_problem.append(line)
                
    if current_problem:
        problems.append(current_problem)
    
    return problems

class HtmlPhaser():
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def find_consecutive_classes(self, div_classes, threshold=4):
        if not div_classes:
            return []

        consecutive_classes = []
        current_class = div_classes[0]
        count = 1
        
        for i in range(1, len(div_classes)):
            if div_classes[i] == current_class:
                count += 1
            else:
                if count >= threshold:
                    consecutive_classes.append((current_class, count))
                current_class = div_classes[i]
                count = 1
        
        if count >= threshold:
            consecutive_classes.append((current_class, count))
        
        return consecutive_classes
    
    @classmethod
    def get_classes(cls, repeated_classes):
        line_break_classes = [item[0] for item in repeated_classes if item[0] is not None]
        line_break_classes_list = [list(item) for item in set(tuple(row) for row in line_break_classes)]
        stop_classes = [' '.join(p) for p in line_break_classes_list]
        return stop_classes, line_break_classes_list

    def remove_line_break(self, line_break_classes_list):
        for classes in line_break_classes_list:
            cnt = 0
            for tag in self.soup.body.find_all('div', class_=classes):
                if not tag.find_all():
                    cnt += 1
                    if cnt >= 4:
                        tag.extract()
                else:
                    cnt = 0

    def remove_attributes(self, attributes_to_remove):
        for tag in self.soup.find_all(True): 
            for attribute in attributes_to_remove:
                if attribute == 'style' and 'style' in tag.attrs:
                    style_value = tag.attrs['style']
                    if 'url' in style_value:
                        new_style = ''.join([style_part + ';' for style_part in style_value.split(';') if 'background-image' in style_part])
                        tag.attrs['style'] = new_style
                    else:
                        del tag.attrs['style']
                elif attribute in tag.attrs:
                    del tag.attrs[attribute]

    def replace_uids_with_math_tags(self, uuid_to_eqn):
        for elem in self.soup.body.find_all(string=True):
            new_text = elem
            for uid in uuid_to_eqn:
                new_text = new_text.replace(uid, f"${uid}$")
            elem.replace_with(new_text)

    def clean_html_tags(self):
        divs = self.soup.body.find_all('div', recursive=False)
        for div in divs:
            for tag in div.find_all(['div', 'span', 'p']):
                if tag.name == 'span':
                    tag.unwrap()
                elif tag.name == 'p':
                    tag.attrs = {}
                elif tag.name == 'div' and tag.get('class') == ['heq']:
                    tag.extract()
        return divs

    def process_div_elements(self, line_break_classes_list):
        divs = self.clean_html_tags()
        divs = divs[:sum([len(div.find_all('div', class_='hhe')) > 0 for div in divs])]
        pattern_ = "|".join([f'(<div class="{" ".join(class_pair)}"></div>){{{3}}}' for class_pair in line_break_classes_list])
        pattern = rf'(<div class="hhe">.*?)(?={pattern_})'
        divs = [[x[0] if isinstance(x, tuple) else x for x in sublist] for sublist in [re.findall(pattern, str(div), re.DOTALL) for div in divs]]
        return divs

    def replace_image_tag(self, divs):
        pages = []
        for div in divs:
            problems = []
            for problem in div:
                soup = BeautifulSoup(problem, 'html.parser')
                for tag in soup.find_all(['div', 'path']):
                    if not self.should_keep_tag(tag):
                        tag.decompose()
                problems.append(self.replace_unicode_spaces(html.unescape(str(soup)))[17:])
            pages.append(problems)

        updated_pages = []
        for page in pages:
            updated_pages.append([self.replace_images_with_placeholder(problem) for problem in page])

        simplified_pages = []
        for page in updated_pages:
            simplified_pages.append([self.simplify_image_tags(problem) for problem in page])

        return simplified_pages

    def remove_newlines_inside_dollars(self, s):
        dollar_sections = re.findall(r'\$.*?\$', s, re.DOTALL)
        for section in dollar_sections:
            cleaned_section = section.replace('\r\n', '')
            s = s.replace(section, cleaned_section)
        return s
        
    def should_keep_tag(self, tag):
        if not isinstance(tag, Tag):
            return False
        if tag.attrs and tag.get('style'):
            return True
        if tag.get_text(strip=True):
            return True
        for child in tag.children:
            if self.should_keep_tag(child):
                return True
        return False

    @staticmethod
    def replace_unicode_spaces(text):
        unicode_spaces = [
            '\u0020',  # 공백(space)
            '\u00A0',  # 비분리 공백(no-break space)
            '\u0009',  # 수평 탭(horizontal tab)
            '\u000A',  # 줄 바꿈(line feed)
            '\u000B',  # 수직 탭(vertical tab)
            '\u000C',  # 폼 피드(form feed)
            '\u000D',  # 캐리지 리턴(carriage return)
            '\u1680',  # Ogham space mark
            '\u2000',  # en quad
            '\u2001',  # em quad
            '\u2002',  # en space
            '\u2003',  # em space
            '\u2004',  # three-per-em space
            '\u2005',  # four-per-em space
            '\u2006',  # six-per-em space
            '\u2007',  # figure space
            '\u2008',  # punctuation space
            '\u2009',  # thin space
            '\u200A',  # hair space
            '\u200B',  # zero width space
            '\u200C',  # zero width non-joiner
            '\u200D',  # zero width joiner
            '\u2028',  # line separator
            '\u2029',  # paragraph separator
            '\u202F',  # narrow no-break space
            '\u205F',  # medium mathematical space
            '\u3000',  # ideographic space
            '\uFEFF'   # zero width no-break space
        ]
        for space in unicode_spaces:
            text = text.replace(space, ' ')
        return text

    def replace_images_with_placeholder(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all('div'):
            if 'style' in tag.attrs and 'url' in tag['style']:
                tag.replace_with("[image]")
        for tag in soup.find_all('image'):
            tag.replace_with("[image]")
        return self.replace_unicode_spaces(html.unescape(str(soup)))

    def simplify_image_tags(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all('div'):
            if tag.get_text(strip=True) == "[image]":
                tag.replace_with("[image]")
        return self.replace_unicode_spaces(html.unescape(str(soup)))

    def extract_page_info(self, uuid_to_eqn):
        classes = [div.get('class') for div in self.soup.body.find_all()]

        repeated_classes = self.find_consecutive_classes(classes)
        stop_classes, line_break_classes_list = self.get_classes(repeated_classes)
        pages_positions = extract_positions(self.soup, stop_classes)

        self.remove_line_break(line_break_classes_list)
        self.remove_attributes(attributes_to_remove)
        self.replace_uids_with_math_tags(uuid_to_eqn)

        divs = self.process_div_elements(line_break_classes_list)

        pages = self.replace_image_tag(divs)
        pages = [[self.remove_newlines_inside_dollars(problem) for problem in page] for page in pages]
        return pages, pages_positions

    def extract_endnote_info(self, uuid_to_eqn):
        endnote_positions = get_endnote_positions(self.soup)

        html_str = str(self.soup)
        for uid in uuid_to_eqn:
            html_str = html_str.replace(uid, f"${uid}$")
        self.soup = BeautifulSoup(html_str, 'html.parser')

        self.remove_attributes(attributes_to_remove)
        divs = self.clean_html_tags()

        pages = []
        for problem in divs:
            soup_ = BeautifulSoup(str(problem), 'html.parser')
            for tag in soup_.find_all(['div', 'path']):
                if not self.should_keep_tag(tag):
                    tag.decompose()
            pages.append(HtmlPhaser.replace_unicode_spaces(html.unescape(str(soup_)))[17:])

        pages = [self.replace_images_with_placeholder(problem) for problem in pages]
        pages = [self.simplify_image_tags(problem) for problem in pages]

        endnotes = []
        for page in pages:
            soup_ = BeautifulSoup(page, 'html.parser')

            text_parts = []
            for div in soup_.find_all(string=True):
                text_parts.append(div.get_text())

            solutions = split_problems(text_parts)
            solutions = ['\n'.join(solution[1:]) for solution in solutions]
            endnotes.append(solutions)
        endnotes = [endnote for endnote in endnotes if len(endnote) > 0]

        return endnotes, endnote_positions