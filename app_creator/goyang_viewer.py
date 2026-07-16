"""파싱이 끝난 posts_temp.json을 읽어 화면에 보여주는 순수 뷰어.

데이터 생성 파이프라인: crawl_posts.py(크롤링) → parse_posts.py(파싱) → posts_temp.json
상단 "데이터 업데이트" 버튼으로 위 파이프라인을 화면에서 직접 실행할 수 있다.
"""
import json
import os
import subprocess
import sys
from datetime import date, datetime
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


# ── HTML 테이블 ─────────────────────────────────
def build_html_table(df: pd.DataFrame) -> str:
    rows = ""
    for _, r in df.iterrows():
        url   = r["url"]
        title = r["title"].replace("<", "&lt;").replace(">", "&gt;")
        closed_cls = ' class="closed"' if r.get("is_closed") else ""
        badge = ' <span class="badge-closed">마감</span>' if r.get("is_closed") else ""
        rows += f"""
        <tr{closed_cls}>
          <td><a href="{url}" target="_blank">{title}</a>{badge}</td>
          <td style="white-space:nowrap">{r['경기일자']}</td>
          <td style="white-space:nowrap">{r['시간']}</td>
          <td>{r['std_name'] or ''}</td>
          <td style="white-space:nowrap">{r.get('intent') or ''}</td>
          <td style="white-space:nowrap">{r['source']}</td>
        </tr>"""

    return f"""
    <style>
      .post-table {{ width:100%; border-collapse:collapse; font-size:14px; }}
      .post-table th {{
        background:#f4f4f4; text-align:left;
        padding:8px 12px; border-bottom:2px solid #ddd;
      }}
      .post-table td {{
        padding:7px 12px; border-bottom:1px solid #eee; vertical-align:top;
      }}
      .post-table tr:hover td {{ background:#fafafa; }}
      .post-table a {{ color:#1a73e8; text-decoration:none; }}
      .post-table a:hover {{ text-decoration:underline; }}
      .post-table tr.closed td, .post-table tr.closed a {{ color:#aaa; }}
      .badge-closed {{
        background:#eee; color:#888; font-size:11px;
        padding:1px 6px; border-radius:8px; margin-left:4px;
      }}
    </style>
    <table class="post-table">
      <thead><tr>
        <th>원제목</th><th>날짜</th><th>시간</th><th>장소</th><th>구분</th><th>출처</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""


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
st.set_page_config(page_title="게시글 뷰어", layout="wide")
st.title("게시글 목록")

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
    intents = sorted(df["intent"].dropna().unique().tolist())
    selected_intents = st.pills(
        "글 구분",
        options=intents,
        selection_mode="multi",
        default=intents,
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

        def parse_match_date(md, created):
            """'M/D' 문자열을 게시일(created) 연도 기준 date로 변환. 실패 시 None."""
            try:
                m, d = str(md).split("/")
                return date(int(str(created)[:4]), int(m), int(d))
            except (ValueError, AttributeError):
                return None

        match_dts = [
            parse_match_date(md, cr)
            for md, cr in zip(df_complete["경기일자"], df_complete["created"])
        ]
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

# ── 게시글 테이블 ───────────────────────────────
city_label = "·".join(selected_cities) if selected_cities else "없음"
if view_mode == "전체보기":
    st.caption(f"[{city_label}] 전체 {len(view)}개 표시 중")
else:
    total_complete = len(df_complete) if df_complete is not None else 0
    st.caption(f"[{city_label}] 조건 충족 {total_complete}개 중 · {len(view)}개 표시 중")
st.markdown(build_html_table(view), unsafe_allow_html=True)
