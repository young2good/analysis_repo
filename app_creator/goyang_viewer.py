"""파싱이 끝난 posts_temp.json을 읽어 화면에 보여주는 순수 뷰어.

데이터 생성 파이프라인: crawl_posts.py(크롤링) → parse_posts.py(파싱) → posts_temp.json
상단 "데이터 업데이트" 버튼으로 위 파이프라인을 화면에서 직접 실행할 수 있다.
"""
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
import altair as alt
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
POSTS_JSON = BASE_DIR / "posts_temp.json"
GEOJSON_URL = (
    "https://raw.githubusercontent.com/southkorea/southkorea-maps"
    "/master/kostat/2013/json/skorea_municipalities_geo_simple.json"
)

# 카테고리(글 구분) 태그에 순서대로 배정하는 고정 색상 슬롯 (최대 8개, 이후는 마지막 슬롯 재사용)
CATEGORICAL_SLOTS = 8


def parse_match_date(md, created) -> date | None:
    """'M/D' 문자열을 게시일(created) 연도 기준 date로 변환. 실패 시 None."""
    try:
        m, d = str(md).split("/")
        return date(int(str(created)[:4]), int(m), int(d))
    except (ValueError, AttributeError):
        return None


def intent_badge_class(intent: str, ordered_intents: list) -> str:
    idx = ordered_intents.index(intent) if intent in ordered_intents else CATEGORICAL_SLOTS - 1
    return f"badge-cat-{idx % CATEGORICAL_SLOTS + 1}"


