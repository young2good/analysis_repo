import sys
import io
import re
import json
import time
import requests
import codecs
from datetime import datetime
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://cafe.daum.net/skfootball"
}

BOARDS = {
    "서울북부 주말축구": "IxV1",
    "서울남부 주말축구": "IxUz",
    "경기북부 주말축구": "IxVG",
    "경기남부 주말축구": "IxUs",
    "인천부천 주말축구": "Uc8G",
}

DATE_FROM = datetime(2026, 5, 8)
DATE_TO   = datetime(2026, 5, 21)


def decode_title(raw_title):
    try:
        return json.loads('"' + raw_title + '"')
    except Exception:
        try:
            return codecs.decode(raw_title, "unicode_escape").encode("latin-1").decode("utf-8")
        except Exception:
            return raw_title


def _parse_pushes(raw):
    pushes = re.findall(r"articles\.push\(\{[^}]+\}\)", raw)
    result = []
    for item in pushes:
        dm = re.search(r"dataid:\s*'(\d+)'", item)
        tm = re.search(r"title:\s*'([^']*)'", item)
        cm = re.search(r"created:\s*'([^']+)'", item)
        if dm and tm:
            created_str = cm.group(1) if cm else None
            try:
                created_dt = datetime.strptime(created_str, "%y.%m.%d") if created_str else None
            except Exception:
                created_dt = None
            result.append({
                "dataid":  dm.group(1),
                "title":   decode_title(tm.group(1)),
                "created": created_dt,
            })
    return result


def crawl_board(board_name, fldid, date_from, date_to, max_pages=20):
    base = f"https://cafe.daum.net/_c21_/bbs_list?grpid=1O7ju&fldid={fldid}"
    raw0 = requests.get(base, headers=headers).text
    first_page = _parse_pushes(raw0)
    cf = re.search(r"firstBbsDepth:\s*'([^']+)'", raw0)
    cl = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw0)
    if not cf or not cl:
        print(f"  [{board_name}] 파싱 실패")
        return []
    cf, cl = cf.group(1), cl.group(1)
    cp = 1
    result = []

    pages = [first_page] + [None] * (max_pages - 1)
    for page_posts in pages:
        if page_posts is None:
            time.sleep(2)
            url = (
                f"https://cafe.daum.net/_c21_/bbs_list?grpid=1O7ju&fldid={fldid}"
                f"&page={cp+1}&prev_page={cp}&listnum=20"
                f"&firstbbsdepth={cf}&lastbbsdepth={cl}"
            )
            raw = requests.get(url, headers=headers).text
            page_posts = _parse_pushes(raw)
            nf = re.search(r"firstBbsDepth:\s*'([^']+)'", raw)
            nl = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw)
            cp += 1
            cf = nf.group(1) if nf else None
            cl = nl.group(1) if nl else None

        done = False
        for p in page_posts:
            if p["created"] is None:
                continue
            if p["created"] > date_to:
                continue
            if p["created"] < date_from:
                done = True
                break
            result.append({**p, "board": board_name})

        print(f"  page {cp} - 누적 {len(result)}개")

        if done:
            print(f"  조기종료 (기간 이전 게시물 도달)")
            break
        if cf is None:
            print(f"  마지막 페이지 도달")
            break

    return result


all_posts = []
for i, (name, fldid) in enumerate(BOARDS.items()):
    print(f"\n[{name}] 크롤링 시작")
    posts = crawl_board(name, fldid, DATE_FROM, DATE_TO)
    print(f"  => {len(posts)}개 수집 완료")
    all_posts.extend(posts)
    if i < len(BOARDS) - 1:
        print("  (다음 게시판까지 5초 대기)")
        time.sleep(5)

print(f"\n===== 전체 수집: {len(all_posts)}개 =====")
df = pd.DataFrame(all_posts)
print(df["board"].value_counts().to_string())

df.to_json("data/raw_posts.json", orient="records", force_ascii=False, indent=2, date_format="iso")
print("\ndata/raw_posts.json 저장 완료")
