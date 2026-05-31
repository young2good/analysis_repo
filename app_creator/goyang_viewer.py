import json
import re
import pandas as pd
import streamlit as st
from pathlib import Path

POSTS_JSON = Path(__file__).parent / "posts.json"
CAFE_URL   = "https://cafe.daum.net/skfootball/IxVG/"


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


def build_html_table(df: pd.DataFrame) -> str:
    rows = ""
    for _, r in df.iterrows():
        url   = CAFE_URL + str(r["dataid"])
        title = r["title"].replace("<", "&lt;").replace(">", "&gt;")
        date  = r["경기일자"]
        time  = r["시간"]
        venue = r["std_name"] or ""
        rows += f"""
        <tr>
          <td><a href="{url}" target="_blank">{title}</a></td>
          <td style="white-space:nowrap">{date}</td>
          <td style="white-space:nowrap">{time}</td>
          <td>{venue}</td>
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
      <thead>
        <tr>
          <th>원제목</th>
          <th>날짜</th>
          <th>시간</th>
          <th>장소</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
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

st.caption(f"전체 {len(df)}개 중 고양시 {len(df_goyang)}개")

# ── 날짜 필터 (상단) ────────────────────────────
dates = sorted(df_goyang["경기일자"].replace("", None).dropna().unique().tolist())
selected_dates = st.multiselect("날짜 선택", options=dates, default=dates)

# ── 장소 필터 ───────────────────────────────────
venues = sorted(df_goyang["std_name"].dropna().unique().tolist())
selected_venues = st.multiselect("장소 선택", options=venues, default=venues)

# ── 필터 적용 ───────────────────────────────────
view = df_goyang.copy()
if selected_dates:
    view = view[view["경기일자"].isin(selected_dates)]
if selected_venues:
    view = view[view["std_name"].isin(selected_venues)]

st.caption(f"{len(view)}개 표시 중")
st.markdown(build_html_table(view), unsafe_allow_html=True)
