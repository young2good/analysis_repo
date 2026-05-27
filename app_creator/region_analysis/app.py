import streamlit as st
from data_loader import load_data
from charts import (
    sido_bar_chart,
    sigungu_bar_chart,
    interactive_sido_sigungu_chart,
    sido_pie_chart,
    board_pie_chart,
    zone_bar_chart,
    interactive_zone_sigungu_chart,
    AXIS_CONFIG,
)

st.title("지역별 게시글 분석")

df = load_data()

st.subheader("데이터 미리보기")
st.dataframe(df.head(5))

st.subheader("게시판별 비중 (파이차트)")
chart = board_pie_chart(df).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("시도별")
chart = sido_bar_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("시도별 비율 (파이차트)")
chart = sido_pie_chart(df).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("시군구별")
chart = sigungu_bar_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("시도 선택 → 시군구 필터")
chart = interactive_sido_sigungu_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("권역별")
chart = zone_bar_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("권역 선택 → 시군구 필터")
chart = interactive_zone_sigungu_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)
