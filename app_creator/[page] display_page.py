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
    "Son",
    "JaeYoon"
]

# 포지션 정렬 순서
position_order = {
    "FW": 0,
    "MF": 1,
    "DF": 2,
    "GK": 3
}

# -----------------------------
# 초기 page 상태
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "calendar"

# -----------------------------
# CALENDAR PAGE
# -----------------------------
if st.session_state.page == "calendar":

    st.set_page_config(page_title="선수 포지션 시스템")

    st.title("⚽ 출석부 & 포지션")

    selected_date = st.date_input(
        "포지션 확인 날짜 선택",
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

    st.title(f"📅 {selected_date} 포지션")

    # 현재 py파일 기준 경로
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # data 폴더 경로
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # JSON 파일 경로
    data_file = os.path.join(DATA_DIR, f"{selected_date}.json")

    # # JSON 파일 경로
    # data_file = f"app_creator/data/{selected_date}.json"

    # JSON 읽기
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            ratings = json.load(f)
    else:
        ratings = {}

    st.write("---")

    # -----------------------------
    # 활성 / 비활성 분리
    # -----------------------------
    active_players = []
    inactive_players = []

    for player in players:

        # 활성 선수
        if player in ratings:

            active_players.append({
                "name": player,
                "quarter_1": ratings[player]["quarter_1"],
                "quarter_2": ratings[player]["quarter_2"]
            })

        # 비활성 선수
        else:
            inactive_players.append(player)

    # -----------------------------
    # 활성 선수 정렬
    # FW → MF → DF → GK
    # -----------------------------
    active_players.sort(
        key=lambda x: position_order.get(x["quarter_1"], 99)
    )

    # -----------------------------
    # 활성 선수 출력
    # -----------------------------
    for player_info in active_players:

        player = player_info["name"]
        quarter_1 = player_info["quarter_1"]
        quarter_2 = player_info["quarter_2"]

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
                <span style="float:right;">
                    1Q: {quarter_1} | 2Q: {quarter_2}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------
    # 비활성 선수 출력
    # -----------------------------
    for player in inactive_players:

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

    # -----------------------------
    # 뒤로가기
    # -----------------------------
    if st.button("← 날짜 선택으로 돌아가기"):
        st.session_state.page = "calendar"
        st.rerun()