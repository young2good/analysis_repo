import re
import json
import time
import requests
from datetime import datetime, date

import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────
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

VENUES_XLSX = r"e:\git-younghyun\analysis_repo\app_creator\venues_final.xlsx"

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

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]

# ──────────────────────────────────────────────
# 크롤링 함수
# ──────────────────────────────────────────────
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
                "created": created_dt,
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


def collect_posts(max_pages=15, date_from=None, date_to=None, progress_cb=None):
    from_dt = datetime.strptime(date_from, "%Y-%m-%d") if date_from else None
    to_dt   = datetime.strptime(date_to,   "%Y-%m-%d") if date_to   else None

    raw0 = requests.get(BASE_URL, headers=HEADERS).text
    all_posts = _parse_pushes(raw0)

    m_first = re.search(r"firstBbsDepth:\s*'([^']+)'", raw0)
    m_last  = re.search(r"lastBbsDepth:\s*'([^']+)'",  raw0)
    if not m_first or not m_last:
        return []

    cur_first = m_first.group(1)
    cur_last  = m_last.group(1)
    cur_page  = 1
    if progress_cb:
        progress_cb(1, max_pages, len(all_posts))

    for _ in range(max_pages - 1):
        time.sleep(0.8)
        posts, cur_page, cur_first, cur_last = _get_page(
            cur_page + 1, cur_page, cur_first, cur_last
        )
        all_posts.extend(posts)
        if progress_cb:
            progress_cb(cur_page, max_pages, len(all_posts))

        if from_dt and posts:
            latest = max((p["created"] for p in posts if p["created"]), default=None)
            if latest and latest < from_dt:
                break
        if not cur_first:
            break

    if from_dt or to_dt:
        all_posts = [
            p for p in all_posts
            if p["created"] is not None
            and (from_dt is None or p["created"] >= from_dt)
            and (to_dt   is None or p["created"] <= to_dt)
        ]

    return all_posts


# ──────────────────────────────────────────────
# 장소 추출 & 매핑 함수
# ──────────────────────────────────────────────
def extract_venue_candidate(title):
    text = title
    text = re.sub(r'\d+월\s*\d*일?', '', text)
    text = re.sub(r'\d+일', '', text)
    text = re.sub(r'\d+시\s*[~\-]\s*\d+시', '', text)
    text = re.sub(r'오전|오후', '', text)
    text = re.sub(r'\d+시', '', text)
    text = re.sub(r'월요일|화요일|수요일|목요일|금요일|토요일|일요일', '', text)
    text = re.sub(r'\s*\d+구장', '', text)
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
        text = text.replace(w, '')
    text = re.sub(r'\b[일월달]\b', '', text)
    text = re.sub(r'\b하{1,3}\b', '', text)
    text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None


@st.cache_data
def load_venue_lookup():
    try:
        df_v = pd.read_excel(VENUES_XLSX)
        df_v = df_v[df_v["conflict_name"].notna()].copy()
        df_v["std_name"] = df_v["conflict_name"].astype(str).str.strip()
        return {
            row["venue_confirm"]: row["std_name"]
            for _, row in df_v.iterrows()
            if pd.notna(row.get("venue_confirm"))
        }
    except Exception:
        return {}


def match_venue(candidate, sorted_confirms, confirm_map):
    if not candidate or pd.isna(candidate):
        return None, None
    for confirm in sorted_confirms:
        if confirm in candidate or candidate in confirm:
            std = confirm_map[confirm]
            city = VENUE_CITY.get(std)
            return std, city
    return None, None


def build_dataframe(posts):
    confirm_map = load_venue_lookup()
    sorted_confirms = sorted(confirm_map.keys(), key=len, reverse=True)

    records = []
    for p in posts:
        candidate = extract_venue_candidate(p["title"])
        std, city = match_venue(candidate, sorted_confirms, confirm_map)
        dt = p["created"]
        records.append({
            "날짜":     dt.strftime("%Y-%m-%d") if dt else "",
            "요일":     WEEKDAY_KR[dt.weekday()] if dt else "",
            "제목":     p["title"],
            "표준구장명": std or "",
            "시/구":    city or "",
            "_dataid": p["dataid"],
        })

    df = pd.DataFrame(records)
    return df


# ──────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="경기북부 주말축구 게시판",
    page_icon="⚽",
    layout="wide",
)

