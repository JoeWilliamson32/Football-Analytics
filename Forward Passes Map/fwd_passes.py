import pandas as pd
from mplsoccer.pitch import Pitch
import numpy as np
import math
import matplotlib.pyplot as plt

# Here I'm using Opta data - will need to get the actual data yourself 
df = pd.read_csv('input.csv').iloc[:,1:]

# Select whichever player you want to do the pass map for
player = 'Mason Mount'
games = df[df['player'] == player]['game'].unique()
games = np.delete(games, [0,8,10])

def get_game_details(games):
    teams = games.rsplit('-')[2][3:6] + ' - ' + games.rsplit('-')[3][:3]
    date = date = games.rsplit(' ')[0]
    
    return teams,date

def get_pass_details(game, player):
    df_game = df[df['game'] == game]
    df_game = df_game[['type', 'outcome_type', 'player', 'x', 'y', 'end_x', 'end_y']]
    df_player = df_game[df_game['player'] == str(player)]
    df_player = df_player[(df_player['type'] == 'Pass') & (df_player['outcome_type'] == 'Successful')]
    df_player = df_player.reset_index(drop=True)
    
# Below is if you want to do Progressive Passes, here I'm just doing forward passes

#     beg_dist = []
#     for i in range(len(df_player)):
#         beg_dist.append(np.sqrt((100-df_player['x'][i])**2 + (50-df_player['y'][i])**2))
#     df_player['beg_dist'] = beg_dist

#     end_dist = []
#     for i in range(len(df_player)):
#         end_dist.append(np.sqrt((100-df_player['end_x'][i])**2 + (50-df_player['end_y'][i])**2))
#     df_player['end_dist'] = end_dist

#     df_player = df_player[df_player['end_dist']/df_player['beg_dist'] < 0.95]   
    df_player = df_player[df_player['end_x']/df_player['x'] > 1]
    df_player = df_player[['x', 'y', 'end_x', 'end_y']]
    
    return df_player

# Pick subplots size depending on how much data you've got
fig, axs = plt.subplots(5, 5, figsize=(30, 25))
axs = axs.ravel()
pitch = Pitch(pitch_color='cornsilk', line_color='slategray', pitch_type='opta')
fig.subplots_adjust(hspace = 0.0, wspace=0.02)
fig.set_facecolor('cornsilk')
fig.suptitle(str(player) + ' \n Forward Pass Map ', fontsize=24, 
             fontfamily='Helvetica', color='slategrey', fontweight="bold")
fig.tight_layout()
fig.subplots_adjust(top=0.935)

for i in range(25):
    pitch.draw(axs[i], figsize=(5,5))
    game, date = get_game_details(games[i])
    axs[i].set_title(str(game).upper() + '\n' + date, fontsize=15, fontfamily='Helvetica', color='slategrey')
    df_player = get_pass_details(games[i], player)
    pitch.arrows(df_player.x, df_player.y, df_player.end_x, df_player.end_y, color='slategrey',
             width=2, headwidth=5, headlength=5, ax=axs[i])
    
axs[13].set_title('CHE - MNU' + '\n' + '2021-11-28', fontsize=15, fontfamily='Helvetica', color='slategrey')
axs[21].set_title('CHE - WHU' + '\n' + '2022-04-24', fontsize=15, fontfamily='Helvetica', color='slategrey')
axs[22].set_title('CHE - MNU' + '\n' + '2021-11-28', fontsize=15, fontfamily='Helvetica', color='slategrey')

fig.savefig('mount_fwd_passes_22.png', dpi=300)

