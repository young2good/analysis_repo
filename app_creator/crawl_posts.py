"""등록된 크롤러들을 실행해 원본 게시글을 수집하고 posts_raw.json으로 저장한다.

python crawl_posts.py            # 작성일 기준 최근 DEFAULT_DAYS일 게시글 수집
python crawl_posts.py --days 7   # 작성일 기준 최근 7일 게시글 수집

# 테스트용: 시작·끝 작성일을 직접 지정 (지정 시 --days 무시)
# 오래된 기간은 목록 페이지를 더 내려가야 하므로 --max-pages를 함께 늘릴 것
python crawl_posts.py --date-from 2026-03-01 --date-to 2026-03-31 --max-pages 60

수집 기간은 게시글 "작성일" 기준이다 (제목에 적힌 경기일과는 다름 — 경기일 필터는
파싱 후 뷰어에서 수행한다). 크롤링만 담당하며, 파싱은 parse_posts.py에서 수행한다.
새 크롤링 소스를 추가하려면 crawlers/ 에 모듈을 만들고 CRAWLERS에 등록하면 된다.
"""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from crawlers import daum_cafe
from crawlers import naver_cafe

RAW_JSON = Path(__file__).resolve().parent / "posts_raw.json"

# 크롤링 조건 (필요시 여기만 수정)
DEFAULT_DAYS = 14   # 작성일 기준 최근 N일
MAX_PAGES = 15

CRAWLERS = [
    daum_cafe,
    naver_cafe,
]


def main(days=DEFAULT_DAYS, date_from=None, date_to=None, max_pages=MAX_PAGES):
    d_to = date.fromisoformat(date_to) if date_to else date.today()
    d_from = date.fromisoformat(date_from) if date_from else d_to - timedelta(days=days)
    label = "직접 지정" if (date_from or date_to) else f"최근 {days}일"
    print(f"수집 기간(작성일 기준): {d_from} ~ {d_to} ({label}) / 최대 {max_pages}페이지")

    all_posts = []
    for crawler in CRAWLERS:
        posts = crawler.collect_posts(
            max_pages=max_pages,
            date_from=d_from.isoformat(),
            date_to=d_to.isoformat(),
        )
        print(f"[{crawler.SOURCE}] {len(posts)}개 수집")
        all_posts.extend(posts)

    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    print(f"saved: {RAW_JSON}")
    print(f"total: {len(all_posts)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="게시글 크롤링 (작성일 기준 최근 N일)")
    parser.add_argument(
        "--days", type=int, default=DEFAULT_DAYS,
        help=f"작성일 기준 최근 N일 게시글 수집 (기본 {DEFAULT_DAYS}일)",
    )
    parser.add_argument(
        "--date-from", metavar="YYYY-MM-DD",
        help="테스트용: 시작 작성일 직접 지정 (지정 시 --days 무시)",
    )
    parser.add_argument(
        "--date-to", metavar="YYYY-MM-DD",
        help="테스트용: 끝 작성일 직접 지정 (기본: 오늘)",
    )
    parser.add_argument(
        "--max-pages", type=int, default=MAX_PAGES,
        help=f"목록 최대 페이지 수 (기본 {MAX_PAGES} — 오래된 기간 조회 시 늘릴 것)",
    )
    args = parser.parse_args()
    main(args.days, args.date_from, args.date_to, args.max_pages)
