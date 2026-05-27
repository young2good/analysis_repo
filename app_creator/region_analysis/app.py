import streamlit as st
from data_loader import load_data
from charts import sido_bar_chart, sigungu_bar_chart, interactive_sido_sigungu_chart, AXIS_CONFIG

st.title("지역별 게시글 분석")

df = load_data()

st.subheader("데이터 미리보기")
st.dataframe(df.head(5))

st.subheader("시도별")
chart = sido_bar_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("시군구별")
chart = sigungu_bar_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)

st.subheader("시도 선택 → 시군구 필터")
chart = interactive_sido_sigungu_chart(df).configure_axis(**AXIS_CONFIG).configure_view(stroke=None)
st.altair_chart(chart, use_container_width=True)
