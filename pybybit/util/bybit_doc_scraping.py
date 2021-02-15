import keyword

import bs4
import requests

# pip isntall requests bs4

# Running the script will create a bybit_doc_scraping.txt and md file in the current directory.

urls = {
    'Inverse': 'https://bybit-exchange.github.io/docs/inverse',
    'Linear': 'https://bybit-exchange.github.io/docs/linear',
}

rm_pathname = ['v2', 'linear']
repl_pathname = {'open-api': 'private'}

type_mapping = {
    'string': str,
    'integer': int,
    'int': int,
    'number': float,
    'bool': bool,
}

table = {}
with open('bybit_doc_scraping.txt', 'w') as f:
    for cont, url in urls.items():
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        text = ''
        text += f'class {cont}:\n'
        text += f'    def __init__(self, request: RESTAPI._request):\n'
        text += f'        self._request = request\n'
        text += f'\n'
        print(text)
        f.write(text)

        http_request = False
        request_parameters = False
        # response_parameters = False
        desc = None
        method = None
        path = None
        params = []
        table[cont] = []
        for element in soup.select_one('body > div.page-wrapper > div.content'):
            if isinstance(element, bs4.element.Tag):
                if element.name in {'h1', 'h2', 'h3', }:
                    # changed section
                    if method and path:
                        p_list = path[1:].split('/')
                        for rm in rm_pathname:
                            if rm in p_list:
                                p_list.remove(rm)
                        for k, v in repl_pathname.items():
                            if k in p_list:
                                idx = p_list.index(k)
                                p_list[idx] = p_list[idx].replace(k, v)
                        funcname = '_'.join(p_list).replace('-', '').lower()
                        private = 'True' if 'private' in funcname else 'False'

                        text = ''
                        text += f'    def {funcname}(\n'
                        text += f'        self,\n'
                        for p, t in params:
                            p = p if not keyword.iskeyword(p) else f'{p}_'
                            text += f'        {p}: {t.__name__}=None,\n'
                        text += f'    ) -> requests.Response:\n'
                        text += f'        """\n'
                        text += f'        {desc}\n'
                        text += f'        """\n'
                        text += f"        method = '{method}'\n"
                        text += f"        path = '{path}'\n"
                        text += f"        query = {{\n"
                        for p, t in params:
                            _p = p if not keyword.iskeyword(p) else f'{p}_'
                            text += f"            '{p}': {_p},\n"
                        text += f"        }}\n"
                        text += f'        return self._request(method, path, query, private={private})\n'
                        text += '\n'
                        print(text)
                        f.write(text)

                        table[cont] += [(funcname, method, path, desc, )]

                        method = None
                        path = None
                        params.clear()
                    desc = element.text
                    if desc == 'Abandoned Endpoints':
                        break
                elif element.name == 'p':
                    if element.text == 'HTTP Request':
                        http_request = True
                    elif element.text == 'Request Parameters':
                        request_parameters = True
                    # elif element.text == 'Response Parameters':
                    #     response_parameters = True
                if http_request:
                    if element.name == 'p':
                        if element.select_one('code > span'):
                            http_request = False
                            strings = element.strings
                            method: str = next(strings)[:-1]
                            path: str = next(strings)
                if request_parameters:
                    if element.name == 'table':
                        request_parameters = False
                        for tr in element.select('tbody > tr'):
                            tr: bs4.element.Tag
                            tds: list[bs4.Tag] = list(tr.select('td'))
                            params.append((tds[0].text, type_mapping[tds[2].text], ))
                # if response_parameters:
                #     pass

text = ''
text += '## メソッド名⇔エンドポイント名 対応表\n'
for cont in table:
    text += f'### {cont}\n'
    header = ['Function Name', 'Http Method', 'Endpoint URL', 'Description', ]
    text += f"| {' | '.join(header)} |\n"
    text += f"| {' | '.join(['---'] * len(header))} |\n"
    for row in table[cont]:
        text += f"| {' | '.join(row)} |\n"
print(text)
with open('bybit_doc_scraping.md', 'w') as f:
    f.write(text)