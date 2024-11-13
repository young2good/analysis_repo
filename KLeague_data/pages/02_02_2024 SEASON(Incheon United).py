import streamlit as st 
import KLeague2024 as KLeague2024

st.title('2024 SEASON - Incheon United')

st.subheader(':soccer: Attacking Efficiency')
st.altair_chart(KLeague2024.tot_shot_chart)
st.write("""In the 2024 season, Incheon United's attacking efficiency is the worst among the 12 teams. Their average shots per match is the second-lowest, just above Daejeon, and their conversion rate (the percentage of shots leading to goals) is the second-lowest, just above Jeju. It seems there are significant issues with their attacking efficiency.""")
with st.expander('Data Source'):
    st.write('The data used is the number of shot attempts per match and shot conversion rate from Round 1 to Round 33 of the 2024 season. (Source: KFA website)')

st.divider()

st.subheader(':soccer: Passing')
st.altair_chart(KLeague2024.tot_chart)
st.write("""Incheon's pass statistics are around the middle. Looking at the overall metrics, teams with strong passing indicators are placed in Final A (Ulsan, Gimcheon, Gangwon, Seoul, Pohang, Suwon FC), while teams with weaker passing indicators are assigned to Final B (Gwangju, Jeju, Daejeon, Jeonbuk, Daegu, Incheon). Among these, Gwangju stands out as an unusual case.""")
with st.expander('Data Source'):
    st.write('The data used is the number of pass attempts per match and pass complete rate from Round 1 to Round 33 of the 2024 season. (Source: KFA website)')

