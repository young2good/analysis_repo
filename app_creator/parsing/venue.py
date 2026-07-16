"""게시글 제목에서 장소를 추출해 표준 장소명·도시로 매핑하는 모듈.

parse_posts.py 파이프라인에서 사용한다.
표준 장소명 사전은 venue_dimension/venues_final.xlsx에서 읽는다.
"""
import re
from pathlib import Path

import pandas as pd

VENUES_XLSX = Path(__file__).resolve().parent.parent / "venue_dimension" / "venues_final.xlsx"

# 표준 장소명 → 도시
VENUE_CITY = {
    "YMCA 축구장":                              "고양시",
    "감일축구장":                                "하남시",
    "강남세곡체육공원축구장":                     "서울특별시",
    "걸포중앙공원축구장":                         "김포시",
    "경민대학교대운동장":                         "의정부시",
    "경복대학교 남양주캠퍼스운동장":              "남양주시",
    "고양고등학교운동장":                         "고양시",
    "교하체육공원 인조잔디축구장":                "파주시",
    "구리시민스포츠센터축구장":                   "구리시",
    "구리왕숙체육공원 축구장":                    "구리시",
    "금남축구장":                                "남양주시",
    "김포시종합운동장":                           "김포시",
    "남양주체육문화센터(종합운동장)메인스타디움":  "남양주시",
    "남양주체육문화센터(종합운동장)축구장 A구장":  "남양주시",
    "남양주체육문화센터(종합운동장)축구장 B구장":  "남양주시",
    "남양주체육문화센터(종합운동장)축구장 C구장":  "남양주시",
    "농협대학교운동장":                           "고양시",
    "다락원체육공원축구장":                       "의정부시",
    "다산체육공원 축구장":                        "남양주시",
    "대화동레포츠공원인조잔디축구장":             "고양시",
    "둔치축구":                                   "고양시",
    "먹골구장":                                  "남양주시",
    "문원체육공원운동장":                         "과천시",
    "불암산스포츠타운축구장":                     "서울특별시",
    "서울어린이대공원잔디축구장":                 "서울특별시",
    "성내유수지축구장":                           "서울특별시",
    "수도전기공업고등학교축구장":                 "서울특별시",
    "신내차량기지축구장":                         "서울특별시",
    "아차산배수지체육공원축구장":                 "서울특별시",
    "연세대학교 신촌캠퍼스대운동장":              "서울특별시",
    "와부공설운동장":                             "남양주시",
    "용마폭포공원축구장":                         "서울특별시",
    "운정건강공원(가온) 인조잔디축구장":           "파주시",
    "원능수질복원센터":                           "파주시",
    "은평구립축구장":                             "서울특별시",
    "인덕대학교운동장":                           "서울특별시",
    "진건푸른물센터인조잔디구장":                 "남양주시",
    "중랑구립잔디운동장":                         "서울특별시",
    "지금푸른물센터축구장":                       "구리시",
    "지영체육공원축구장":                         "고양시",
    "직동근린공원축구장":                         "의정부시",
    "초안산스포츠타운축구장":                     "서울특별시",
    "충장근린체육공원축구장":                     "고양시",
    "파주스타디움보조경기장":                     "파주시",
    "하남종합운동장 주경기장":                    "하남시",
    "하남종합운동장보조경기장":                   "하남시",
    "한국항공대학교운동장":                       "고양시",
    "활기체육공원축구장":                         "의정부시",
}

STOPWORDS = [
    '무료초청', '매치초청', '초청경기', '초청매치', '초청',
    '신청합니다', '신청바랍니다', '신청',
    '경기모집', '경기신청', '경기',
    '주말리그', '주말', '리그',
    '구합니다', '구인', '모집합니다', '모집',
    '합니다', '입니다', '안내', '공지', '친선', '매칭',
    '상대팀', '상대', '팀', '쿼터', '이상', '무관',
]


def load_venue_lookup():
    """표기 변형(venue_confirm) → 표준 장소명(conflict_name) 사전을 반환한다."""
    df_v = pd.read_excel(VENUES_XLSX)
    df_v = df_v[df_v["conflict_name"].notna()].copy()
    df_v["std_name"] = df_v["conflict_name"].astype(str).str.strip()
    return {
        row["venue_confirm"]: row["std_name"]
        for _, row in df_v.iterrows()
        if pd.notna(row.get("venue_confirm"))
    }


def extract_venue_candidate(title):
    """제목에서 날짜·시간·요일·모집 상투어를 제거해 장소 후보 텍스트만 남긴다."""
    text = title
    text = re.sub(r'\d+월\s*\d*일?', '', text)
    text = re.sub(r'\d+일', '', text)
    text = re.sub(r'\d+시\s*[~\-]\s*\d+시', '', text)
    text = re.sub(r'오전|오후', '', text)
    text = re.sub(r'\d+시', '', text)
    text = re.sub(r'월요일|화요일|수요일|목요일|금요일|토요일|일요일', '', text)
    text = re.sub(r'\s*\d+구장', '', text)
    for w in STOPWORDS:
        text = text.replace(w, '')
    text = re.sub(r'\b[일월달]\b', '', text)
    text = re.sub(r'\b하{1,3}\b', '', text)
    text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None


def match_venue(candidate, sorted_confirms, confirm_map):
    """장소 후보 텍스트를 사전과 양방향 부분일치로 매칭한다. (표준명, 도시) 반환."""
    if not candidate:
        return None, None
    for confirm in sorted_confirms:
        if confirm in candidate or candidate in confirm:
            std = confirm_map[confirm]
            return std, VENUE_CITY.get(std)
    return None, None


def apply_mapping(posts):
    """posts 각 항목에 venue_candidate / std_name / city 필드를 채워 반환한다."""
    confirm_map = load_venue_lookup()
    sorted_confirms = sorted(confirm_map.keys(), key=len, reverse=True)

    for p in posts:
        candidate = extract_venue_candidate(p["title"])
        std, city = match_venue(candidate, sorted_confirms, confirm_map)
        p["venue_candidate"] = candidate
        p["std_name"] = std
        p["city"] = city
    return posts
