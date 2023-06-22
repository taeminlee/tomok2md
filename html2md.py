from lxml import html
import re
import pcre
import tomd
from util import logger


class html2md():
    def __init__(self, doc):
        parser = html.HTMLParser()
        self.doc = doc
        html_str = doc['subView']
        if html_str == '':  # 2023-06-22 empty html 에러 우회
            html_str = "<body></body>"
        self.tree = html.fromstring(html_str, parser=parser)
        # 수식 변환
        self.conv_formula()
        # 그림 변환
        # 테이블 변환
        self.conv_table()
        # 태그 제거
        self.md = self.html2md()
        # 타이틀 추가
        self.md = self.add_title()
    def conv_formula(self):
        style_symbols = ['rm',
                         'bold',
                         'it']
        function_symbols =[
            'arccos',
            'cos',
            'csc',
            'exp',
            'ker',
            'limsup',
            'min',
            'sinh',
            'arcsin',
            'cosh',
            'deg',
            'gcd',
            'lg',
            'ln',
            'Pr',
            'sup',
            'arctan',
            'cot',
            'det',
            'hom',
            'lim',
            'log',
            'sec',
            'tan',
            'arg',
            'coth',
            'dim',
            'inf',
            'liminf',
            'max',
            'sin',
            'tanh',
        ]
        math_symbols = ['over',
                        'BULLET',
                        'TIMES',
                        'DEG',
                        'sqrt',
                        'prime',
                        'SMALLSUM',
                        '%', # 2023-06-14 # 4.2.4.2
                        'INF', # 2023-06-14 # 4.2.4.3
                        'sum', # 2023-06-15 # 4.5.4.5
                        'LITER', # 2023-06-15 # 4.5.8.2
                        ]
        relation_symbols = ['LEQ',
                            'LEFT',
                            'RIGHT',
                            'left',
                            'right',
                            'GEQ',
                            'LT',
                            'RT',
                            'CDOT',
                            'le', # 2023-06-22 4.1.2.4
                            'ge', # 2023-06-22 4.1.2.4
                            ]
        greek_symbols = ['alpha',
                   'beta',
                   'chi',
                   'delta',
                   'epsilon',
                   'eta',
                   'gamma',
                   'iota',
                   'kappa',
                   'lambda',
                   'mu',
                   'nu',
                   'omega',
                   'phi',
                   'pi',
                   'psi',
                   'rho',
                   'sigma',
                   'tau',
                   'theta',
                   'upsilon',
                   'xi',
                   'zeta',
                   'digamma',
                   'varepsilon',
                   'varkappa',
                   'varphi',
                   'varpi',
                   'varrho',
                   'varsigma',
                   'vartheta',
                   'DELTA',
                   'GAMMA',
                   'LAMBDA',
                   'OMEGA',
                   'PHI',
                   'PI',
                   'PSI',
                   'SIGMA',
                   'THETA',
                   'UPSILON',
                   'XI',
                   'ALEPH',
                   'BETH',
                   'DALETH',
                   'gimel']
        symbol_fixes = {
            'DELTA': 'Delta',
            'GAMMA': 'Gamma',
            'LAMBDA': 'Lambda',
            'OMEGA': 'Omega',
            'PHI': 'Phi',
            'PI': 'Pi',
            'PSI': 'Psi',
            'SIGMA': 'Sigma',
            'THETA': 'Theta',
            'UPSILON': 'Upsilon',
            'XI': 'Xi',
            'ALEPH': 'Aleph',
            'BETH': 'Beth',
            'DALETH': 'Daleth',
            'LEQ': 'leq',
            'LEFT': 'left',
            'RIGHT': 'right',
            'BULLET': 'bullet',
            'TIMES': 'times',
            'DEG': 'degree',
            'GEQ': 'geq',
            'SMALLSUM': 'sum',
            'LT': 'lt',
            'RT': 'rt',
            'CDOT': 'cdot',
            'INF': 'infty',
            'LITER': 'ell',
        }
        pre_fixes = {
            '［':'[',
            '］':']',
            # '<': 'LT',  # 2023-06-14 &lt; # md 컨버팅 후에 발생하는 문제. md conv 단계에서 해결하도록 함
            # '>': 'RT',  # 2023-06-14 &rt; # md 컨버팅 후에 발생하는 문제. md conv 단계에서 해결하도록 함
            '&': '~',
            '�': '#0',  # 2023-06-14 3.1.2.4,
            '': '|',  # 2023-06-14 4.1.7.1
            'ALPHA': 'A', # 2023-06-15 4.7.1.6
            'left(': 'left( ', # 2023-06-22 4.1.1.3
        }
        post_fixes = {
            '\\left  {': '\\left \{',
            '\\right  }': '\\right \}',
            '\\prime': '^\\prime',
            '#': '\\\\', # 2023-06-15 # 4.7.3.3
            '`%': '\\%', # 2023-06-22 # 3.1.2.4
        }
        symbols = style_symbols + \
                  greek_symbols + \
                  relation_symbols + \
                  math_symbols + \
                  function_symbols

        symbol_regex = r'|'.join([fr'({symbol})' for symbol in symbols])
        # 2023-06-12 sqrt fix # 4.2.4.2
        sqrt_regex = r'root[^{]*{([^}]*)}\s*of'
        # 2023-06-13 over fix
        over_regex = r'(?:({([^{}]|(?1))*})|[^{}\s]*)\s*\\over\s*(?:({([^{}]|(?2))*})|[^{}\s]*)'
        # 2023-06-14 cases fix
        cases_regex = r'{\s*cases({(([^{}]|(?1))*)})}'
        # 2023-06-15 eqalign remove # 4.5.2.1
        eqalign_regex = r'_{eqalign{[^{}]*}}'
        remove_char = ['`']
        

        if self.tree is None:
            return

        for elem in self.tree.iter():
            if(elem.tag == 'img' and 'data-script' in elem.attrib.keys()):
                logger.debug('ELEM_ATTRIB ' + str(elem.attrib))
                elem.tag = 'span'
                eq = elem.get('data-script')

                for from_eq, to_eq in pre_fixes.items():
                    if from_eq in eq:
                        eq = eq.replace(from_eq, to_eq)
                        # print('PREFIX', from_eq, eq)

                mod_eq = ''
                cursor = 0

                for match in re.finditer(symbol_regex, eq, re.MULTILINE):
                    mod_eq += eq[cursor:match.start()]
                    symbol = match.group()
                    if symbol in symbol_fixes.keys():
                        symbol = symbol_fixes[symbol]
                    mod_eq += '\\' + symbol + ' '
                    cursor = match.end()

                mod_eq += eq[cursor:]
                logger.debug('MOD EQ ' +  mod_eq)
                for char in remove_char:
                    mod_eq = mod_eq.replace(char, '')

                # 2023-06-12 sqrt fix
                mod_eq = re.sub(sqrt_regex, r'\\sqrt[\1]', mod_eq)
                
                # 2023-06-13 over fix
                add_tokens = 0
                for m in pcre.finditer(over_regex, mod_eq):
                    # print("OVER REGEX", m)
                    new_eq = mod_eq[0:m.start()+add_tokens]
                    new_eq += '{' + mod_eq[m.start()+add_tokens:m.end()+add_tokens] + '}'
                    new_eq += mod_eq[m.end()+add_tokens:]
                    mod_eq = new_eq
                    add_tokens += 2
                
                # 2023-06-14 cases fix
                for m in pcre.finditer(cases_regex, mod_eq):
                    orig_len = len(m.group())
                    mod_cases = '\\begin{cases}' + m.group(2) + '\\end{cases}'
                    mod_cases = mod_cases.replace('#', '\\\\')
                    new_eq = mod_eq[0:m.start()+add_tokens]
                    new_eq += mod_cases
                    new_eq += mod_eq[m.end()+add_tokens:]
                    mod_eq = new_eq
                    # print('MOD CASES', new_eq)
                    add_tokens += (len(mod_cases) - orig_len)
                
                # 2023-06-15 eqalign remove
                mod_eq = re.sub(eqalign_regex, '', mod_eq)
                
                # 2023-06.14 notend fix
                if mod_eq.count('{') != mod_eq.count('}'):
                    mod_eq += '}'
                
                for from_eq, to_eq in post_fixes.items():
                    mod_eq = mod_eq.replace(from_eq, to_eq)
                
                if mod_eq != '':
                    elem.text = '${0}$'.format(mod_eq)
                else:
                    elem.text = ''
                for key in elem.attrib.keys():
                    elem.attrib.pop(key)

    def html2md(self):
        if self.tree == None:
            return ''
        html_str = html.tostring(self.tree, encoding='UTF-8').decode('UTF-8')
        logger.debug("HTML_STR " + html_str[0:10])
        md = tomd.Tomd(html_str).markdown
        logger.debug("MD " + md)

        md = md.replace('&lt;', '<')
        md = md.replace('&gt;', '>')
        # print(md)
        return md
    def add_title(self):
        title_tree = html.fromstring(self.doc['contentsView'], parser=html.HTMLParser())

        level = int(title_tree.xpath('./a')[0].get('data-level'))
        title_md = '#' * level + ' ' + title_tree.xpath('./a')[0].text
        # print(title_md)
        return f'{title_md}\n\n{self.md}'

    def conv_table(self):
        # table 태그 선택
        remove_elems = {}
        for elem in self.tree.iter():
            if elem.tag == 'table':
                table = elem
                remove_elems[table] = []

                # caption, header와 body 태그 선택
                captions = table.xpath('./caption')
                header = table.xpath('./thead/tr')
                body = table.xpath('./tbody/tr')
                body = header + body

                col_cnt = 0

                # body 내용 추출
                body_rows = []
                matrix = {}
                first_row_has_row_span = False
                for row_idx, row in enumerate(body):
                    col_cnt = 0
                    if row_idx not in matrix:
                        matrix[row_idx] = {}
                    for rel_col_idx, cell in enumerate(row.xpath('./td')):
                        row_span = 1
                        col_span = 1
                        col_idx = rel_col_idx
                        while col_idx in matrix[row_idx]:
                            col_idx += 1
                        if 'colspan' in cell.attrib.keys():
                            col_span = int(cell.attrib['colspan'])
                        if 'rowspan' in cell.attrib.keys():
                            row_span = int(cell.attrib['rowspan'])
                        if row_span > 1:
                            for span_idx in range(1, row_span):
                                if row_idx + span_idx not in matrix:
                                    matrix[row_idx + span_idx] = {}
                                matrix[row_idx + span_idx][col_idx] = '^'
                                if row_idx+span_idx == 1:
                                    first_row_has_row_span = True
                        elif col_span > 1:
                            for span_idx in range(1, col_span):
                                matrix[row_idx][col_idx + span_idx] = ''
                        cell_value = "</br>".join([p.text_content().strip() for p in cell.xpath('./p')])
                        logger.debug(html.tostring(cell))
                        for img in cell.xpath('.//img'):
                            # print(img)
                            cell_value += 'ㅤ' + html.tostring(img).decode()
                        if cell_value == '':  # 2023-06-22 내용이 빈 td 처리
                            cell_value = 'ㅤ'
                        matrix[row_idx][col_idx] = cell_value
                    matrix[row_idx] = dict(sorted(matrix[row_idx].items()))
                matrix = dict(sorted(matrix.items()))
                
                col_cnt = len(matrix[0])
                body_rows = ['|' + '|'.join([cell for cell in row.values()]) + '|' for row in matrix.values()]

                # # 마크다운 테이블 생성
                markdown_table = '\n'.join(body_rows)

                # # 출력
                logger.debug("MARKDOWN TABLE START " + markdown_table)
                logger.debug("MARKDOWN TABLE END")
                # elem.text = markdown_table
                table.tag = 'table'
                for key in table.attrib.keys():
                    table.attrib.pop(key)

                for child in table: # 2023-06-22 child elem 제거 부분 수정
                    remove_elems[table].append(child)

                caption_rows = []

                for caption in captions:  # 2023-06-21 header row에 caption 추가
                    caption_rows.append('|' + caption.text_content() + '|' * col_cnt)

                logger.debug('first_row_has_row_span ' + str(first_row_has_row_span))
                
                if first_row_has_row_span and len(caption_rows) == 0:  # 2023-06-22 header row에서 row span 안되므로, 빈 줄 추가
                    caption_rows.append('| ' + '|' * col_cnt)
                
                logger.debug(caption_rows)
                
                rows = caption_rows + body_rows
                
                for idx, row in enumerate(rows):
                    row_elem = html.Element('tr')
                    row_elem.text = row
                    table.append(row_elem)
                    if idx == 0:
                        row_elem = html.Element('tr')
                        row_elem.text = ('|' + '---|' * col_cnt)
                        table.append(row_elem)
        
        for table in remove_elems:  # 2023-06-22 child elem 제거 부분 수정
            for elem in remove_elems[table]:
                table.remove(elem)
