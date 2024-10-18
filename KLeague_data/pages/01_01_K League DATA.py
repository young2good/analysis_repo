import streamlit as st
import KLeague2024 as KLeague2024
import pass_dribble


# Streamlit title
st.title('K리그 데이터 시각화')

# with st.sidebar:
#     st.write("홈")
#     st.divider()
#     st.write("수신함")
#     st.divider()
#     st.write("선수단")
#     st.write("선수단 계획표")
#     st.write("세력 구도")
#     st.write("전술")
#     st.page_link("testpy.py", label = "데이터 허브")
#     st.write("스탭")
#     st.write("훈련")
#     st.write("의료 센터")
#     st.divider()
#     st.write("주요 일정")
#     st.write("대회")
#     st.divider()
#     st.write("스카우트")
#     st.write("이적")
#     st.divider()
#     st.write("구단 정보")
#     st.write("구단 비전")


#     st.write("재정")
#     st.divider()
#     st.write("육성 센터")

# page = st.sidebar.radio('페이지 선택',['기본 정보', '팀', '선수', '경기', '다음 상대', '전적'])

# # 선택한 페이지에 따라 내용 표시
# if page == '기본 정보':
#     st.title('기본 정보 페이지')
#     st.subheader('공격효율')
#     st.write('K리그, 이번 시즌')
#     st.altair_chart(KLeague2024.tot_shot_chart)
#     with st.expander("See explanation"):
#         st.write(':blue[_인천 유나이티드_]의 공격 효율 수치는 매우 부족합니다.')
#         st.write("슈팅이 득점으로 연결되는 비율이 '제주' 다음으로 낮습니다.")
#         st.write("경기당 슈팅수가 '대전' 다음으로 낮습니다.")

# elif page == '팀':
#     st.title('팀 페이지')
#     st.write('여기에 팀 관련 내용을 작성하세요.')

# elif page == '선수':
#     st.title('선수 페이지')
#     st.write('여기에 선수 관련 내용을 작성하세요.')

# elif page == '경기':
#     st.title('경기 페이지')
#     st.write('여기에 경기 관련 내용을 작성하세요.')

# elif page == '다음 상대':
#     st.title('다음 상대 페이지')
#     st.write('여기에 다음 상대 관련 내용을 작성하세요.')

# elif page == '전적':
#     st.title('전적 페이지')
#     st.write('여기에 전적 관련 내용을 작성하세요.')

# st.sidebar.selectbox("select one of them", ('Attacking','Defending'))

#

# tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['기본 정보', '팀', '선수', '경기', '다음 상대', '전적'])
tab2023, tab2024 = st.tabs([':soccer:2023 SEASON', ':soccer:2024 SEASON'])

with tab2023:
    st.header('2023: SEASON')
    st.subheader('플레이 스타일 by Team')
    st.altair_chart(pass_dribble.tot_chart)
    st.write('need a comment')

with tab2024:
    st.header('2024 SEASON: 인천 유나이티드')
    st.subheader('공격 효율')
    st.altair_chart(KLeague2024.tot_shot_chart)

    st.subheader('패스')
    st.altair_chart(KLeague2024.tot_chart)



# with tab1:
#     st.subheader('공격효율')
#     st.write('K리그, 이번 시즌')
#     st.altair_chart(KLeague2024.tot_shot_chart)
#     with st.expander("See explanation"):
#         st.write(':blue[_인천 유나이티드_]의 공격 효율 수치는 매우 부족합니다.')
#         st.write("슈팅이 득점으로 연결되는 비율이 '제주' 다음으로 낮습니다.")
#         st.write("경기당 슈팅수가 '대전' 다음으로 낮습니다.")

# with tab2:    
#     st.write('next')
#     st.altair_chart(KLeague2024.tot_chart)

# with tab3:
#     st.write('gg')
#     st.balloons()
#     st.metric("My metric", 42, 2)

# with tab4:
#     st.write('Done!')






# # 페이지 레이아웃을 두 개의 열로 나눔 (왼쪽: 본문, 오른쪽: 사이드바)
# col1, col2 = st.columns([3, 1])  # 비율로 열 크기 조정

# with col1:
#     st.write("여기에 본문 내용 입력")
#     tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['기본 정보', '팀', '선수', '경기', '다음 상대', '전적'])
#     # 탭 내용 추가

# with col2:
#     st.write("오른쪽에 위치한 사이드바")
#     option = st.selectbox("옵션 선택", ["옵션 1", "옵션 2", "옵션 3"])
#     st.write(f"선택한 옵션: {option}")
