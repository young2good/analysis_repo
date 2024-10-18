#!/usr/bin/env python
# coding: utf-8

# In[14]:


import altair as alt
import pandas as pd
import numpy as np
import pickle


# In[15]:


# temp_df = pd.read_clipboard()
# temp_df


# In[16]:


# with open('pass_dribble_2023.pickle','wb') as f:
#     pickle.dump(temp_df,f)


# In[17]:


temp_df = pd.read_pickle('pass_dribble_2023.pickle')


# In[18]:


new_temp = temp_df[['구단', '패스 성공', '롱패스 성공']]
new_temp


# In[19]:


### 값을 int로 변경
new_temp['패스 성공'] = new_temp['패스 성공'].str.replace(',','').astype(int)
new_temp['롱패스 성공'] = new_temp['롱패스 성공'].str.replace(',','').astype(int)

new_temp


# In[20]:


new_temp['avg_pass'] = new_temp['패스 성공'] / 38
new_temp['avg_logpass'] = new_temp['롱패스 성공'] / 38
new_temp


# In[21]:


new_temp.head()


# In[22]:


alt.Chart(new_temp).mark_point().encode(
    x = alt.X('avg_pass').scale(domain= [200,550]),
    y = alt.Y('avg_logpass').scale(domain=[25, 45]),
    tooltip= '구단'
)


# In[23]:


new_temp


# In[24]:


def split(df):
    split_d ={
        '울산': '파이널A',
        '포항': '파이널A',
        '광주': '파이널A',
        '전북': '파이널A',
        '인천': '파이널A',
        '대구': '파이널A',
        '서울': '파이널B',
        '대전': '파이널B',
        '제주': '파이널B',
        '강원': '파이널B',
        '수원FC': '파이널B',
        '수원': '파이널B',
    }
    return split_d.get(df)

split('광주')


# In[25]:


temp_df['split'] = temp_df['구단'].apply(lambda x: split(x))
temp_df


# In[26]:


new_temp['split'] = new_temp['구단'].apply(lambda x: split(x))
new_temp


# In[27]:


alt.Chart(new_temp).mark_point().encode(
    x = 'avg_pass',
    y = 'avg_logpass',
    color = 'split',
    tooltip='구단'
)


# In[28]:


temp_df.columns


# In[29]:


temp_df[['패스 성공%','롱패스 성공%']]


# In[30]:


point_chart = alt.Chart(temp_df).mark_point().encode(
    x = alt.X('패스 성공%').scale(domain=[70, 100]),
    y = alt.Y('롱패스 성공%').scale(domain=[40, 70]),
    color = 'split',
    tooltip='구단'
)


# In[31]:


point_chart = alt.Chart(new_temp).mark_circle(size = 100).encode(
    x = alt.X('avg_pass').scale(domain= [200,550]),
    y = alt.Y('avg_logpass').scale(domain=[25, 45]),
    tooltip= '구단',
    color = alt.Color('split').scale(range=['red','blue'])
)

rulex_chart = alt.Chart(new_temp).mark_rule(stroke='lightgray', strokeDash=[5,5]).encode(
    x = 'tot_avg:Q',
).transform_aggregate(
    tot_avg = 'median(avg_pass)'
)

textx_chart = alt.Chart(new_temp).mark_text().encode(
    x = 'tot_avg:Q',
    y = alt.value(20),
    text = alt.value('Median Pass')
    # text = 'tot_avg:Q'
).transform_aggregate(
    tot_avg = 'median(avg_pass)'
)

ruley_chart = alt.Chart(new_temp).mark_rule(stroke ='lightgrey', strokeDash=[5,5]).encode(
    y = 'tot_avg2:Q',
).transform_aggregate(
    tot_avg2 = 'median(avg_logpass)'
)

texty_chart = alt.Chart(new_temp).mark_text().encode(
    x = alt.value(40),
    y = 'tot_avg2:Q',
    text =alt.value('Median Longpass')
    # text = 'tot_avg2:Q'
).transform_aggregate(
    tot_avg2 = 'median(avg_logpass)'
)

textt_chart = alt.Chart(new_temp).mark_text(dx = 15, dy = 10).encode(
    x = 'avg_pass',
    y = 'avg_logpass',
    text = '구단'
)




tot_chart = point_chart + rulex_chart + textx_chart + ruley_chart + texty_chart + textt_chart
tot_chart.properties(
    width = 800,
    height = 450
)


# In[32]:


new_temp.describe(include='all')


# In[33]:


selection = alt.selection_point(
    fields=['구단']
)

