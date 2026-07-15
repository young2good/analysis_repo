"""네이버 카페 매칭 게시판(clubid=11367414, menuid=647) 크롤러.

목록은 비로그인으로 열리는 공식 목록 API(ArticleListV2.json)를 사용하고,
페이지 이동은 search.page 증가 + 응답의 hasNext 플래그를 따른다.
작성일은 writeDateTimestamp(밀리초 epoch)를 YYYY-MM-DD로 변환한다.
"""
import time
from datetime import datetime

import requests

SOURCE = "naver_cafe"

CLUBID = "11367414"
MENUID = "647"
API_URL = "https://apis.naver.com/cafe-web/cafe2/ArticleListV2.json"
POST_URL_PREFIX = f"https://cafe.naver.com/f-e/cafes/{CLUBID}/articles/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://cafe.naver.com/",
}
PAGE_DELAY_SEC = 0.8
PER_PAGE = 20


def _get_page(page_num):
    params = {
        "search.clubid": CLUBID,
        "search.menuid": MENUID,
        "search.page": str(page_num),
        "search.perPage": str(PER_PAGE),
        "search.queryType": "lastArticle",
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
    result = resp.json()["message"]["result"]

    posts = []
    for a in result.get("articleList", []):
        ts = a.get("writeDateTimestamp")
        created = (
            datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
            if ts else None
        )
        article_id = str(a["articleId"])
        posts.append({
            "source":  SOURCE,
            "dataid":  article_id,
            "title":   a.get("subject", ""),
            "created": created,
            "url":     POST_URL_PREFIX + article_id,
        })
    return posts, result.get("hasNext", False)


def collect_posts(max_pages=15, date_from=None, date_to=None, progress_cb=None):
    """게시글을 수집해 공통 스키마 리스트로 반환한다.

    date_from/date_to: "YYYY-MM-DD" (None이면 해당 방향 제한 없음)
    progress_cb: callable(cur_page, max_pages, total_count) — 대시보드 진행률 표시용
    """
    from_dt = datetime.strptime(date_from, "%Y-%m-%d") if date_from else None
    to_dt   = datetime.strptime(date_to,   "%Y-%m-%d") if date_to   else None

    all_posts = []
    for page in range(1, max_pages + 1):
        if page > 1:
            time.sleep(PAGE_DELAY_SEC)
        posts, has_next = _get_page(page)
        all_posts.extend(posts)
        if progress_cb:
            progress_cb(page, max_pages, len(all_posts))

        # 이 페이지의 최신 글이 이미 수집 시작일보다 오래됐으면 더 내려갈 필요 없음
        if from_dt and posts:
            dates = [datetime.strptime(p["created"], "%Y-%m-%d") for p in posts if p["created"]]
            if dates and max(dates) < from_dt:
                break
        if not has_next:
            break

    if from_dt or to_dt:
        all_posts = [
            p for p in all_posts
            if p["created"]
            and (from_dt is None or datetime.strptime(p["created"], "%Y-%m-%d") >= from_dt)
            and (to_dt   is None or datetime.strptime(p["created"], "%Y-%m-%d") <= to_dt)
        ]
    return all_posts
