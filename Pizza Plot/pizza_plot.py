import requests
from bs4 import BeautifulSoup
import pandas as pd
import re 
import matplotlib.pyplot as plt
from mplsoccer import PyPizza, add_image, FontManager
from PIL import Image, ImageDraw
import math
from urllib.request import urlopen
import numpy as np


# This is mainly for attacking players
# If you want other stats for a different position, just use the scraping below and put them in the features wanted dict and rename df accordingly
# Just replace the below url for whatever player you want
url = str('https://fbref.com/en/players/9674002f/scout/365_m1/Mason-Mount-Scouting-Report')
name = url.rsplit('/', 1)[-1].rsplit('-',2)[0]

res = requests.get(url)
comm = re.compile("<!--|-->")
soup = BeautifulSoup(comm.sub("",res.text),'lxml')

all_tables = soup.findAll("tbody")
player_table =  all_tables[0]

pre_df_player = dict()
features_wanted = {"Number of players tackled", 
                   "Interceptions",
                   "Dribbles Completed Successfully",
                   "Progressive Passes Received<br>Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch",
                   "Pass Completion Percentage<br>Minimum 30 minutes played per squad game to qualify as a leader",
                   "Progressive Passes<br>Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch",
                   "<strong>Expected Assisted Goals</strong><br>xG which follows a pass that assists a shot<br>Provided by Opta.<br>An underline indicates there is a match that is missing data, but will be updated when available.",
                   "<strong>Non-Penalty Expected Goals</strong><br>Provided by Opta.<br>An underline indicates there is a match that is missing data, but will be updated when available.",
                   "Shots Total<br>Does not include penalty kicks"  ,
                   "Touches in attacking penalty area",
                   "Non-Penalty Goals",
                   "Assists",
                   "Aerials won",
                   "Passes Attempted",
                   "Shot-Creating Actions<br>The two offensive actions directly leading to a shot, such as passes, dribbles and drawing fouls. Note: A single player can receive credit for multiple actions and the shot-taker can also receive credit."
                  }
rows_player = player_table.find_all('tr')

for row in rows_player:
    if(row.find('th',{"scope":"row"}) != None): 

        for f in features_wanted:
            if (row.find('th',{'data-tip':f}) != None):
                cell = row.find("td",{"data-stat": 'percentile'})
                a = cell.text.strip().encode()
                text=a.decode("utf-8")

                if f in pre_df_player:
                    break
                else:
                    pre_df_player[f] = [text]


df_player = pd.DataFrame.from_dict(pre_df_player)
df_player = df_player.rename(index={0:name})
df_player = df_player.rename(columns={"Number of players tackled":"Tackles",
                                      "Interceptions":"Interceptions",
                                      "Dribbles Completed Successfully":"Dribbles\nCompleted",
                                      "Progressive Passes Received<br>Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch":"Progressive\nPasses Received",
                                      "Pass Completion Percentage<br>Minimum 30 minutes played per squad game to qualify as a leader" : "Pass Completion\nPercentage",
                                      "Progressive Passes<br>Completed passes that move the ball towards the opponent's goal at least 10 yards from its furthest point in the last six passes, or any completed pass into the penalty area. Excludes passes from the defending 40% of the pitch":"Progressive Passes",
                                      "<strong>Expected Assisted Goals</strong><br>xG which follows a pass that assists a shot<br>Provided by Opta.<br>An underline indicates there is a match that is missing data, but will be updated when available.":'xA',
                                      "<strong>Non-Penalty Expected Goals</strong><br>Provided by Opta.<br>An underline indicates there is a match that is missing data, but will be updated when available.":'npxG',
                                      "Shots Total<br>Does not include penalty kicks" : "Shots" ,
                                      "Touches in attacking penalty area":"Touches in\nPenalty Area",
                                      "Non-Penalty Goals":"npG",
                                      "Assists":"Assists",
                                      "Aerials won":"Aerials\nWon",
                                      "Passes Attempted":"Passes\nAttempted",
                                      "Shot-Creating Actions<br>The two offensive actions directly leading to a shot, such as passes, dribbles and drawing fouls. Note: A single player can receive credit for multiple actions and the shot-taker can also receive credit.":"SCA"
                                     })

df_player = df_player[['Pass Completion\nPercentage',"Passes\nAttempted" ,'Progressive Passes', 'Dribbles\nCompleted', 
       'Tackles', 'Interceptions',  "Aerials\nWon",
        'Progressive\nPasses Received', 'Touches in\nPenalty Area',
       'npxG', 'npG','xA', "Assists", 'SCA']]
