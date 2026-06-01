"""
Step 1 - 게시판 크롤링
지정한 게시판·날짜 범위의 게시글 제목을 수집해 JSON으로 저장.

사용법:
    python step1_crawl.py
아래 CONFIG 블록만 수정하면 됨.
"""
import re
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# ── CONFIG ───────────────────────────────────────────────────────────────────
GRPID       = "1O7ju"
FLDID       = "IxVG"           # 경기북부 주말축구 게시판
BOARD_LABEL = "경기북부게시판"
DATE_FROM   = "2026-04-15"
DATE_TO     = "2026-04-30"
MAX_PAGES   = 20
# ─────────────────────────────────────────────────────────────────────────────

BASE   = Path(__file__).parent
OUTPUT = BASE / "data" / f"raw_posts_{BOARD_LABEL}_{DATE_FROM}_{DATE_TO}.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": f"https://cafe.daum.net/skfootball/{FLDID}",
}
BASE_URL = f"https://cafe.daum.net/_c21_/bbs_list?grpid={GRPID}&fldid={FLDID}"


def _parse_pushes(raw: str) -> list[dict]:
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
            result.append({
                "dataid":  dm.group(1),
                "title":   json.loads(f'"{tm.group(1)}"'),
                "created": created_dt.isoformat() if created_dt else None,
            })
    return result


def _get_page(page_num, prev_page, first_depth, last_depth):
    url = (
        f"https://cafe.daum.net/_c21_/bbs_list?grpid={GRPID}&fldid={FLDID}"
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


def collect_posts(date_from: str, date_to: str, max_pages: int = MAX_PAGES) -> list[dict]:
    from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    to_dt   = datetime.strptime(date_to,   "%Y-%m-%d")

    raw0 = requests.get(BASE_URL, headers=HEADERS).text
    all_posts = _parse_pushes(raw0)

    m_first = re.search(r"firstBbsDepth:\s*'([^']+)'", raw0)
    m_last  = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw0)
    if not m_first or not m_last:
        print("1페이지 파싱 실패")
        return []

    cur_first, cur_last, cur_page = m_first.group(1), m_last.group(1), 1
    print(f"page 1 - {len(all_posts)}개")

    for _ in range(max_pages - 1):
        time.sleep(1)
        posts, cur_page, cur_first, cur_last = _get_page(cur_page + 1, cur_page, cur_first, cur_last)
        print(f"page {cur_page} - {len(posts)}개")
        all_posts.extend(posts)

        if posts:
            latest = max(
                (datetime.fromisoformat(p["created"]) for p in posts if p["created"]),
                default=None,
            )
            if latest and latest < from_dt:
                print(f"  → {from_dt.date()} 이전 도달, 수집 중단")
                break

        if not cur_first:
            print("마지막 페이지 도달")
            break

    print(f"\n총 수집: {len(all_posts)}개")

    filtered = [
        p for p in all_posts
        if p["created"]
        and from_dt <= datetime.fromisoformat(p["created"]) <= to_dt
    ]
    print(f"날짜 필터 ({date_from} ~ {date_to}): {len(filtered)}개")
    return filtered


def main():
    posts = collect_posts(DATE_FROM, DATE_TO)

    seen, dedup = set(), []
    for p in posts:
        if p["dataid"] not in seen:
            seen.add(p["dataid"])
            dedup.append(p)
    print(f"중복 제거 후: {len(dedup)}개")

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(dedup, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {OUTPUT}")


if __name__ == "__main__":
    main()
