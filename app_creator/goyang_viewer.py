import json
import re
import requests
import altair as alt
import pandas as pd
import streamlit as st
from pathlib import Path

POSTS_JSON = Path(__file__).parent / "posts.json"
CAFE_URL   = "https://cafe.daum.net/skfootball/IxVG/"
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
        url   = CAFE_URL + str(r["dataid"])
        title = r["title"].replace("<", "&lt;").replace(">", "&gt;")
        rows += f"""
        <tr>
          <td><a href="{url}" target="_blank">{title}</a></td>
          <td style="white-space:nowrap">{r['경기일자']}</td>
          <td style="white-space:nowrap">{r['시간']}</td>
          <td>{r['std_name'] or ''}</td>
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
        <th>원제목</th><th>날짜</th><th>시간</th><th>장소</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""


# ── UI ─────────────────────────────────────────
st.set_page_config(page_title="고양시 게시글", layout="wide")
st.title("고양시 게시글 목록")

with open(POSTS_JSON, encoding="utf-8") as f:
    posts = json.load(f)

df = pd.DataFrame(posts)
df_goyang = df[df["city"] == "고양시"].copy()
df_goyang = df_goyang.sort_values("created", ascending=False).reset_index(drop=True)
df_goyang["경기일자"] = df_goyang["title"].apply(extract_date)
df_goyang["시간"]     = df_goyang["title"].apply(extract_time)

# ── 사이드바 필터 ───────────────────────────────
with st.sidebar:
    st.header("필터")

    def valid_date(d):
        if not d or "/" not in str(d):
            return False
        try:
            return int(str(d).split("/")[0]) <= 12
        except ValueError:
            return False

    dates = sorted(
        [d for d in df_goyang["경기일자"].replace("", None).dropna().unique() if valid_date(d)],
        key=lambda d: tuple(int(x) for x in d.split("/"))
    )

    if len(dates) >= 2:
        date_range = st.select_slider("날짜 범위", options=dates, value=(dates[0], dates[-1]))
        start_idx, end_idx = dates.index(date_range[0]), dates.index(date_range[1])
        selected_dates = set(dates[start_idx:end_idx + 1])
    else:
        selected_dates = set(dates)

    st.divider()

    venues = sorted(df_goyang["std_name"].dropna().unique().tolist())
    selected_venues = st.pills("장소 선택", options=venues, selection_mode="multi", default=venues)

# ── 필터 적용 ───────────────────────────────────
view = df_goyang.copy()
view = view[view["경기일자"].isin(selected_dates)]
if selected_venues:
    view = view[view["std_name"].isin(selected_venues)]

## 지도부분 일단 hide (6/30)
# ── 지도 (테이블 상단) ──────────────────────────
# try:
#     fc = load_sudogwon_fc()
#     st.altair_chart(make_map(fc), width="stretch")
# except Exception as e:
#     st.warning(f"지도 로딩 실패: {e}")

# st.divider()

# ── 게시글 테이블 ───────────────────────────────
st.caption(f"전체 {len(df)}개 중 고양시 {len(df_goyang)}개 · {len(view)}개 표시 중")
st.markdown(build_html_table(view), unsafe_allow_html=True)