APP_CSS = """
<style>
:root {
  --surface-1:      #ffffff;
  --page-plane:     #f4f6f5;
  --text-primary:   #101c14;
  --text-secondary: #46554b;
  --text-muted:     #84928a;
  --border:         rgba(16,40,24,0.12);
  --pitch:          #1baf7a;   /* 피치 그린 */
  --pitch-deep:     #0e8a5e;
  --pitch-soft:     rgba(27,175,122,0.12);
  --hero-bg-1:      #0d1f16;
  --hero-bg-2:      #143528;
  --hero-text:      #f2fbf6;
  --cat-1: #1baf7a; --cat-2: #2a78d6; --cat-3: #eb6834; --cat-4: #eda100;
  --cat-5: #e87ba4; --cat-6: #4a3aa7; --cat-7: #008300; --cat-8: #e34948;
}
@media (prefers-color-scheme: dark) {
  :root {
    --surface-1:      #16211b;
    --page-plane:     #0c120e;
    --text-primary:   #edf7f1;
    --text-secondary: #b3c4ba;
    --text-muted:     #84928a;
    --border:         rgba(220,255,235,0.12);
    --pitch:          #22c98d;
    --pitch-deep:     #1baf7a;
    --pitch-soft:     rgba(34,201,141,0.14);
    --hero-bg-1:      #0a1810;
    --hero-bg-2:      #10281d;
    --hero-text:      #f2fbf6;
    --cat-1: #199e70; --cat-2: #3987e5; --cat-3: #d95926; --cat-4: #c98500;
    --cat-5: #d55181; --cat-6: #9085e9; --cat-7: #008300; --cat-8: #e66767;
  }
}

.block-container { padding-top: 2.2rem; max-width: 980px; }

/* ── 히어로 ── */
.app-hero {
  background: linear-gradient(120deg, var(--hero-bg-1), var(--hero-bg-2));
  border-radius: 20px; padding: 24px 28px; margin-bottom: 1.2rem;
  position: relative; overflow: hidden;
}
.app-hero::after {
  content: "⚽"; position: absolute; right: 18px; bottom: -14px;
  font-size: 5.2rem; opacity: .12; transform: rotate(-12deg);
}
.hero-eyebrow {
  display: inline-block; font-size: .72rem; font-weight: 800; letter-spacing: .14em;
  color: var(--pitch); text-transform: uppercase; margin-bottom: .3rem;
}
.hero-title { font-size: 1.6rem; font-weight: 900; color: var(--hero-text); line-height: 1.25; }
.hero-title .hl { color: var(--pitch); }
.hero-sub { color: rgba(242,251,246,.72); font-size: .9rem; margin-top: .35rem; }

/* ── KPI 칩 ── */
.kpi-row { display: flex; gap: 10px; margin: .2rem 0 1.2rem; }
.kpi-card {
  flex: 1; display: flex; align-items: baseline; gap: .5rem;
  background: var(--surface-1); border: 1px solid var(--border);
  border-radius: 12px; padding: 10px 16px;
}
.kpi-value { font-size: 1.3rem; font-weight: 900; color: var(--pitch-deep); font-variant-numeric: tabular-nums; }
.kpi-label { font-size: .8rem; font-weight: 600; color: var(--text-secondary); }

/* ── 날짜 그룹 헤더 ── */
.day-header {
  display: flex; align-items: center; gap: .55rem;
  margin: 1.3rem 0 .55rem; font-size: 1.02rem; font-weight: 800; color: var(--text-primary);
}
.day-header .day-chip {
  font-size: .7rem; font-weight: 800; color: #fff; background: var(--pitch);
  padding: 2px 8px; border-radius: 999px; letter-spacing: .04em;
}
.day-header .day-count { font-size: .8rem; font-weight: 600; color: var(--text-muted); }

/* ── 매치 카드 ── */
.match-list { display: flex; flex-direction: column; gap: 8px; }
.match-card {
  display: flex; align-items: stretch; gap: 14px;
  background: var(--surface-1); border: 1px solid var(--border);
  border-radius: 14px; padding: 12px 16px; text-decoration: none;
  transition: transform .08s ease, box-shadow .08s ease, border-color .08s ease;
}
.match-card:hover {
  transform: translateY(-1px); box-shadow: 0 5px 14px rgba(14,138,94,.12);
  border-color: color-mix(in srgb, var(--pitch) 55%, var(--border));
  text-decoration: none;
}
.match-card.closed { opacity: .5; }
.mc-time {
  flex: 0 0 84px; display: flex; flex-direction: column; justify-content: center;
  border-right: 2px solid var(--pitch-soft); padding-right: 12px;
}
.mc-time .t { font-size: 1.02rem; font-weight: 900; color: var(--pitch-deep); font-variant-numeric: tabular-nums; }
.mc-time .t.tbd { color: var(--text-muted); font-size: .86rem; font-weight: 700; }
.mc-body { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: 3px; }
.mc-venue { font-size: .98rem; font-weight: 800; color: var(--text-primary); }
.mc-venue.tbd { color: var(--text-muted); font-weight: 600; }
.match-card.closed .mc-venue { text-decoration: line-through; }
.mc-title {
  font-size: .8rem; color: var(--text-secondary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.mc-side {
  display: flex; flex-direction: column; align-items: flex-end; justify-content: center;
  gap: 5px; flex-shrink: 0;
}
.mc-src { font-size: .72rem; color: var(--text-muted); }

.badge {
  display: inline-block; font-size: 11px; font-weight: 800;
  padding: 2px 9px; border-radius: 999px; white-space: nowrap;
}
.badge-open { background: var(--pitch); color: #fff; }
.badge-closed { background: var(--page-plane); color: var(--text-muted); border: 1px solid var(--border); }
.badge-cat-1 { background: color-mix(in srgb, var(--cat-1) 15%, transparent); color: var(--cat-1); }
.badge-cat-2 { background: color-mix(in srgb, var(--cat-2) 15%, transparent); color: var(--cat-2); }
.badge-cat-3 { background: color-mix(in srgb, var(--cat-3) 15%, transparent); color: var(--cat-3); }
.badge-cat-4 { background: color-mix(in srgb, var(--cat-4) 20%, transparent); color: var(--cat-4); }
.badge-cat-5 { background: color-mix(in srgb, var(--cat-5) 20%, transparent); color: var(--cat-5); }
.badge-cat-6 { background: color-mix(in srgb, var(--cat-6) 15%, transparent); color: var(--cat-6); }
.badge-cat-7 { background: color-mix(in srgb, var(--cat-7) 15%, transparent); color: var(--cat-7); }
.badge-cat-8 { background: color-mix(in srgb, var(--cat-8) 15%, transparent); color: var(--cat-8); }

.empty-note {
  text-align: center; color: var(--text-muted); padding: 2.2rem 0;
  background: var(--surface-1); border: 1px dashed var(--border); border-radius: 14px;
}
</style>
"""