params = df_player.columns.values.tolist()
values = df_player.values.flatten().tolist()
values = [int(i) for i in values]

font_normal = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/"
                           "Roboto%5Bwdth,wght%5D.ttf?raw=true"))
font_italic = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/"
                           "Roboto-Italic%5Bwdth,wght%5D.ttf?raw=true"))
font_bold = FontManager(("https://github.com/google/fonts/blob/main/apache/robotoslab/"
                         "RobotoSlab%5Bwght%5D.ttf?raw=true"))


# color for the slices and text
values.insert(4,0)
values.insert(8,0)
values.insert(11,0)
values.insert(17,0)
params.insert(4,'')
params.insert(8,'')
params.insert(11,'')
params.insert(17, '')

blank_colors = ["cornsilk"] * 4 + ['none'] + ["cornsilk"] * 3 + ['none'] +  ['cornsilk'] * 2 + ['none'] + ['cornsilk']*5 + ['none']
slice_colors = ["#1A78CF"] * 4 + ["#F2F2F2"] + ["#D70232"] * 3 + ["#F2F2F2"] +  ["#228B22"] * 2 + ["#F2F2F2"] + ['#FF8000']*5 + ["#F2F2F2"]
text_colors = ["#000000"] * 14 + ["#000000"] * 4

# instantiate PyPizza class
baker = PyPizza(
    inner_circle_size = 20,
    params=params,                  # list of parameters
    straight_line_color="#F2F2F2",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=1,               # linewidth of last circle
    last_circle_ls = '-',
    other_circle_lw=1,              # linewidth for other circles
    other_circle_ls= '-'  ,       # linestyle for other circles
    background_color = 'cornsilk',
    straight_line_limit = 101
)

# plot pizza
fig, ax = baker.make_pizza(
    values,                          # list of values
    figsize=(8, 9),                # adjust the figsize according to your need
    color_blank_space=blank_colors,         # use the same color to fill blank space
    slice_colors=slice_colors,       # color for individual slices
    value_colors=text_colors,        # color for the value-text
    value_bck_colors=['cornsilk']*18,   # color for the blank spaces
    blank_alpha=1 ,                 # alpha for blank-space colors
    kwargs_slices=dict(
        edgecolor="#000000", zorder=3, linewidth=1
    ),                               # values to be used when plotting slices
    kwargs_params=dict(
        color="#000000", fontsize=9,fontproperties=font_normal.prop,
        va="center"
    ),                               # values to be used when adding parameter labels
    kwargs_values=dict(
        color="#000000", fontsize=9,fontproperties=font_normal.prop,
        zorder=5,
        bbox=dict(
            edgecolor="#000000", facecolor="#F2F2F2",
            boxstyle="round,pad=.2", lw=1
        )
    )                                # values to be used when adding parameter-values labels
)

baker.get_value_texts()[4] = baker.get_value_texts()[4].set_text('')
baker.get_value_texts()[8] = baker.get_value_texts()[8].set_text('')
baker.get_value_texts()[11] = baker.get_value_texts()[11].set_text('')
baker.get_value_texts()[17] = baker.get_value_texts()[17].set_text('')


# add title
fig.text(
    0.515, 0.975, name.replace("-"," ") , size=16,
    ha="center",color="#000000",weight='bold',fontproperties=font_bold.prop
)

# add subtitle
fig.text(
    0.515, 0.955,
    "Percentile Rank vs Top-Five League Forwards | Last 365 days",
    size=13,
    ha="center",color="#000000"
)

# add credits
CREDIT_1 = "Data: Opta via Fbref"

fig.text(
    0.99, 0.02, f"{CREDIT_1}", size=9,
    color="#000000",
    ha="right"
)

# add text
fig.text(
    0.18, 0.93, "Passing/Dribbling        Defending      Box Play      Attacking", size=14,
    color="#000000"
)

# add rectangles
fig.patches.extend([
    plt.Rectangle(
        (0.145, 0.927), 0.025, 0.021, fill=True, color="#1A78CF",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.42, 0.927), 0.025, 0.021, fill=True, color="#D70232",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.595, 0.927), 0.025, 0.021, fill=True, color="#228B22",
        transform=fig.transFigure, figure=fig
    ),
    plt.Rectangle(
        (0.745, 0.927), 0.025, 0.021, fill=True, color="#FF8000",
        transform=fig.transFigure, figure=fig
    ),

])
fig.savefig('mount_pizza_plot.png', dpi=300)