st.title("⚽ 경기북부 주말축구 게시판 뷰어")
st.caption("대상: [cafe.daum.net/skfootball/IxVG](https://cafe.daum.net/skfootball/IxVG)")

# ── 사이드바 ──────────────────────────────────
with st.sidebar:
    st.header("수집 설정")

    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        d_from = st.date_input("시작일", value=date(today.year, today.month, 1))
    with col2:
        d_to = st.date_input("종료일", value=today)

    max_pages = st.slider("최대 페이지 수", min_value=1, max_value=30, value=15)

    crawl_btn = st.button("🔍 게시글 수집", use_container_width=True, type="primary")

    st.divider()
    st.caption("페이지당 20개 · 페이지 간 0.8초 대기")

# ── 메인 영역 ─────────────────────────────────
if crawl_btn:
    prog_bar  = st.progress(0, text="수집 시작...")
    status_tx = st.empty()

    def on_progress(cur, total, cnt):
        pct = int(cur / total * 100)
        prog_bar.progress(pct, text=f"페이지 {cur}/{total} — 누적 {cnt}개")
        status_tx.text(f"페이지 {cur} 수집 중...")

    with st.spinner("크롤링 중..."):
        posts = collect_posts(
            max_pages=max_pages,
            date_from=str(d_from),
            date_to=str(d_to),
            progress_cb=on_progress,
        )

    prog_bar.empty()
    status_tx.empty()

    if not posts:
        st.warning("수집된 게시글이 없습니다.")
        st.stop()

    df = build_dataframe(posts)
    st.session_state["df"] = df
    st.session_state["period"] = f"{d_from} ~ {d_to}"

if "df" not in st.session_state:
    st.info("왼쪽 사이드바에서 날짜 범위를 설정하고 **게시글 수집** 버튼을 눌러주세요.")
    st.stop()

df: pd.DataFrame = st.session_state["df"]

# ── 요약 지표 ──────────────────────────────────
total     = len(df)
mapped    = (df["시/구"] != "").sum()
unmapped  = total - mapped
map_rate  = mapped / total * 100 if total else 0

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("기간", st.session_state["period"])
col_b.metric("총 게시글", f"{total}개")
col_c.metric("구장 매핑", f"{mapped}개 ({map_rate:.0f}%)")
col_d.metric("미매핑", f"{unmapped}개")

st.divider()

# ── 필터 ───────────────────────────────────────
with st.expander("필터", expanded=False):
    cities = sorted(df["시/구"].replace("", "미매핑").unique().tolist())
    sel_cities = st.multiselect("시/구 필터", options=cities, default=cities)
    keyword = st.text_input("제목 키워드 검색")

view = df.copy()
view["시/구_disp"] = view["시/구"].replace("", "미매핑")
view = view[view["시/구_disp"].isin(sel_cities)]
if keyword:
    view = view[view["제목"].str.contains(keyword, na=False)]

# ── 시/구 분포 차트 ────────────────────────────
city_counts = (
    view["시/구_disp"]
    .value_counts()
    .reset_index()
    .rename(columns={"시/구_disp": "시/구", "count": "게시글 수"})
)
st.subheader(f"시/구별 게시글 수  ·  {len(view)}건")
st.bar_chart(city_counts.set_index("시/구")["게시글 수"])

st.divider()

# ── 게시글 목록 테이블 ──────────────────────────
st.subheader("게시글 목록")

display_cols = ["날짜", "요일", "제목", "표준구장명", "시/구"]
st.dataframe(
    view[display_cols].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config={
        "날짜":     st.column_config.TextColumn("날짜",     width=100),
        "요일":     st.column_config.TextColumn("요일",     width=50),
        "제목":     st.column_config.TextColumn("제목",     width=None),
        "표준구장명": st.column_config.TextColumn("표준구장명", width=220),
        "시/구":    st.column_config.TextColumn("시/구",    width=100),
    },
)

# ── 다운로드 ───────────────────────────────────
csv = view[display_cols].to_csv(index=False, encoding="utf-8-sig")
st.download_button(
    label="CSV 다운로드",
    data=csv,
    file_name=f"cafe_posts_{st.session_state['period'].replace(' ', '').replace('~', '_')}.csv",
    mime="text/csv",
)
