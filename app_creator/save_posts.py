"""등록된 크롤러들을 실행해 게시글을 수집하고, 장소 매핑 후 JSON으로 저장한다.

python save_posts.py

새 크롤링 소스를 추가하려면 crawlers/ 에 모듈을 만들고 CRAWLERS에 등록하면 된다.
"""
import json
from pathlib import Path

from crawlers import daum_cafe
from crawlers import naver_cafe

from venue_mapping import apply_mapping

OUTPUT_JSON = Path(__file__).resolve().parent / "posts_temp.json"

# 크롤링 조건 (필요시 여기만 수정)
DATE_FROM = "2026-07-10"
DATE_TO   = "2026-07-30"
MAX_PAGES = 15

CRAWLERS = [
    daum_cafe,
    naver_cafe,
]


def main():
    all_posts = []
    for crawler in CRAWLERS:
        posts = crawler.collect_posts(
            max_pages=MAX_PAGES, date_from=DATE_FROM, date_to=DATE_TO
        )
        print(f"[{crawler.SOURCE}] {len(posts)}개 수집")
        all_posts.extend(posts)

    all_posts = apply_mapping(all_posts)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    goyang = sum(1 for p in all_posts if p["city"] == "고양시")
    unmapped = sum(1 for p in all_posts if not p["std_name"])
    print(f"saved: {OUTPUT_JSON}")
    print(f"total: {len(all_posts)} / 고양시: {goyang} / 미매핑: {unmapped}")


if __name__ == "__main__":
    main()
