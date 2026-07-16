import json
import re
import requests
import altair as alt
import pandas as pd
import streamlit as st
from pathlib import Path

POSTS_JSON = Path(__file__).parent / "posts_temp.json"
GEOJSON_URL = (
    "https://raw.githubusercontent.com/southkorea/southkorea-maps"
    "/master/kostat/2013/json/skorea_municipalities_geo_simple.json"
)


# ── 파싱 함수 ───────────────────────────────────
def extract_date(title: str) -> str:
    m = re.search(r'(\d{1,2})월\s*(\d{1,2})일?', title)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    m = re.search(r'(\d{1,2})[./]\s*(\d{1,2})', title)
    if m:
        return f"{int(m.group(1))}/{int(m.group(2))}"
    m = re.search(r'(\d{1,2})월', title)
    if m:
        return f"{m.group(1)}월"
    return ""


def extract_time(title: str) -> str:
    m = re.search(r'(\d{1,2}:\d{2})\s*[-~]\s*(\d{1,2}:\d{2})', title)
    if m:
        return f"{m.group(1)}~{m.group(2)}"
    m = re.search(r'(오전|오후)?\s*(\d{1,2})\s*[~\-]\s*(\d{1,2})\s*시', title)
    if m:
        prefix = m.group(1) or ""
        return f"{prefix}{m.group(2)}~{m.group(3)}시"
    m = re.search(r'(\d{1,2})시\s*[-~]\s*(\d{1,2})시', title)
    if m:
        return f"{m.group(1)}~{m.group(2)}시"
    m = re.search(r'\b(\d{1,2})\s*[~\-]\s*(\d{1,2})\b', title)
    if m and int(m.group(1)) <= 24 and int(m.group(2)) <= 24:
        return f"{m.group(1)}~{m.group(2)}시"
    m = re.search(r'(\d{1,2})시', title)
    if m:
        return f"{m.group(1)}시"
    return ""

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
        rows += f"""
        <tr>
          <td><a href="{url}" target="_blank">{title}</a></td>
          <td style="white-space:nowrap">{r['경기일자']}</td>
          <td style="white-space:nowrap">{r['시간']}</td>
          <td>{r['std_name'] or ''}</td>
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
    </style>
    <table class="post-table">
      <thead><tr>
        <th>원제목</th><th>날짜</th><th>시간</th><th>장소</th><th>출처</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""


# ── UI ─────────────────────────────────────────
st.set_page_config(page_title="게시글 뷰어", layout="wide")
st.title("게시글 목록")

with open(POSTS_JSON, encoding="utf-8") as f:
    posts = json.load(f)

df = pd.DataFrame(posts)
df["경기일자"] = df["title"].apply(extract_date)
df["시간"]     = df["title"].apply(extract_time)
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

        def valid_date(d):
            if not d or "/" not in str(d):
                return False
            try:
                return int(str(d).split("/")[0]) <= 12
            except ValueError:
                return False

        dates = sorted(
            [d for d in df_complete["경기일자"].unique() if valid_date(d)],
            key=lambda d: tuple(int(x) for x in d.split("/"))
        )

        if len(dates) >= 2:
            date_range = st.select_slider("날짜 범위", options=dates, value=(dates[0], dates[-1]))
            start_idx = dates.index(date_range[0])
            end_idx = dates.index(date_range[1])
            selected_dates = set(dates[start_idx:end_idx + 1])
        elif len(dates) == 1:
            selected_dates = set(dates)
        else:
            selected_dates = set()
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
    if selected_dates:
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
