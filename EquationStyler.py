import re


def insert_it(expression):
    """
    부등호 뒤에 - 오는 경우 it 추가
    """
    pattern = r'((?:LEQ|GEQ|<<|>>|<<<|>>>|PREC|SUCC|=|<=|>=|<|>|le|ge))\s*(-)'
    result = re.sub(pattern, r'\1 it \2', expression, flags=re.IGNORECASE)
    return result


def insert_tilde_after_comma(expression):
    """
    콤마 뒤에 ~ 
    """
    pattern = r',\s*(?!~)'  
    result = re.sub(pattern, ', ~', expression)
    return result

def add_backticks_to_arrows(expression):
    """
    화살표 앞 뒤로 `
    """
    pattern = r'(<-|->)'
    result = re.sub(pattern, r'`\1`', expression)
    return result

def insert_backtick_before_d(expression):
    """
    적분 d 앞에 `
    """
    pattern = r'(int[^d]*?)d'
    result = re.sub(pattern, r'\1`d', expression, count=1)
    return result

def insert_backticks_cases(expression):
    """
    cases 빈칸 추가
    """
    pattern = r'(cases\{)'
    expression = re.sub(pattern, r'\1``', expression)
    
    expression = re.sub(r'(#)', r'\1``', expression)
    expression = re.sub(r'(&)', r'\1\1\1', expression)
    return expression

def insert_backtick_before_prime(expression):
    """
    prime 앞에 `
    """
    return re.sub(r"\b((prime|')(?:\s*(prime|'))*)\b", r'`\1', expression)

def add_backticks_around_pipe(expression):
    """
    | 뒤에 `
    """
    pattern = r'\|'
    result = re.sub(pattern, r'|`', expression)
    return result

def add_backtick_after_trig_functions(expression):
    """
    삼각함수 앞 뒤로 `
    """
    pattern = r'\b(sin|cos|tan|sec|csc|cot)\b'
    result = re.sub(pattern, r'`\1`', expression)
    return result

def add_backtick_after_log(expression):
    """
    log 뒤에 `
    """
    pattern_with_underscore = r'((log|ln)\s*_\s*(\d+|{(?:[^{}]|\{[^{}]*\})*}))(.*?)(\s*\d+|\s*\w+)'
    def replace_with_underscore(match):
        return f"{match.group(1)}{match.group(4)}`{match.group(5)}"
    
    expression = re.sub(pattern_with_underscore, replace_with_underscore, expression)
    
    pattern_without_underscore = r'(log|ln)(?!\s*_)'
    expression = re.sub(pattern_without_underscore, 'log`', expression)
    
    return expression

def add_backtick_around_equals(expression):
    """
    sum 아래 = 앞 뒤로 `
    """
    pattern = r'(?i)(sum\s*_\s*\{[^{}]*?)=(.*?\})'
    def replace_equals(match):
        return f"{match.group(1)}`=`{match.group(2)}"
    
    expression = re.sub(pattern, replace_equals, expression)
    return expression

def add_backticks_between_brackets(expression):
    """
    대괄호 앞 뒤로 `
    """
    pattern = r'(?i)(left\s*\[)(\s*.*?\s*)(right\s*\])'
    def replace_brackets(match):
        return f"{match.group(1)}`{match.group(2)}`{match.group(3)}"
    
    # 패턴을 이용해 변환 적용
    expression = re.sub(pattern, replace_brackets, expression)
    
    return expression

def add_backtick_if_no_rm(expression):
    # rm이 문장에 없는지 확인
    if 'rm' not in expression:
        # 대문자 한 글자 뒤에 백틱을 추가하는 패턴
        pattern = r'\b([A-Z])\b'
        expression = re.sub(pattern, r'\1`', expression)
    return expression

def add_backtick(text):
    text = insert_it(text)
    text = insert_tilde_after_comma(text)
    text = add_backticks_to_arrows(text)
    text = insert_backtick_before_d(text)
    text = insert_backticks_cases(text)
    text = insert_backtick_before_prime(text)
    text = add_backticks_around_pipe(text)
    text = add_backtick_after_trig_functions(text)
    text = add_backtick_after_log(text)
    text = add_backtick_around_equals(text)
    text = add_backticks_between_brackets(text)
    text = add_backtick_if_no_rm(text)
    return text