point_chart = alt.Chart(new_temp).mark_circle(size = 100).encode(
    x = alt.X('avg_pass').scale(domain= [200,550]),
    y = alt.Y('avg_logpass').scale(domain=[25, 45]),
    tooltip= '구단',
    color = alt.condition(
        selection,
        # alt.Color('split').scale(range=['red','blue']),
        alt.value('blue'),
        alt.value('lightgray')
    )
    # color = alt.Color('split').scale(range=['red','blue'])
)

rulex_chart = alt.Chart(new_temp).mark_rule(stroke='lightgray', strokeDash=[5,5]).encode(
    x = 'tot_avg:Q',
).transform_aggregate(
    tot_avg = 'median(avg_pass)'
)

textx_chart = alt.Chart(new_temp).mark_text().encode(
    x = 'tot_avg:Q',
    y = alt.value(20),
    text = alt.value('Median Pass')
    # text = 'tot_avg:Q'
).transform_aggregate(
    tot_avg = 'median(avg_pass)'
)

ruley_chart = alt.Chart(new_temp).mark_rule(stroke ='lightgrey', strokeDash=[5,5]).encode(
    y = 'tot_avg2:Q',
).transform_aggregate(
    tot_avg2 = 'median(avg_logpass)'
)

texty_chart = alt.Chart(new_temp).mark_text().encode(
    x = alt.value(40),
    y = 'tot_avg2:Q',
    text =alt.value('Median Longpass')
    # text = 'tot_avg2:Q'
).transform_aggregate(
    tot_avg2 = 'median(avg_logpass)'
)

textt_chart = alt.Chart(new_temp).mark_text(dx = 10, dy = 10).encode(
    x = 'avg_pass',
    y = 'avg_logpass',
    text = '구단'
)




tot_chart = point_chart + rulex_chart + textx_chart + ruley_chart + texty_chart + textt_chart
tot_chart.properties(
    width = 800,
    height = 450
).add_params(
    selection
).transform_filter(
    selection
)


# In[34]:


temp_df.head()


# In[35]:


temp_df.columns


# In[38]:


### 값을 int로 변경

temp_df2 = pd.DataFrame()

for i in temp_df.columns:
    if i != '구단' and i != 'split' and temp_df[i].dtype == 'O':
        temp_df2[i] = pd.to_numeric(temp_df[i].str.replace(',', ''), errors='coerce').fillna(0).astype(int)
    else:
        temp_df2[i] = temp_df[i]

temp_df2

# new_temp['패스 성공'] = new_temp['패스 성공'].str.replace(',','').astype(int)
# new_temp['롱패스 성공'] = new_temp['롱패스 성공'].str.replace(',','').astype(int)




# In[120]:


temp_df2.columns


# In[39]:


base_chart = alt.Chart(temp_df2).transform_calculate(
    avg_pass = 'datum["패스 시도"]/38',
    avg_dri = 'datum["드리블 시도"]/38'
)


tot_chart = alt.layer(
    base_chart.mark_circle(size=200).encode(
        x=alt.X('avg_pass:Q').scale(domain=[250,650], bins=[300, 400, 500, 600]).title('Passes Per Match'),
        y=alt.Y('avg_dri:Q').scale(domain=[5,10.5], bins= [6,7,8,9,10]).axis(format = '0.0f').title('Dribbles Per Match'),
        color = alt.Color('split').scale(range=['#ee3224', '#001c48']).title('파이널 라운드')
    ),
    base_chart.mark_text(
        dx = 15, 
        dy = 15
    ).encode(
        x = alt.X('avg_pass:Q'),
        y = alt.Y('avg_dri:Q'),
        text= '구단',
        color = alt.Color('split').scale(range=['#ee3224', '#001c48'])
    ),
    base_chart.encode(x='med_pass:Q').mark_rule(
        stroke='gray',
        strokeDash=[5,5]
    ).transform_aggregate(
        med_pass = 'median(avg_pass)',
        med_dri = 'median(avg_dri)'
    ),
    base_chart.encode(y = 'med_dri:Q').mark_rule(
        stroke='gray',
        strokeDash=[5,5]
    ).transform_aggregate(
        med_pass = 'median(avg_pass)',
        med_dri = 'median(avg_dri)'
    ),
    base_chart.encode(
        x = 'med_pass:Q',
        y = alt.value(5),
        text = alt.value('Median Passes')
    ).mark_text(
        color='gray',
        dy = 8
    ).transform_aggregate(
        med_pass = 'median(avg_pass)',
    ),
    base_chart.encode(
        x = alt.value(50),
        y = 'med_dri:Q',
        text = alt.value('Median Dribbles')
    ).mark_text(
        dy = -10,
        color='gray'
    ).transform_aggregate(
        med_dri = 'median(avg_dri)'    
    ),
    alt.Chart().mark_rect(color = '#9D0A0F').encode(
        x = alt.value(10),
        x2 = alt.value(230),
        y = alt.value(110),
        y2 = alt.value(90),
        # color = 'red'
    ),
    alt.Chart().mark_text(color = 'white').encode(
        x = alt.value(120),
        y = alt.value(100),
        text = alt.value('Less Pass Attempt & More Dribble Attempt'),
    ),
    alt.Chart().mark_rect(color = '#9D0A0F').encode(
        x = alt.value(570),
        x2 = alt.value(790),
        y = alt.value(590),
        y2 = alt.value(570),
        # color = 'red'
    ),
    alt.Chart().mark_text(color = 'white').encode(
        x = alt.value(680),
        y = alt.value(580),
        text = alt.value('More Pass Attempt & Less Dribble Attempt'),
    )
)

