"""게시글 크롤러 모음.

각 크롤러 모듈은 다음을 제공해야 한다:
  - SOURCE: 출처 식별자 문자열
  - collect_posts(max_pages, date_from, date_to, progress_cb) -> list[dict]
    반환 스키마: {"source", "dataid", "title", "created"(YYYY-MM-DD), "url"}
"""
