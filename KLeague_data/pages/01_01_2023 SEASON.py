import streamlit as st
import KLeague2024 as KLeague2024
import pass_dribble


st.title('2023 SEASON')

st.subheader(':soccer: Play Style by team')
st.altair_chart(pass_dribble.tot_chart,)

st.write("""The chart shows the dribble attempts and pass attempts for each team. Teams choose between dribbling or passing to develop their attacks, and this graph helps define a team's style roughly. The red dots represent teams that were placed in the Final A after Round 33, while the blue dots represent teams in Final B. Ulsan, Seoul, Pohang, and Suwon FC are teams that use passing as their preferred style of play, while Gwangju stands out with a higher tendency to develop attacks through dribbling compared to other teams.""")

with st.expander('Data Source'):
    st.write('The data used is the number of pass attempts per match and dribble attempts per match from Round 1 to Round 33 of the 2023 season. (Source: KFA website)')

