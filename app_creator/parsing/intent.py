"""게시글 제목에서 글의 의도(무엇을 원하는 글인지)와 마감 여부를 분류하는 모듈.

분류 체계 (4분류):
  - 상대구함: 구장을 가진 팀이 상대팀을 찾는 글 (초청합니다·상대 구합니다·매치초청 등)
  - 초청원함: 구장 없이 초대받길 원하는 글 (초청해주세요·어디든 가능 등)
  - 양도:     구장 예약 양도 글
  - 기타:     위 어디에도 해당하지 않는 글

마감 여부([마감]·(완료) 등)는 의도와 별개의 is_closed 플래그로 분리한다.
"""
import re

INTENT_HOSTING = "상대구함"
INTENT_SEEKING = "초청원함"
INTENT_TRANSFER = "양도"
INTENT_ETC = "기타"

# 초대받길 원하는 글 — "초청/초대" 뒤에 요청 표현이 붙는 경우
_SEEKING_RE = re.compile(
    r'초청\s*받|초대\s*받'
    r'|초[청대]\s*(?:부탁|원합|해\s*주|주세요|바랍)'
    r'|어디든|언제\s*어디든|불러\s*주'
)

# 구장 보유 팀이 상대를 찾는 글
_HOSTING_RE = re.compile(
    r'초청|초대'
    r'|상대\s*팀?\s*구|매칭\s*구|매치\s*구'
    r'|구합니다|구해요|모십니다|모셔요|모집'
)

_TRANSFER_RE = re.compile(r'양도')

_CLOSED_RE = re.compile(r'마감|완료')


def classify_intent(title: str) -> str:
    """제목의 의도를 상대구함/초청원함/양도/기타 중 하나로 분류한다."""
    if _TRANSFER_RE.search(title):
        return INTENT_TRANSFER
    if _SEEKING_RE.search(title):
        return INTENT_SEEKING
    if _HOSTING_RE.search(title):
        return INTENT_HOSTING
    return INTENT_ETC


def detect_closed(title: str) -> bool:
    """[마감]·(완료)·마감완료 등 마감 표시가 있으면 True."""
    return bool(_CLOSED_RE.search(title))