## 지도부분 일단 hide (6/30)
# ── 지도 ────────────────────────────────────────
# @st.cache_resource(show_spinner="지도 데이터 로딩 중...")
# def load_sudogwon_fc():
#     """수도권 GeoJSON FeatureCollection 반환 (필터 + highlight 속성 추가)"""
#     SIDO_CODE = {"11": "서울", "23": "인천", "31": "경기"}
#     EXCLUDE   = {"옹진군", "강화군"}
#     geojson   = requests.get(GEOJSON_URL, timeout=15).json()

#     features = []
#     for f in geojson["features"]:
#         code = f["properties"]["code"]
#         name = f["properties"]["name"]
#         if code[:2] not in SIDO_CODE or name in EXCLUDE:
#             continue
#         features.append({
#             "type": "Feature",
#             "properties": {
#                 "name":      name,
#                 "sido":      SIDO_CODE[code[:2]],
#                 "highlight": "고양시" if "고양" in name else "기타",
#             },
#             "geometry": f["geometry"],
#         })
#     return {"type": "FeatureCollection", "features": features}

## 지도부분 일단 hide (6/30)
# def make_map(fc: dict) -> alt.Chart:
#     # InlineData + format=json 으로 Altair에 GeoJSON을 직접 전달 (Arrow 변환 우회)
#     data = alt.InlineData(
#         values=fc,
#         format=alt.DataFormat(property="features", type="json"),
#     )
#     return (
#         alt.Chart(data)
#         .mark_geoshape(stroke="white", strokeWidth=0.6)
#         .encode(
#             color=alt.Color(
#                 "properties.highlight:N",
#                 scale=alt.Scale(
#                     domain=["고양시", "기타"],
#                     range=["#F78535", "#D9EFEE"],
#                 ),
#                 legend=None,
#             ),
#             tooltip=[
#                 alt.Tooltip("properties.name:N", title="지역"),
#                 alt.Tooltip("properties.sido:N", title="시도"),
#             ],
#         )
#         .project("mercator")
#         .properties(height=300, title="수도권 — 고양시 위치")
#         .configure_view(stroke=None)
#         .configure_title(fontSize=13, color="#555")
#     )


# ── 매치 카드 리스트 (경기 날짜별 그룹핑) ────────
WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]


def day_header_label(dt: date | None, today: date) -> str:
    if dt is None:
        return "📌 날짜 미정"
    label = f"{dt.month}월 {dt.day}일 {WEEKDAY_KO[dt.weekday()]}요일"
    if dt == today:
        label += ' <span class="day-chip">오늘</span>'
    elif dt == today + timedelta(days=1):
        label += ' <span class="day-chip">내일</span>'
    return label


