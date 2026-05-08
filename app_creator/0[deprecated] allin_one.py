import streamlit as st
from datetime import date
import json
import os

# 전체 선수 목록
players = [
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Kylian Mbappé",
    "Erling Haaland",
    "Neymar Jr",
    "Kevin De Bruyne",
    "Mohamed Salah",
    "Harry Kane",
    "Vinícius Jr",
    "Jude Bellingham",
    "Son"
]

# -----------------------------
# 초기 page 상태
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "calendar"

# -----------------------------
# CALENDAR PAGE
# -----------------------------
if st.session_state.page == "calendar":

    st.set_page_config(page_title="선수 평가 시스템")

    st.title("⚽ 출석부")

    selected_date = st.date_input(
        "평가 날짜 선택",
        value=date.today()
    )

    if st.button("결과 보기"):
        st.session_state.selected_date = str(selected_date)
        st.session_state.page = "display"
        st.rerun()

# -----------------------------
# DISPLAY PAGE
# -----------------------------
elif st.session_state.page == "display":

    selected_date = st.session_state.get("selected_date")

    st.title(f"📅 {selected_date} 평가 결과")

    data_file = f"data/{selected_date}.json"

    # JSON 읽기
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            ratings = json.load(f)
    else:
        ratings = {}

    st.write("---")

    # 선수 표시
    for player in players:

        # 활성 선수
        if player in ratings:
            score = ratings[player]

            st.markdown(
                f"""
                <div style="
                    padding:10px;
                    margin-bottom:8px;
                    border-radius:10px;
                    background-color:#d4edda;
                    color:black;
                    font-size:18px;
                ">
                    ✅ <b>{player}</b>
                    <span style="float:right;">{score}점</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 비활성 선수
        else:
            st.markdown(
                f"""
                <div style="
                    padding:10px;
                    margin-bottom:8px;
                    border-radius:10px;
                    background-color:#dddddd;
                    color:#777777;
                    font-size:18px;
                ">
                    {player}
                </div>
                """,
                unsafe_allow_html=True
            )

    # 뒤로가기
    if st.button("← 날짜 선택으로 돌아가기"):
        st.session_state.page = "calendar"
        st.rerun()