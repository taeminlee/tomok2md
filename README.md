# tomok2md

건설기준 md converter

## Install

- use [poetry](https://python-poetry.org/)

```sh
poetry install
```

## kds2md execution

- 건설기준 웹페이지를 읽고 md 형식으로 변환

- 실행 예시 : `콘크리트교 설계기준(한계상태설계법) KDS 24 14 21 :2021`

```sh
poetry run python kds2md.py --code=40145
```

- 실행 결과로 `40145.md` 과 `40145_chunks.json` 생성

    - `40145.md`는 건설기준 전체를 markdown 문법으로 변환함
        - md 문법 : github flavored + extended table syntax
        - ![](https://i.imgur.com/W6mQjuN.png)
    - `40145_chunks.json`은 건설기준을 구획별로 나누어 저장.
        - 주의 : Q&A 용도로 활용 가능하도록 이미지는 제거됨
        - ![](https://i.imgur.com/KPCIZrV.png)

- md 파일은 vscode의 markdown preview enhanced의 Markdown-preview-enhanced: Enable Extended Table Syntax 옵션을 키고 렌더링하는 것을 기준으로 생성되었음.

### options

```sh
NAME
    kds2md.py - KDS json을 읽고, markdown으로 변환

SYNOPSIS
    kds2md.py <flags>

DESCRIPTION
    KDS json을 읽고, markdown으로 변환

FLAGS
    --code=CODE
        Default: 40145
        건설기준 웹 뷰어 코드. Defaults to 40145.
    -s, --save_json=SAVE_JSON
        Default: True
        JSON 파일 저장. Defaults to True.
    -m, --md_filename=MD_FILENAME
        Default: 'default'
        저장 이름, default시 [code].md 로 저장. Defaults to 'default'.
    --chunks_filename=CHUNKS_FILENAME
        Default: 'default'
        저장 이름, default시 [code]_chunks.json 로 저장. Defaults to 'default'.
```