def build_match_card(r: pd.Series, ordered_intents: list) -> str:
    url    = r["url"]
    title  = r["title"].replace("<", "&lt;").replace(">", "&gt;")
    closed = bool(r.get("is_closed"))

    time_txt  = str(r["시간"]).strip()
    place_txt = str(r["std_name"] or "").strip()
    time_html  = (
        f'<span class="t">{time_txt}</span>' if time_txt
        else '<span class="t tbd">시간 미정</span>'
    )
    venue_html = (
        f'<div class="mc-venue">{place_txt}</div>' if place_txt
        else '<div class="mc-venue tbd">장소 미정</div>'
    )

    intent = r.get("intent") or ""
    badges = (
        f'<span class="badge {intent_badge_class(intent, ordered_intents)}">{intent}</span>'
        if intent else ""
    )
    badges += (
        ' <span class="badge badge-closed">마감</span>' if closed
        else ' <span class="badge badge-open">모집중</span>'
    )

    return f"""
    <a class="match-card{' closed' if closed else ''}" href="{url}" target="_blank">
      <div class="mc-time">{time_html}</div>
      <div class="mc-body">
        {venue_html}
        <div class="mc-title">{title}</div>
      </div>
      <div class="mc-side">
        <div>{badges}</div>
        <div class="mc-src">{r["source"]}</div>
      </div>
    </a>"""


def build_match_list(df: pd.DataFrame, ordered_intents: list, today: date) -> str:
    if df.empty:
        return '<div class="empty-note">🔍 조건에 맞는 경기가 없어요. 필터를 넓혀보세요!</div>'

    # 경기 날짜 오름차순, 날짜 미정은 마지막 그룹으로
    df = df.copy()
    df["_grp"] = df["match_dt"].apply(lambda d: d if isinstance(d, date) else None)
    df["_ord"] = df["_grp"].apply(lambda d: d if d else date.max)
    df = df.sort_values(["_ord", "시간"])

    html = ""
    for grp_dt, grp in df.groupby("_grp", dropna=False, sort=False):
        grp_dt = grp_dt if isinstance(grp_dt, date) else None
        cards = "".join(build_match_card(r, ordered_intents) for _, r in grp.iterrows())
        html += f"""
        <div class="day-header">{day_header_label(grp_dt, today)}
          <span class="day-count">{len(grp)}건</span>
        </div>
        <div class="match-list">{cards}</div>"""
    return html


# ── 데이터 업데이트 ─────────────────────────────
def run_script(name: str, *args: str) -> str:
    """crawl_posts.py / parse_posts.py를 별도 프로세스로 실행하고 stdout을 반환한다."""
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=BASE_DIR,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


