"""posts_raw.json을 읽어 파싱을 적용하고 posts_temp.json으로 저장한다.

python parse_posts.py

크롤링 없이 파싱만 다시 수행하므로, parsing/ 모듈(장소 매핑·날짜·시간·의도 분류)을
수정한 뒤 빠르게 재실행할 수 있다. 크롤링은 crawl_posts.py에서 수행한다.
"""
import json
from collections import Counter
from pathlib import Path

import parsing

BASE_DIR = Path(__file__).resolve().parent
RAW_JSON = BASE_DIR / "posts_raw.json"
OUTPUT_JSON = BASE_DIR / "posts_temp.json"


def main():
    with open(RAW_JSON, encoding="utf-8") as f:
        posts = json.load(f)

    posts = parsing.enrich(posts)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    goyang = sum(1 for p in posts if p["city"] == "고양시")
    unmapped = sum(1 for p in posts if not p["std_name"])
    closed = sum(1 for p in posts if p["is_closed"])
    intents = Counter(p["intent"] for p in posts)

    print(f"saved: {OUTPUT_JSON}")
    print(f"total: {len(posts)} / 고양시: {goyang} / 미매핑: {unmapped} / 마감: {closed}")
    print("의도 분류:", dict(intents))


if __name__ == "__main__":
    main()