tot_chart.properties(
    height = 600,
    width = 800,
    # title = alt.Title(text = 'Team Style Comparison', subtitle='2023 K League1')
).configure_axis(
    grid=False,
    ticks = False,
    domainWidth= 2,
    domainOpacity=0.4,
    labelFontSize=11,
    labelFont='Helvetica',
    labelFontStyle= 'bold',
    labelColor='gray'
).configure_view(
    stroke = None,
    fill = '#F6F6F6',
    opacity=0.3
)


# In[40]:


### 한글이 최고다

base_chart = alt.Chart(temp_df2).transform_calculate(
    avg_pass = 'datum["패스 시도"]/38',
    avg_dri = 'datum["드리블 시도"]/38'
)


tot_chart = alt.layer(
    base_chart.mark_circle(size=200).encode(
        x = alt.X('avg_pass:Q').scale(domain=[250,650], bins=[300, 400, 500, 600]).title('매치당 평균 패스 시도'),
        y = alt.Y('avg_dri:Q').scale(domain=[5,10], bins= [6,7,8,9,10]).axis(format = '0.0f').title('매치당 평균 드리블 시도'),
        color = alt.Color('split').scale(range=['#ee3224', '#001c48']).title('파이널 라운드')
    ),
    base_chart.mark_text(
        dx = 15, 
        dy = 15
    ).encode(
        x = alt.X('avg_pass:Q'),
        y = alt.Y('avg_dri:Q'),
        text= '구단',
        color = alt.Color('split').scale(range=['#ee3224', '#001c48'])
    ),
    base_chart.encode(x = 'med_pass:Q').mark_rule(
        stroke='gray',
        strokeDash=[5,5]
    ).transform_aggregate(
        med_pass = 'median(avg_pass)',
        med_dri = 'median(avg_dri)'
    ),
    base_chart.encode(y = 'med_dri:Q').mark_rule(
        stroke='gray',
        strokeDash=[5,5]
    ).transform_aggregate(
        med_pass = 'median(avg_pass)',
        med_dri = 'median(avg_dri)'
    ),
    base_chart.encode(
        x = 'med_pass:Q',
        y = alt.value(5),
        text = alt.value('패스 시도(중앙값)')
    ).mark_text(
        color='gray',
        dy = 8,
        dx = 45
    ).transform_aggregate(
        med_pass = 'median(avg_pass)',
    ),
    base_chart.encode(
        x = alt.value(60),
        y = 'med_dri:Q',
        text = alt.value('드리블 시도(중앙값)')
    ).mark_text(
        dy = -10,
        color='gray'
    ).transform_aggregate(
        med_dri = 'median(avg_dri)'    
    ),
    alt.Chart().mark_rect(color = '#9D0A0F').encode(
        x = alt.value(10),
        x2 = alt.value(230),
        y = alt.value(110),
        y2 = alt.value(90),
        # color = 'red'
    ),
    alt.Chart().mark_text(color = 'white').encode(
        x = alt.value(120),
        y = alt.value(100),
        text = alt.value('패스 빈도 낮음 & 드리블 빈도 높음'),
    ),
    alt.Chart().mark_rect(color = '#9D0A0F').encode(
        x = alt.value(570),
        x2 = alt.value(790),
        y = alt.value(590),
        y2 = alt.value(570),
        # color = 'red'
    ),
    alt.Chart().mark_text(color = 'white').encode(
        x = alt.value(680),
        y = alt.value(580),
        text = alt.value('패스 빈도 높음 & 드리블 빈도 낮음'),
    )
)

tot_chart = tot_chart.properties(
    height = 600,
    width = 800,
    # title = alt.Title(text = 'Team Style Comparison', subtitle='2023 K League1')
).configure_axis(
    grid=False,
    ticks = False,
    domainWidth= 2,
    domainOpacity=0.4,
    # domainCap='round',
    labelFontSize=11,
    labelFont='Helvetica',
    labelFontStyle= 'bold',
    labelColor='gray'
).configure_view(
    stroke = None,
    fill = '#F6F6F6',
    opacity=0.3
)


# In[ ]:


# 클릭 하이라이트

