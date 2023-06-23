import json
import os
import fire
import requests
from util import logger
import html2md
import tqdm


def kds2md(code=40145, save_json=True, md_filename='default', chunks_filename='default'):
    """KDS json을 읽고, markdown으로 변환

    Args:
        code (int, optional): 건설기준 웹 뷰어 코드. Defaults to 40145.
        save_json (bool, optional): JSON 파일 저장. Defaults to True.
        md_filename (str, optional): 저장 이름, default시 [code].md 로 저장. Defaults to 'default'.
        chunks_filename (str, optional): 저장 이름, default시 [code]_chunks.json 로 저장. Defaults to 'default'.
    """
    json_filename = f'{code}.json'
    if md_filename == 'default':
        md_filename = f'{code}.md'
    if chunks_filename == 'default':
        chunks_filename = f'{code}_chunks.json'
    
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
        
    chunks = []
    headers = {}
    md = ''
    logger.info(f'CONVERT {json_filename} => {md_filename}')
    for doc_fragment in tqdm.tqdm(doc['detail']['listDocument']):
        doc_md = html2md.html2md(doc_fragment)
        md += doc_md.md_with_title
        if(doc_md.md.replace('<br>','').strip() == ''):
            headers[doc_md.level] = doc_md.title
        else:
            headers[doc_md.level] = doc_md.title
            if len(headers) > doc_md.level:
                for del_idx in range(doc_md.level, len(headers)):
                    del(headers[del_idx + 1])
            header_str = '\n\n'.join(headers.values())
            chunks.append({
                    'id': doc_md.id,
                    'content': f'{header_str}\n\n{doc_md.md_without_img}'.strip()
                })
            
    logger.info(f'SAVE INTO {md_filename}')
    with open(md_filename, 'w') as fp:
        fp.write(md)

    logger.info(f'SAVE INTO {chunks_filename}')
    with open(chunks_filename, 'w') as fp:
        json.dump(chunks, fp, ensure_ascii=False, indent=4)
    logger.info(f'DONE')


if __name__ == '__main__':
    fire.Fire(kds2md)

