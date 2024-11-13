import streamlit as st

st.title('K League Data Visualization :sunglasses:')


first_text = '''
This page aims to visualize various K League data to highlight league trends, team performance, and player statstics.

Through this visualization, I strive to provide you with more insightful information.
'''
st.markdown(first_text)

st.divider()

st.subheader('KEY VISUALIZATIONS')
st.markdown('**Team Performance**: Compare and analyze team performance based on metrics such as the number of matches, goals scored, and goals conceded per season.')
st.markdown('**Player Stats**: Evaluate individual player performance through key stats, including goals scored, pass success rate, and game time.')
st.markdown('**League Trend**: Display various game metrics over time, such as changes in goals scored, number of penalties, and red cards, using time series data.')

st.divider()

st.subheader('Contents')    
st.markdown('- 2023 SEASON')
st.markdown('- 2024 SEASON: for Incheon United')

