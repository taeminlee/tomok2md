import json
import os
import fire
import requests
from util import logger
import html2md
import tqdm


def kds2md(code=40145, save_json=True, md_filename='default', md_mode='default'):
    """KDS json을 읽고, markdown으로 변환

    Args:
        code (int, optional): 건설기준 웹 뷰어 코드. Defaults to 40145.
        save_json (bool, optional): JSON 파일 저장. Defaults to True.
        md_filename (str, optional): 저장 이름, default시 [code].md 로 저장. Defaults to 'default'.
        md_mode (str, optional): 마크다운 저장 모드, default 시 일반 문서 형식으로 저장, chunk 시 구획 단위로 나뉘어진 json array로 저장. Defaults to 'default.
    """
    json_filename = f'{code}.json'
    if md_filename == 'default':
        md_filename = f'{code}.md'
    
    if os.path.exists(json_filename):
        with open(json_filename) as fp:
            doc = json.load(fp)
        logger.info(f'READ {json_filename}')
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
            "Content-Type": "application/json"
        }

        payload = {'paramSeq': "40145"}

        logger.info(f'DOWNLOAD {code}')
        response = requests.post('https://www.kcsc.re.kr/api/ViewerApi/Detail', json=payload, headers=headers)
        logger.debug(response)

        doc = response.json()
        if(save_json):
            with open(json_filename, 'w') as fp:
                json.dump(doc, fp, ensure_ascii=False, indent=4)
        
    md = ''
    logger.info(f'CONVERT {json_filename} => {md_filename}')
    for doc_fragment in tqdm.tqdm(doc['detail']['listDocument']):
        md += html2md.html2md(doc_fragment).md
    logger.info(f'SAVE INTO {md_filename}')
    with open(md_filename, 'w') as fp:
        fp.write(md)
    logger.info(f'DONE')


if __name__ == '__main__':
    fire.Fire(kds2md)

