import streamlit as st
import KLeague2024


# Streamlit title
st.title('Your Dashboard')

st.sidebar.selectbox("select one of them", ('Attacking','Defending'))


tab1, tab2 = st.tabs(['shot', 'pass'])

with tab1:
    st.write('shots')
    st.altair_chart(KLeague2024.tot_shot_chart)
    with st.expander("See explanation"):
        st.write('I think this is the best')

st.write('next')
st.altair_chart(KLeague2024.tot_chart)



