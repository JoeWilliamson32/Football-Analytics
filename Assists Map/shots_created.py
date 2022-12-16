from understatapi import UnderstatClient
import pandas as pd
import plotly.express as px
from matplotlib.patches import Rectangle
import matplotlib as mpl
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch, VerticalPitch

understat = UnderstatClient()

# To change to a particular season/league - change the season/league accordingly
match_ids = pd.DataFrame(understat.league(league='EPL').get_match_data(season='2021'))

# For specific player - just change matches to their team here
matches = []
home_away = []
for i in range(len(match_ids)):
    if match_ids['h'][i]['title'] == 'Chelsea':
        matches.append(match_ids['id'][i])
        home_away.append('h')
    elif match_ids['a'][i]['title'] == 'Chelsea':
        matches.append(match_ids['id'][i])
        home_away.append('a')

# Then add player name here - all you need to change
df = {'id':matches, 'h/a':home_away}
df = pd.DataFrame(df)
player = 'Mason Mount'

df_player = pd.DataFrame()

for i in range(len(df)):
    test_id = df['id'][i]
    h_a = df['h/a'][i]
    df1 = pd.DataFrame(understat.match(match=test_id).get_shot_data()[h_a])
    for i in range(len(df1)):
        if df1['player_assisted'][i] == str(player):
            df_ = pd.DataFrame(df1[['result', 'X', 'Y', 'xG', 'player', 'situation', 'player_assisted']].iloc[i,:]).T.reset_index(drop=True)
            df_player = pd.concat([df_player, df_], axis=0)

df_player = df_player.reset_index(drop=True)
df_player['xG'] = pd.to_numeric(df_player['xG'])

assists = df_player[df_player['result'] == 'Goal']['result'].count()
openplay = df_player[df_player['situation'] == 'OpenPlay']['result'].count()
setpieces = df_player[(df_player['situation'] == 'FromCorner') | (df_player['situation'] == 'SetPiece')]['situation'].count()

df_player['X'] = pd.to_numeric(df_player['X'])
df_player['Y'] = pd.to_numeric(df_player['Y'])
df_player['X1'] = (df_player['X'])*100
df_player['Y1'] = (df_player['Y'])*100

colors = []
alpha = []
for i in range(len(df_player)):
    if df_player['result'][i] == 'Goal':
        colors.append('gold')
        alpha.append(1)
    elif df_player['situation'][i] == 'OpenPlay':
        colors.append('#ea6969')
        alpha.append(0.7)
    else:
        colors.append('dodgerblue')
        alpha.append(0.7)

df_player['color'] = colors
df_player['alpha'] = alpha

league_player_data = understat.league(league="EPL").get_player_data(season="2021")
df_playerlist = pd.DataFrame(league_player_data)
mins = int(df_playerlist[df_playerlist['player_name'] == str(player)]['time'])
xA = df_player['xG'].sum()
xAp90 = (xA/(mins/90)).round(2)
opxA = df_player[df_player['situation'] == 'OpenPlay']['xG'].sum()
opxAp90 = (opxA/(mins/90)).round(2)
spxA = xA - opxA
spxAp90 = (spxA/(mins/90)).round(2)

fig, ax = plt.subplots(figsize=(14,7.8))
fig.set_facecolor('black')
ax.patch.set_facecolor('black')

#The statsbomb pitch from mplsoccer
pitch = VerticalPitch(pitch_type='opta',
              pitch_color='black', line_color='#c7d5cc', half=True )

pitch.draw(ax=ax)
plt.scatter(df_player['Y1'],df_player['X1'], s=df_player['xG']*750, c=df_player['color'],alpha=df_player['alpha'])

plt.suptitle(str(player), c = 'white', fontsize=20, ha='left', x = 0.1525, y=0.99)
plt.title('Shots Created Map | Premier League 21-22', c = 'white', fontsize=14,  x = 0.23, y=0.99)
plt.subplots_adjust(top=1)

circle1 = plt.Circle((93, 57), 2, color='gold')
plt.gca().add_patch(circle1)
cx = 91 + circle1.get_width()/2.0
cy = 57 + circle1.get_height()/2.0
ax.annotate(str(assists), (cx, cy-2), color='black', fontsize=12, ha='center', va='center')
ax.annotate('Assists', (cx, cy+2.5), color='white', fontsize=12, ha='center', va='center')

circle2 = plt.Circle((85, 57), 2, color='#ea6969')
plt.gca().add_patch(circle2)
cx2 = 83 + circle2.get_width()/2.0
cy2 = 57 + circle2.get_height()/2.0
ax.annotate(str(openplay), (cx2, cy2-2), color='black', fontsize=12, ha='center', va='center')
ax.annotate('Open \n Play KP', (cx2, cy2+2.5), color='white', fontsize=12, ha='center', va='center')

circle3 = plt.Circle((77, 57), 2, color='dodgerblue')
plt.gca().add_patch(circle3)
cx3 = 75 + circle3.get_width()/2.0
cy3 = 57 + circle3.get_height()/2.0
ax.annotate(str(setpieces), (cx3, cy3-2), color='black', fontsize=12, ha='center', va='center',fontfamily='monospace')
ax.annotate('Set \n Piece KP', (cx3, cy3+2.5), color='white', fontsize=12, ha='center', va='center')

ax.annotate('Minutes:         ' + str(mins), (24, 65), color='white', fontsize=12, ha='left', va='center',
           fontfamily='monospace')
ax.annotate('xA:              ' + str(xA.round(2)), (24, 63), color='white', fontsize=12, ha='left',
            fontfamily='monospace', va='center')
ax.annotate('xA/90:           ' + str(xAp90), (24, 61), color='white', fontsize=12, ha='left', va='center',
           fontfamily='monospace')
ax.annotate('Open Play xA:    ' + str(opxA.round(2)), (24, 59), color='white', fontsize=12, ha='left', 
            fontfamily='monospace', va='center')
ax.annotate('Open Play xA/90: ' + str(opxAp90.round(2)), (24, 57), color='white', fontsize=12, ha='left', 
            fontfamily='monospace', va='center')
ax.annotate('Set Piece xA:    ' + str(spxA.round(2)), (24, 55), color='white', fontsize=12, ha='left', 
            fontfamily='monospace', va='center')
ax.annotate('Set Piece xA/90: ' + str(spxAp90.round(2)), (24, 53), color='white', fontsize=12, ha='left',
            fontfamily='monospace', va='center')

ax.add_patch(Rectangle((1.5, 51.25), 24, 16.5, fill=False, edgecolor='white'))


ax.set_aspect('equal')

fig.savefig('mount_sc_22.png', dpi=300)



