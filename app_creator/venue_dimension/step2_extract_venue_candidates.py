"""
Step 2 — 장소 후보 추출
step1 결과 JSON에서 장소로 추정되는 키워드를 뽑아 Excel로 저장.
venue_confirm 컬럼을 수동으로 채우면 Step 3 완료.

사용법:
    python step2_extract_venue_candidates.py
아래 CONFIG 블록만 수정하면 됨 (step1과 동일하게 맞출 것).
"""
import re
import json
from pathlib import Path

import pandas as pd

# ── CONFIG ───────────────────────────────────────────────────────────────────
BOARD_LABEL = "경기북부게시판"
DATE_FROM   = "2026-04-15"
DATE_TO     = "2026-04-30"
# ─────────────────────────────────────────────────────────────────────────────

BASE   = Path(__file__).parent
INPUT  = BASE / "data" / f"raw_posts_{BOARD_LABEL}_{DATE_FROM}_{DATE_TO}.json"
OUTPUT = BASE / f"venues_manual_review_{BOARD_LABEL}_{DATE_FROM}_{DATE_TO}.xlsx"

CITY_KEYWORDS = {
    "남양주시": ["남양주", "다산", "별내", "진접", "오남", "화도", "퇴계원", "와부", "진건"],
    "고양시":   ["일산", "탄현", "능곡", "화정", "행신", "풍산", "장항", "대화", "백석",
                 "마두", "주엽", "정발산", "원흥", "삼송", "지축", "향동", "고양", "덕양",
                 "강매", "현천", "토당", "화전", "충장"],
    "파주시":   ["운정", "교하", "야당", "금촌", "문산", "파주", "원능", "원릉",
                 "조리", "월롱", "법원", "광탄"],
    "의정부시": ["직동", "의정부", "호원", "장암", "신곡", "가능", "녹양", "민락",
                 "고산", "용현", "흥선", "금오", "낙양", "경민대", "활기"],
    "양주시":   ["양주", "덕계", "덕정", "회천", "옥정", "고읍", "고덕"],
    "포천시":   ["포천", "소흘", "군내", "가산", "신북"],
    "동두천시": ["동두천", "지행", "소요", "생연", "보산"],
    "구리시":   ["구리", "인창", "갈매", "교문", "수택", "왕숙"],
    "가평군":   ["가평", "청평"],
    "연천군":   ["연천", "전곡"],
}


def extract_venue_candidate(title: str) -> str | None:
    t = title
    t = re.sub(r'\d+월\s*\d*일?', '', t)
    t = re.sub(r'\d+일', '', t)
    t = re.sub(r'\d+시\s*[~\-]\s*\d+시', '', t)
    t = re.sub(r'오전|오후', '', t)
    t = re.sub(r'\d+시', '', t)
    t = re.sub(r'월요일|화요일|수요일|목요일|금요일|토요일|일요일', '', t)
    t = re.sub(r'\s*\d+구장', '', t)

    stopwords = [
        '무료초청', '매치초청', '초청경기', '초청매치', '초청',
        '신청합니다', '신청바랍니다', '신청',
        '경기모집', '경기신청', '경기',
        '주말리그', '주말', '리그',
        '구합니다', '구인', '모집합니다', '모집',
        '합니다', '입니다', '안내', '공지', '친선', '매칭',
        '상대팀', '상대', '팀', '쿼터', '이상', '무관',
    ]
    for w in stopwords:
        t = t.replace(w, '')

    t = re.sub(r'\b[일월달]\b', '', t)
    t = re.sub(r'\b하{1,3}\b', '', t)
    t = re.sub(r'[^\w\s]', ' ', t, flags=re.UNICODE)
    t = re.sub(r'\d+', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t if t else None


def guess_city(venue: str) -> str:
    if not venue:
        return "미확인"
    for city, keywords in CITY_KEYWORDS.items():
        for kw in keywords:
            if kw in venue:
                return city
    return "미확인"


def main():
    posts = json.loads(INPUT.read_text(encoding="utf-8"))
    df = pd.DataFrame(posts)
    print(f"입력 포스트: {len(df)}개")

    df["venue_candidate"] = df["title"].apply(extract_venue_candidate)

    unique_candidates = (
        df["venue_candidate"]
        .dropna()
        .str.strip()
        .replace("", None)
        .dropna()
        .unique()
    )

    df_out = pd.DataFrame({"venue_candidate": sorted(unique_candidates)})
    df_out["city"]          = df_out["venue_candidate"].apply(guess_city)
    df_out["venue_confirm"] = ""   # ← Step 3: 수동으로 공식 장소명 입력

    df_out.to_excel(OUTPUT, index=False)
    print(f"저장: {OUTPUT}")
    print(f"unique 후보: {len(df_out)}개  (자동매핑: {(df_out['city'] != '미확인').sum()}개, 미확인: {(df_out['city'] == '미확인').sum()}개)")
    print(f"\n※ {OUTPUT.name} 의 venue_confirm 컬럼을 채운 뒤 step4를 실행하세요.")


if __name__ == "__main__":
    main()
