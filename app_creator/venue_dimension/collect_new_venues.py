"""
복수 게시판/기간에서 크롤링 + 장소 추출 + 기존 dimension 매핑 후
미매핑(새 장소)만 합쳐서 Excel로 저장.

TARGETS 리스트에 (board_label, fldid, date_from, date_to) 추가하거나
기존 manual_review 파일 경로를 EXISTING_REVIEW_FILES 에 넣으면 재활용.
"""
import re
import io
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── CONFIG ───────────────────────────────────────────────────────────────────
GRPID = "1O7ju"

# 새로 크롤링할 대상
TARGETS = [
    # (board_label,       fldid,  date_from,     date_to)
    ("서울북부게시판", "IxV1", "2026-05-01", "2026-05-31"),
]

# 이미 만들어진 manual_review 파일 중 미매핑만 가져올 것
EXISTING_REVIEW_FILES = [
    Path(__file__).parent / "venues_manual_review_경기북부게시판_2026-04-15_2026-04-30.xlsx",
]

DIMENSION = Path(__file__).parent / "venues_final.xlsx"
OUTPUT    = Path(__file__).parent / "new_venues_to_review.xlsx"
MAX_PAGES = 20
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://cafe.daum.net/skfootball",
}

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
    "서울특별시": ["연세대", "불암", "성내", "은평", "인덕대", "중랑", "신내", "아차산",
                   "초안", "수도공고", "수도전기", "서울어린이", "용마", "강남세곡"],
    "하남시":   ["하남", "감일"],
    "김포시":   ["김포", "걸포"],
}


# ── 크롤링 ──────────────────────────────────────────────────────────────────

def _parse_pushes(raw: str, board_label: str) -> list[dict]:
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
                "dataid":       dm.group(1),
                "title":        json.loads(f'"{tm.group(1)}"'),
                "created":      created_dt.isoformat() if created_dt else None,
                "board_label":  board_label,
            })
    return result


def crawl(board_label: str, fldid: str, date_from: str, date_to: str) -> list[dict]:
    from_dt  = datetime.strptime(date_from, "%Y-%m-%d")
    to_dt    = datetime.strptime(date_to,   "%Y-%m-%d")
    base_url = f"https://cafe.daum.net/_c21_/bbs_list?grpid={GRPID}&fldid={fldid}"
    headers  = {**HEADERS, "Referer": f"https://cafe.daum.net/skfootball/{fldid}"}

    raw0      = requests.get(base_url, headers=headers).text
    all_posts = _parse_pushes(raw0, board_label)

    m_first = re.search(r"firstBbsDepth:\s*'([^']+)'", raw0)
    m_last  = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw0)
    if not m_first or not m_last:
        print(f"[{board_label}] 1페이지 파싱 실패")
        return []

    cur_first, cur_last, cur_page = m_first.group(1), m_last.group(1), 1
    print(f"[{board_label}] page 1 - {len(all_posts)}개")

    for _ in range(MAX_PAGES - 1):
        time.sleep(1)
        url = (
            f"https://cafe.daum.net/_c21_/bbs_list?grpid={GRPID}&fldid={fldid}"
            f"&page={cur_page+1}&prev_page={cur_page}&listnum=20"
            f"&firstbbsdepth={cur_first}&lastbbsdepth={cur_last}"
        )
        raw   = requests.get(url, headers=headers).text
        posts = _parse_pushes(raw, board_label)
        nf    = re.search(r"firstBbsDepth:\s*'([^']+)'", raw)
        nl    = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw)
        cur_page  += 1
        cur_first  = nf.group(1) if nf else None
        cur_last   = nl.group(1) if nl else None

        print(f"[{board_label}] page {cur_page} - {len(posts)}개")
        all_posts.extend(posts)

        if posts:
            latest = max(
                (datetime.fromisoformat(p["created"]) for p in posts if p["created"]),
                default=None,
            )
            if latest and latest < from_dt:
                print(f"  -> {from_dt.date()} 이전 도달, 수집 중단")
                break

        if not cur_first:
            break

    filtered = [
        p for p in all_posts
        if p["created"] and from_dt <= datetime.fromisoformat(p["created"]) <= to_dt
    ]
    seen, dedup = set(), []
    for p in filtered:
        if p["dataid"] not in seen:
            seen.add(p["dataid"])
            dedup.append(p)
    print(f"[{board_label}] {date_from}~{date_to}: {len(dedup)}개")
    return dedup


