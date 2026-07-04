"""
다음 카페 게시글을 크롤링해서 JSON 파일로 저장하는 일회성 스크립트.
python save_posts.py
"""
import re
import json
import time
import requests
from datetime import datetime
from pathlib import Path

import pandas as pd

GRPID = "1O7ju"
FLDID = "IxVG"
BASE_URL = f"https://cafe.daum.net/_c21_/bbs_list?grpid={GRPID}&fldid={FLDID}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": f"https://cafe.daum.net/skfootball/{FLDID}",
}

# 스크립트 위치 기준 상대 경로 (analysis_repo가 어디에 있든 동작)
APP_CREATOR_DIR = Path(__file__).resolve().parent.parent
VENUES_XLSX = APP_CREATOR_DIR / "venue_dimension" / "venues_final.xlsx"
OUTPUT_JSON = APP_CREATOR_DIR / "posts_temp.json"

# 크롤링 조건 (필요시 여기만 수정)
DATE_FROM = "2026-07-01"
DATE_TO   = "2026-07-30"
MAX_PAGES = 15

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


def _parse_pushes(raw):
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
                "title":   json.loads(f'"{ tm.group(1)}"'),
                "created": created_dt.strftime("%Y-%m-%d") if created_dt else None,
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


def collect_posts(max_pages=MAX_PAGES, date_from=DATE_FROM, date_to=DATE_TO):
    from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    to_dt   = datetime.strptime(date_to,   "%Y-%m-%d")

    raw0 = requests.get(BASE_URL, headers=HEADERS).text
    all_posts = _parse_pushes(raw0)
    print(f"page 1: {len(all_posts)}")

    m_first = re.search(r"firstBbsDepth:\s*'([^']+)'", raw0)
    m_last  = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw0)
    if not m_first or not m_last:
        print("파싱 실패")
        return []

    cur_first = m_first.group(1)
    cur_last  = m_last.group(1)
    cur_page  = 1

    for _ in range(max_pages - 1):
        time.sleep(0.8)
        posts, cur_page, cur_first, cur_last = _get_page(
            cur_page + 1, cur_page, cur_first, cur_last
        )
        print(f"page {cur_page}: {len(posts)}")
        all_posts.extend(posts)

        if posts:
            dates = [datetime.strptime(p["created"], "%Y-%m-%d") for p in posts if p["created"]]
            if dates and max(dates) < from_dt:
                print("  stop: out of date range")
                break
        if not cur_first:
            break

    filtered = [
        p for p in all_posts
        if p["created"]
        and from_dt <= datetime.strptime(p["created"], "%Y-%m-%d") <= to_dt
    ]
    print(f"total: {len(all_posts)}, filtered: {len(filtered)}")
    return filtered


def load_venue_lookup():
    df_v = pd.read_excel(VENUES_XLSX)
    df_v = df_v[df_v["conflict_name"].notna()].copy()
    df_v["std_name"] = df_v["conflict_name"].astype(str).str.strip()
    return {
        row["venue_confirm"]: row["std_name"]
        for _, row in df_v.iterrows()
        if pd.notna(row.get("venue_confirm"))
    }


def extract_venue_candidate(title):
    text = title
    text = re.sub(r'\d+월\s*\d*일?', '', text)
    text = re.sub(r'\d+일', '', text)
    text = re.sub(r'\d+시\s*[~\-]\s*\d+시', '', text)
    text = re.sub(r'오전|오후', '', text)
    text = re.sub(r'\d+시', '', text)
    text = re.sub(r'월요일|화요일|수요일|목요일|금요일|토요일|일요일', '', text)
    text = re.sub(r'\s*\d+구장', '', text)
    for w in ['무료초청','매치초청','초청경기','초청매치','초청','신청합니다','신청바랍니다','신청',
              '경기모집','경기신청','경기','주말리그','주말','리그','구합니다','구인',
              '모집합니다','모집','합니다','입니다','안내','공지','친선','매칭',
              '상대팀','상대','팀','쿼터','이상','무관']:
        text = text.replace(w, '')
    text = re.sub(r'\b[일월달]\b', '', text)
    text = re.sub(r'\b하{1,3}\b', '', text)
    text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None


def apply_mapping(posts):
    confirm_map = load_venue_lookup()
    sorted_confirms = sorted(confirm_map.keys(), key=len, reverse=True)

    for p in posts:
        candidate = extract_venue_candidate(p["title"])
        p["venue_candidate"] = candidate
        p["std_name"] = None
        p["city"] = None
        if candidate:
            for confirm in sorted_confirms:
                if confirm in candidate or candidate in confirm:
                    std = confirm_map[confirm]
                    p["std_name"] = std
                    p["city"] = VENUE_CITY.get(std)
                    break
    return posts


if __name__ == "__main__":
    posts = collect_posts()
    posts = apply_mapping(posts)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    goyang = sum(1 for p in posts if p['city'] == '고양시')
    print(f"saved: {OUTPUT_JSON}")
    print(f"goyang: {goyang}")
