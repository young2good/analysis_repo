"""네이버 카페 크롤러 — Step 2에서 구현 예정.

daum_cafe와 동일한 공통 스키마를 반환해야 한다:
    {"source": "naver_cafe", "dataid": str, "title": str,
     "created": "YYYY-MM-DD", "url": str}

구현 시 결정할 것:
  - 대상 카페/게시판 (clubid, menuid)
  - 공개 게시판 여부 (비공개면 로그인 세션 필요)
"""
SOURCE = "naver_cafe"


def collect_posts(max_pages=15, date_from=None, date_to=None, progress_cb=None):
    raise NotImplementedError("네이버 카페 크롤러는 아직 구현되지 않았습니다.")
