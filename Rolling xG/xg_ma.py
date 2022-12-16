from understatapi import UnderstatClient
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

understat = UnderstatClient()

# For specific player - just use their UnderStat ID from the website
df = pd.DataFrame(understat.player('7768').get_shot_data())
df = df[~(df['situation'].isin(['Penalty']))].reset_index(drop=True)

goals = []
for i in range(len(df)):
    if df['result'][i] == 'Goal':
        goals.append(1)
    else:
        goals.append(0)
        
df['goals'] = goals
df2 = df[['match_id','xG', 'goals', 'date']]
df2['xG'] = pd.to_numeric(df2['xG'])
df3 = df2.groupby(['match_id', 'date']).sum()
df3 = df3.sort_values(by='date', ascending=True)
df3 = df3.reset_index()
df3['date'] = pd.to_datetime(df3['date']).dt.date
df3['match'] = range(1, len(df3)+1)
df3['xGsma'] = (df3['goals']-df3['xG']).rolling(window=10).mean()
mask = df3['xGsma'] >= 0 
df3['above'] = np.where(mask, df3['xGsma'], 0)
df3['below'] = np.where(mask, 0, df3['xGsma'])

# Just change the player name in the title 
fig = go.Figure()
fig.add_trace(go.Scatter(x=df3['date'], y=df3['above'], fill='tozeroy', mode='none'))
fig.add_trace(go.Scatter(x=df3['date'], y=df3['below'], fill='tozeroy', mode='none'))
fig.add_hline(y=0.0, opacity=1, line_dash='dash')
fig.update_layout(template='plotly_dark', showlegend=False)
fig.update_layout(
    title = {'text':'Mason Mount - npxG Trendline <br> <sup> 10 Game Rolling Average | Data: Understat </sup>', 'xanchor':'center', 'y':0.95, 'x':0.5},
    yaxis_title="G - xG",
) 

config = {
  'toImageButtonOptions': {
    'format': 'png', # one of png, svg, jpeg, webp
    'filename': 'custom_image',
    'height': 700,
    'width': 1200,
    'scale':6 # Multiply title/legend/axis/canvas sizes by this factor
  }
}


fig.show(config=config)