# ── UI ─────────────────────────────────────────
st.set_page_config(page_title="고양 매치", page_icon="⚽", layout="wide")
st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(
    """
    <div class="app-hero">
      <div class="hero-eyebrow">GOYANG MATCH</div>
      <div class="hero-title">오늘 뛰고 싶다면,<br><span class="hl">고양 매치</span>에서 찾으세요</div>
      <div class="hero-sub">고양시 축구 매칭·양도·초청 경기를 한곳에서</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_btn, col_from, col_mtime = st.columns([1, 1, 2], vertical_alignment="center")
with col_btn:
    update_clicked = st.button("🔄 데이터 업데이트", help="크롤링 → 파싱 순서로 실행 후 화면을 갱신합니다")
with col_from:
    today = date.today()
    crawl_from = st.date_input(
        "수집 시작일 (작성일 기준, 오늘까지 수집)",
        value=today.replace(day=1),
        max_value=today,
        help="이 날짜부터 오늘까지 '작성된' 게시글을 수집합니다. "
             "제목에 적힌 경기 날짜와는 무관하며, 경기 날짜는 아래 상세 필터의 달력으로 조회하세요.",
    )
with col_mtime:
    mtime_slot = st.empty()  # 업데이트 완료 후 최신 시각으로 채우기 위해 자리만 확보

crawl_to = today

if update_clicked:
    # 오래된 기간일수록 목록 페이지를 더 내려가야 함 — 하루 약 0.5페이지로 추정 + 여유분
    crawl_pages = max(15, (today - crawl_from).days // 2 + 15)
    with st.status("데이터 업데이트 중...", expanded=True) as status:
        try:
            st.write(f"1/2 크롤링 중... (작성일 {crawl_from} ~ {crawl_to})")
            st.code(run_script(
                "crawl_posts.py",
                "--date-from", crawl_from.isoformat(),
                "--date-to", crawl_to.isoformat(),
                "--max-pages", str(crawl_pages),
            ))
            st.write("2/2 파싱 중... (parse_posts.py)")
            st.code(run_script("parse_posts.py"))
            status.update(label="업데이트 완료 — 아래 목록은 최신 데이터입니다", state="complete", expanded=False)
        except Exception as e:
            status.update(label="업데이트 실패 — 기존 데이터로 표시합니다", state="error")
            st.error(f"{e}")

if POSTS_JSON.exists():
    mtime = datetime.fromtimestamp(POSTS_JSON.stat().st_mtime)
    mtime_slot.caption(f"마지막 업데이트: {mtime:%Y-%m-%d %H:%M}")

with open(POSTS_JSON, encoding="utf-8") as f:
    posts = json.load(f)

df = pd.DataFrame(posts)
df["경기일자"] = df["match_date"]
df["시간"]     = df["match_time"]
df = df.sort_values("created", ascending=False).reset_index(drop=True)
df["match_dt"] = [parse_match_date(md, cr) for md, cr in zip(df["경기일자"], df["created"])]
all_intents = sorted(df["intent"].dropna().unique().tolist())

NO_CITY = "(도시 미지정)"


def city_mask(frame: pd.DataFrame, selected: list) -> pd.Series:
    mask = frame["city"].isin(selected)
    if NO_CITY in selected:
        mask |= frame["city"].isna() | (frame["city"] == "")
    return mask


# ── 사이드바 필터 ───────────────────────────────
selected_dates = None
selected_venues = None
df_complete = None

with st.sidebar:
    st.header("필터")

    # dimension 1: 보기 구분
    st.subheader("보기 구분")
    view_mode = st.radio(
        "보기 구분",
        ["필터보기", "전체보기"],
        horizontal=True,
        label_visibility="collapsed",
        help="필터보기: 날짜·시간·장소가 모두 입력된 게시글만 표시",
    )

    if view_mode == "필터보기":
        include_no_date  = st.checkbox("날짜 미완성인 것 보기", value=False)
        include_no_time  = st.checkbox("시간 미완성인 것 보기", value=False)
        include_no_place = st.checkbox("장소 미완성인 것 보기", value=False)

    st.divider()

    # dimension: 글 구분 (의도 분류)
    st.subheader("글 구분")
    selected_intents = st.pills(
        "글 구분",
        options=all_intents,
        selection_mode="multi",
        default=all_intents,
        label_visibility="collapsed",
    )
    exclude_closed = st.checkbox("마감된 글 제외", value=False)

    st.divider()

    # dimension 2: 지역 필터
    st.subheader("지역 필터")
    cities = sorted(df["city"].dropna().unique().tolist())
    if (df["city"].isna() | (df["city"] == "")).any():
        cities.append(NO_CITY)
    default_cities = ["고양시"] if "고양시" in cities else cities[:1]
    selected_cities = st.pills(
        "도시 선택",
        options=cities,
        selection_mode="multi",
        default=default_cities,
    )

    # 필터보기 전용 상세 필터
    if view_mode == "필터보기":
        st.divider()
        st.subheader("상세 필터")

        df_base = (
            df[city_mask(df, selected_cities)].copy()
            if selected_cities
            else pd.DataFrame(columns=df.columns)
        )
        has_date  = df_base["경기일자"].astype(str).str.strip() != ""
        has_time  = df_base["시간"].astype(str).str.strip() != ""
        has_place = df_base["std_name"].notna() & (df_base["std_name"].astype(str).str.strip() != "")

        cond = pd.Series(True, index=df_base.index)
        if not include_no_date:
            cond &= has_date
        if not include_no_time:
            cond &= has_time
        if not include_no_place:
            cond &= has_place
        df_complete = df_base[cond].copy().reset_index(drop=True)

        match_dts = df_complete["match_dt"].tolist()
        valid_dts = sorted(d for d in match_dts if d)

        if valid_dts:
            dmin, dmax = valid_dts[0], valid_dts[-1]
            picked = st.date_input(
                "날짜 범위",
                value=(dmin, dmax),
                min_value=dmin,
                max_value=dmax,
                help="달력에서 시작일과 종료일을 차례로 클릭하세요",
            )
            # 시작일만 클릭한 상태면 1개짜리 튜플이 오므로 종료일로도 사용
            if isinstance(picked, (tuple, list)):
                start = picked[0]
                end = picked[1] if len(picked) == 2 else picked[0]
            else:
                start = end = picked
            selected_dates = {
                md for md, dt in zip(df_complete["경기일자"], match_dts)
                if dt and start <= dt <= end
            }
        else:
            selected_dates = None  # 달력 자체가 없으면 날짜 필터 미적용
            if df_complete.empty:
                st.warning("조건에 맞는 게시글이 없습니다.")

        st.divider()

        venues = sorted(df_complete["std_name"].dropna().unique().tolist())
        if venues:
            selected_venues = st.pills("장소 선택", options=venues, selection_mode="multi", default=venues)
        else:
            selected_venues = []

# ── 필터 적용 ───────────────────────────────────
if not selected_cities:
    view = pd.DataFrame(columns=df.columns)
elif view_mode == "전체보기":
    view = df[city_mask(df, selected_cities)].copy()
else:  # 필터보기
    view = df_complete.copy()

if not view.empty:
    if selected_intents:
        view = view[view["intent"].isin(selected_intents)]
    if exclude_closed:
        view = view[~view["is_closed"]]

if view_mode == "필터보기" and not view.empty:
    if selected_dates is not None:
        # 날짜 미완성 포함 시, 날짜 없는 행은 범위 필터에서 제외하지 않고 유지
        no_date = view["경기일자"].astype(str).str.strip() == ""
        view = view[view["경기일자"].isin(selected_dates) | no_date]
    if selected_venues:
        # 장소 미완성 포함 시, 장소 없는 행은 장소 필터에서 제외하지 않고 유지
        no_place = view["std_name"].isna() | (view["std_name"].astype(str).str.strip() == "")
        view = view[view["std_name"].isin(selected_venues) | no_place]

## 지도부분 일단 hide (6/30)
# ── 지도 (테이블 상단) ──────────────────────────
# try:
#     fc = load_sudogwon_fc()
#     st.altair_chart(make_map(fc), width="stretch")
# except Exception as e:
#     st.warning(f"지도 로딩 실패: {e}")

# st.divider()

# ── KPI 요약 ────────────────────────────────────
week_end = today + timedelta(days=7)
if not view.empty:
    is_closed = view["is_closed"].fillna(False).astype(bool)
    open_count = int((~is_closed).sum())
    week_count = int(view["match_dt"].apply(lambda d: isinstance(d, date) and today <= d <= week_end).sum())
else:
    open_count = week_count = 0

st.markdown(
    f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <span class="kpi-value">{len(view)}</span>
        <span class="kpi-label">전체 경기</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-value">{open_count}</span>
        <span class="kpi-label">모집중</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-value">{week_count}</span>
        <span class="kpi-label">이번 주</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── 게시글 테이블 ───────────────────────────────
city_label = "·".join(selected_cities) if selected_cities else "없음"
if view_mode == "전체보기":
    st.caption(f"[{city_label}] 전체 {len(view)}개 표시 중")
else:
    total_complete = len(df_complete) if df_complete is not None else 0
    st.caption(f"[{city_label}] 조건 충족 {total_complete}개 중 · {len(view)}개 표시 중")
st.markdown(build_match_list(view, all_intents, today), unsafe_allow_html=True)
