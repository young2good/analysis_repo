#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import altair as alt
import pickle


# In[2]:


# temp_data = pd.read_clipboard()


# In[5]:


# with open ('shot_data.pickle', 'wb') as f:
#     pickle.dump(temp_data,f)


# In[6]:


temp_data = pd.read_pickle('../shot_data.pickle')
# with open("shot_data.pickle","rb") as f:
#     temp_data = pickle.load(f)


# In[106]:


temp_data['games'] =33
temp_data


# In[107]:


temp_data['shots_per_game'] = temp_data['슈팅'] / temp_data['games']
temp_data


# In[131]:


shot_base = (
    alt.
    Chart(temp_data)        
)

shot_point = (
    shot_base.
    encode(
        x = alt.X('Conversion Rate:Q').scale(domain = [0.06, 0.16], bins = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12,0.13, 0.14, 0.15, 0.16]).axis(format = '0.0%').title('CONVERSION RATE(%)'),
        y = alt.Y('shots_per_game:Q').scale(domain = [8, 14], bins = [8, 9, 10, 11, 12, 13, 14]).axis(format = '~s').title('SHOTS PER GAME'),
        color = alt.condition(
            alt.datum.구단 == '인천',
            alt.value('#0d509f'),
            alt.value('lightgray')
        )
    ).
    mark_circle(size = 200)
)

shot_text = (
    shot_base.
    encode(
        x = 'Conversion Rate:Q',
        y = 'shots_per_game:Q',
        text = '구단:N',
        color = alt.condition(
            alt.datum.구단 == '인천',
            alt.value('#0d509f'),
            alt.value('gray')
        )
    ).
    mark_text(
        dx = 15,
        dy = 10
    )
)

# x axis ruler (med conversion rate)
xruler_shot = (
    shot_base.
    transform_aggregate(
        med_conversion_rate = 'median(Conversion Rate)'
    ).
    encode(
        x = 'med_conversion_rate:Q'
    ).
    mark_rule(
        stroke = 'lightgray',
        strokeDash=[5,5]
    )
)
# x-ruler text
xaxis_shot = (
    xruler_shot.
    encode(
        y = alt.value(5),
        text = alt.value('Median of Conversion Rate'),
        color = alt.value('white')
    ).
    mark_text(dy = 8)
)


# y axis ruler (median of pass attempt per game)
yruler_shot = (
    shot_base.
    transform_aggregate(
        med_shot = 'median(shots_per_game)'
    ).
    encode(
        y = 'med_shot:Q'
    ).
    mark_rule(
        stroke = 'lightgray',
        strokeDash=[5,5]
    )
)
# y-ruler text
yaxis_shot = (
    yruler_shot.
    encode(
        x = alt.value(80),
        text = alt.value('Median of Shots per Game'),
        color = alt.value('white')
    ).
    mark_text(dy = -10)
)


## TEXT 
shot_good_text = (
    alt.Chart().mark_text(color = '#5C9B6D').encode(
        x = alt.value(700),
        y = alt.value(30),
        text = alt.value('Aggressive shooting, Clinical shooting')
    )
)

shot_soso_text1 = (
    alt.Chart().mark_text(color = '#F6A849').encode(
        x = alt.value(110),
        y = alt.value(30),
        text = alt.value('Aggressive shooting, Wasteful shooting')
    )
)

shot_soso_text2 = (
    alt.Chart().mark_text(color = '#F6A849').encode(
        x = alt.value(700),
        y = alt.value(570),
        text = alt.value('Passive shooting, Clinical shooting')
    )
)

shot_bad_text = (
    alt.Chart().mark_text(color = '#D43835').encode(
        x = alt.value(110),
        y = alt.value(570),
        text = alt.value('Passive shooting, Wasteful shooting')
    )
)

tot_shot_chart = alt.layer(
    shot_point,
    shot_text,
    xruler_shot,
    xaxis_shot,
    yruler_shot,
    yaxis_shot,
    shot_good_text,
    shot_soso_text1,
    shot_soso_text2,
    shot_bad_text
)

tot_shot_chart = tot_shot_chart.properties(
    height = 600,
    width = 800,
    background = '#2F2F2F',
    title = 'ATTACKING EFFICIENCY'
).configure_axis(
    grid = False,
    domainColor='lightgray',  # 축 색상
    tickColor='lightgray',  # 틱 색상
    labelColor='white',  # 축 라벨 색상
    titleColor='white',  # 축 제목 색상
).configure_title(
    fontSize = 20,
    anchor = 'start',
    color = '#E23CC9',
    fontWeight= 900,
    offset = 30
)

tot_shot_chart


