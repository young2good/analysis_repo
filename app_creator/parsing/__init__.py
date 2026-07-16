"""게시글 파싱 패키지.

크롤링된 원본 게시글(제목)에서 파생 필드를 만들어내는 모듈 모음:
  - venue.py:          장소후보 추출 → 표준 장소명 매칭 → 도시 변환
  - datetime_parse.py: 경기 날짜·시간 추출
  - intent.py:         글 의도 분류(상대구함/초청원함/양도/기타) + 마감 여부

enrich(posts) 하나로 전체 파싱을 적용한다.
"""
from .venue import apply_mapping
from .datetime_parse import extract_date, extract_time
from .intent import classify_intent, detect_closed


def enrich(posts):
    """posts 각 항목에 파생 필드를 채워 반환한다.

    추가 필드: venue_candidate, std_name, city,
              match_date, match_time, intent, is_closed
    """
    posts = apply_mapping(posts)
    for p in posts:
        p["match_date"] = extract_date(p["title"])
        p["match_time"] = extract_time(p["title"])
        p["intent"] = classify_intent(p["title"])
        p["is_closed"] = detect_closed(p["title"])
    return posts
