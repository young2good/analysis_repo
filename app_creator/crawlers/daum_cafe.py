"""다음 카페 '경기북부 주말축구' 게시판(skfootball/IxVG) 크롤러.

목록 API 응답이 JS 코드(articles.push({...}))라서 정규식으로 파싱하고,
페이지 이동은 firstbbsdepth/lastbbsdepth 커서 토큰 방식을 따른다.
"""
import re
import json
import time
from datetime import datetime

import requests

SOURCE = "daum_cafe"

GRPID = "1O7ju"
FLDID = "IxVG"
BASE_URL = f"https://cafe.daum.net/_c21_/bbs_list?grpid={GRPID}&fldid={FLDID}"
POST_URL_PREFIX = f"https://cafe.daum.net/skfootball/{FLDID}/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": f"https://cafe.daum.net/skfootball/{FLDID}",
}
PAGE_DELAY_SEC = 0.8


def _parse_pushes(raw):
    pushes = re.findall(r'articles\.push\(\{[^}]+\}\)', raw)
    result = []
    for item in pushes:
        dm = re.search(r"dataid:\s*'(\d+)'", item)
        tm = re.search(r"title:\s*'([^']*)'", item)
        cm = re.search(r"created:\s*'([^']+)'", item)
        if dm and tm:
            created_str = cm.group(1) if cm else None
            try:
                created_dt = datetime.strptime(created_str, "%y.%m.%d") if created_str else None
            except ValueError:
                created_dt = None
            dataid = dm.group(1)
            result.append({
                "source":  SOURCE,
                "dataid":  dataid,
                "title":   json.loads(f'"{tm.group(1)}"'),
                "created": created_dt.strftime("%Y-%m-%d") if created_dt else None,
                "url":     POST_URL_PREFIX + dataid,
            })
    return result


def _get_page(page_num, prev_page, first_depth, last_depth):
    url = (
        f"{BASE_URL}"
        f"&page={page_num}&prev_page={prev_page}&listnum=20"
        f"&firstbbsdepth={first_depth}&lastbbsdepth={last_depth}"
    )
    raw = requests.get(url, headers=HEADERS).text
    new_first = re.search(r"firstBbsDepth:\s*'([^']+)'", raw)
    new_last  = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw)
    return (
        _parse_pushes(raw),
        page_num,
        new_first.group(1) if new_first else None,
        new_last.group(1)  if new_last  else None,
    )


def collect_posts(max_pages=15, date_from=None, date_to=None, progress_cb=None):
    """게시글을 수집해 공통 스키마 리스트로 반환한다.

    date_from/date_to: "YYYY-MM-DD" (None이면 해당 방향 제한 없음)
    progress_cb: callable(cur_page, max_pages, total_count) — 대시보드 진행률 표시용
    """
    from_dt = datetime.strptime(date_from, "%Y-%m-%d") if date_from else None
    to_dt   = datetime.strptime(date_to,   "%Y-%m-%d") if date_to   else None

    raw0 = requests.get(BASE_URL, headers=HEADERS).text
    all_posts = _parse_pushes(raw0)

    m_first = re.search(r"firstBbsDepth:\s*'([^']+)'", raw0)
    m_last  = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw0)
    if not m_first or not m_last:
        print(f"[{SOURCE}] 목록 파싱 실패")
        return []

    cur_first = m_first.group(1)
    cur_last  = m_last.group(1)
    cur_page  = 1
    if progress_cb:
        progress_cb(1, max_pages, len(all_posts))

    for _ in range(max_pages - 1):
        time.sleep(PAGE_DELAY_SEC)
        posts, cur_page, cur_first, cur_last = _get_page(
            cur_page + 1, cur_page, cur_first, cur_last
        )
        all_posts.extend(posts)
        if progress_cb:
            progress_cb(cur_page, max_pages, len(all_posts))

        # 이 페이지의 최신 글이 이미 수집 시작일보다 오래됐으면 더 내려갈 필요 없음
        if from_dt and posts:
            dates = [datetime.strptime(p["created"], "%Y-%m-%d") for p in posts if p["created"]]
            if dates and max(dates) < from_dt:
                break
        if not cur_first:
            break

    if from_dt or to_dt:
        all_posts = [
            p for p in all_posts
            if p["created"]
            and (from_dt is None or datetime.strptime(p["created"], "%Y-%m-%d") >= from_dt)
            and (to_dt   is None or datetime.strptime(p["created"], "%Y-%m-%d") <= to_dt)
        ]
    return all_posts