# ── 장소 추출 ────────────────────────────────────────────────────────────────

def extract_venue_candidate(title: str) -> str | None:
    t = title
    t = re.sub(r'\d+월\s*\d*일?', '', t)
    t = re.sub(r'\d+일', '', t)
    t = re.sub(r'\d+시\s*[~\-]\s*\d+시', '', t)
    t = re.sub(r'오전|오후', '', t)
    t = re.sub(r'\d+시', '', t)
    t = re.sub(r'월요일|화요일|수요일|목요일|금요일|토요일|일요일', '', t)
    t = re.sub(r'\s*\d+구장', '', t)
    for w in ['무료초청','매치초청','초청경기','초청매치','초청','신청합니다','신청바랍니다','신청',
              '경기모집','경기신청','경기','주말리그','주말','리그','구합니다','구인','모집합니다',
              '모집','합니다','입니다','안내','공지','친선','매칭','상대팀','상대','팀','쿼터','이상','무관']:
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
    for city, kws in CITY_KEYWORDS.items():
        for kw in kws:
            if kw in venue:
                return city
    return "미확인"


# ── dimension 매핑 ───────────────────────────────────────────────────────────

def build_matcher(dim_path: Path):
    df_dim = pd.read_excel(dim_path)
    df_dim = df_dim[
        df_dim["conflict_name"].notna() &
        (df_dim["conflict_name"].astype(str).str.strip() != "-")
    ]
    confirms = sorted(df_dim["venue_confirm"].dropna().astype(str).tolist(), key=len, reverse=True)
    mapping  = dict(zip(df_dim["venue_confirm"].astype(str), df_dim["conflict_name"].astype(str)))

    def match(candidate):
        if not candidate or pd.isna(candidate):
            return None
        for c in confirms:
            if c in candidate or candidate in c:
                return mapping[c]
        return None

    return match


# ── 메인 ────────────────────────────────────────────────────────────────────

def main():
    match = build_matcher(DIMENSION)
    all_unmapped = []

    # 1) 기존 manual_review 파일에서 미매핑만 추출
    for path in EXISTING_REVIEW_FILES:
        if not path.exists():
            print(f"파일 없음 (skip): {path.name}")
            continue
        df = pd.read_excel(path)
        unmapped = df[df["venue_confirm"].isna() | (df["venue_confirm"].astype(str).str.strip() == "")]
        unmapped = unmapped[["venue_candidate", "city"]].copy()
        unmapped["source"] = path.name
        all_unmapped.append(unmapped)
        print(f"{path.name}: 미매핑 {len(unmapped)}개")

    # 2) 새 게시판 크롤링 -> 장소 추출 -> 매핑 -> 미매핑만
    for board_label, fldid, date_from, date_to in TARGETS:
        print(f"\n[크롤링] {board_label} {date_from}~{date_to}")
        posts = crawl(board_label, fldid, date_from, date_to)
        if not posts:
            continue

        df_posts = pd.DataFrame(posts)
        df_posts["venue_candidate"] = df_posts["title"].apply(extract_venue_candidate)

        unique = (
            df_posts["venue_candidate"]
            .dropna().str.strip().replace("", None).dropna().unique()
        )
        df_venues = pd.DataFrame({"venue_candidate": sorted(unique)})
        df_venues["city"]          = df_venues["venue_candidate"].apply(guess_city)
        df_venues["venue_confirm"] = df_venues["venue_candidate"].apply(match)

        unmapped = df_venues[df_venues["venue_confirm"].isna()][["venue_candidate", "city"]].copy()
        unmapped["source"] = f"{board_label}_{date_from}_{date_to}"
        all_unmapped.append(unmapped)
        print(f"  unique 후보: {len(df_venues)}개 / 미매핑: {len(unmapped)}개")

    # 3) 합치기 + venue_candidate 중복 제거
    if not all_unmapped:
        print("\n미매핑 없음")
        return

    df_out = (
        pd.concat(all_unmapped, ignore_index=True)
        .drop_duplicates(subset="venue_candidate")
        .sort_values("venue_candidate")
        .reset_index(drop=True)
    )
    df_out["venue_confirm"] = ""  # 수동 입력란

    df_out.to_excel(OUTPUT, index=False)
    print(f"\n합계 새 장소: {len(df_out)}개")
    print(f"저장: {OUTPUT}")


if __name__ == "__main__":
    main()
