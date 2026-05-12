import streamlit as st
from datetime import date

st.set_page_config(page_title="선수 평가 시스템")

st.title("⚽ 선수 평가 시스템")

st.write("날짜를 선택하세요.")

selected_date = st.date_input(
    "평가 날짜 선택",
    value=date.today()
)

# 세션 저장
st.session_state["selected_date"] = str(selected_date)

# 이동 버튼
if st.button("결과 보기"):
    st.switch_page("display_app.py")