# In[7]:


# temp_pass_data = pd.read_clipboard()
# temp_pass_data


# In[8]:


# with open('pass_data.pickle','wb') as f:
#     pickle.dump(temp_pass_data,f)


# In[9]:


temp_pass_data = pd.read_pickle('pass_data.pickle')
temp_pass_data


# In[3]:


temp_pass_data['games'] = 33
temp_pass_data['passes_attempted_per_game'] = temp_pass_data['시도'] / temp_pass_data['games']

temp_pass_data


# In[103]:


# base part
base_chart = (
    alt.
    Chart(temp_pass_data)
)

# point part
point_chart = (
    base_chart.
    encode(
        x = alt.X('성공%:Q',scale=alt.Scale(domain = [82,90], bins = [82, 83, 84, 85, 86, 87, 88, 89, 90]), axis = alt.Axis(format = '~s')).title('PASS COMPLETION RATIO (%)'),
        y = alt.Y('passes_attempted_per_game:Q', scale = alt.Scale(domain = [400, 580], bins = [400, 420, 440, 460, 480, 500, 520, 540, 560, 580])).title('PASSES ATTEMPTED PER GAME'),
        color = alt.condition(
            alt.datum.구단 == '인천',
            alt.value('#0d509f'),
            alt.value('lightgray')
        ),
        tooltip= '구단:N'
    ).
    mark_circle(size = 200)
)

# text part
text_chart = (
    base_chart.
    encode(
        x = '성공%:Q',
        y = 'passes_attempted_per_game:Q',
        text = '구단:N',
        color = alt.condition(
            alt.datum.구단 == '인천',
            alt.value('#0d509f'),
            alt.value('gray')
        )
    ).
    mark_text(
        dx = 15,
        dy = 10
    )
)

# # x axis ruler (mean of x axis:pass completion ratio)
xruler_chart = (
    base_chart.
    transform_aggregate(
        med_pass_rate = 'median(성공%)'
    ).
    encode(
        x = 'med_pass_rate:Q'
    ).
    mark_rule(
        stroke = 'lightgray',
        strokeDash=[5,5]
    )
)
# x-ruler text
xaxis_textchart = (
    xruler_chart.
    encode(
        y = alt.value(5),
        text = alt.value('Median of Passes Completion Ratio'),
        color = alt.value('white')
    ).
    mark_text(dy = 8)
)


# y axis ruler (median of pass attempt per game)
yruler_chart = (
    base_chart.
    transform_aggregate(
        med_pass_attempt = 'median(passes_attempted_per_game)'
    ).
    encode(
        y = 'med_pass_attempt:Q'
    ).
    mark_rule(
        stroke = 'lightgray',
        strokeDash=[5,5]
    )
)
# y-ruler text
yaxis_textchart = (
    yruler_chart.
    encode(
        x = alt.value(80),
        text = alt.value('Median of Passes per Game'),
        color = alt.value('white')
    ).
    mark_text(dy = -10)
)

### TEXT for evaluation
good_text = (
    alt.Chart().mark_text(color = '#5C9B6D').encode(
        x = alt.value(700),
        y = alt.value(30),
        text = alt.value('Lots of passes, Accurate passing')
    )
)

soso_text1 = (
    alt.Chart().mark_text(color = '#F6A849').encode(
        x = alt.value(90),
        y = alt.value(30),
        text = alt.value('Lots of passes, Inaccurate passing')
    )
)

soso_text2 = (
    alt.Chart().mark_text(color = '#F6A849').encode(
        x = alt.value(700),
        y = alt.value(570),
        text = alt.value('Fewer passes, Accurate passing')
    )
)

bad_text = (
    alt.Chart().mark_text(color = '#D43835').encode(
        x = alt.value(90),
        y = alt.value(570),
        text = alt.value('Fewer passes, Inaccurate passing')
    )
)

tot_chart = alt.layer(
    point_chart,
    text_chart,
    xruler_chart,
    # xaxis_textchart,
    yruler_chart,
    # yaxis_textchart
    good_text,
    soso_text1,
    soso_text2,
    bad_text
)

tot_chart.properties(
    height = 600,
    width = 800,
    background = '#2F2F2F',
    title = 'PASSING'
).configure_axis(
    grid = False,
    domainColor='lightgray',  # 축 색상
    tickColor='lightgray',  # 틱 색상
    labelColor='white',  # 축 라벨 색상
    titleColor='white',  # 축 제목 색상
).configure_title(
    fontSize = 20,
    anchor = 'start',
    color = '#E23CC9',
    fontWeight= 900,
    offset = 30
)



# In[ ]:




