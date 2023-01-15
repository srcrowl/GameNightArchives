import pandas as pd 
import dataLoader
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.title('Game Night Statistics')

#load data
scores_dict, gplayed_dict, fraction_dict = dataLoader.loadData()
overall_fraction = scores_dict['Game'].sum()/gplayed_dict['Game'].sum()

#google_sheets
sheets_url = 'https://docs.google.com/spreadsheets/d/1b6p3KtOIvPVRaWQ77q4Cq_P_yJ5Lsem12Yp33ufjABw/edit#gid=0'

#Widget indicating win percentage
st.header('Number of Wins')
col1, col2, col3 = st.columns(3)
col1.metric("Sam", scores_dict['Game'].sum()['Sam'], "0")
col2.metric("Gabi", scores_dict['Game'].sum()['Gabi'], "0")
col3.metric("Reagan", scores_dict['Game'].sum()['Reagan'], "0")

st.header('Win Percentages')
col1, col2, col3 = st.columns(3)
col1.metric("Sam", f"{round(overall_fraction['Sam']*100,2)}%", "0 %")
col2.metric("Gabi", f"{round(overall_fraction['Gabi']*100,2)}%", "0 %")
col3.metric("Reagan", f"{round(overall_fraction['Reagan']*100,2)}%", "0 %")



#number of games played
#st.header('Number of Games Won')
#fig = plt.figure()
#plt.bar(scores_dict['Game'].columns, scores_dict['Game'].sum())
#plt.ylabel('Number of Games Won')
#st.pyplot(fig)



#Breaking Down By Games
st.header('Breaking Down Win Percentage By Game')
chart_type = st.selectbox('Chart Type:', ['Bar', 'Heatmap'])
category = st.selectbox('Break down stats by:', ['Game','Game Format','Game Type', 'Game Owner'])
fraction = fraction_dict[category]
games_played = gplayed_dict[category]
if category == 'Game':
    min_gplayed = st.slider('Minimum Number of Times Played', min_value = 0, max_value = 50, value = 0)
    games_played = games_played[games_played >= min_gplayed]
    fraction = fraction.loc[games_played.index]
    
if chart_type == 'Bar':
    fig, ax = plt.subplots(figsize = (10,6), nrows = 3, sharex = 'col', sharey = 'all')
    for p in range(3):
        name = fraction.columns[p]
        ax[p].bar(fraction.index,fraction[name])
        ax[p].axhline(overall_fraction[name], linestyle = 'dashed', color = 'red')
        ax[p].set_ylabel('Win Fraction')
        ax[p].set_ylim([0,1])
        ticks = plt.xticks(rotation = 90)
        ax[p].set_title(name)
        for i in range(fraction.shape[0]):
            index = fraction.index[i]
            ax[p].annotate(int(games_played[index]), (i, fraction.loc[index,name]), ha = 'center')
else:
    if category == 'Game':
        fig = plt.figure(figsize = (2,6))
    else:
        fig = plt.figure(figsize = (2,3))
    sns.heatmap(fraction, cmap = 'coolwarm', vmin = 0, vmax = 1, cbar_kws = {'label': "Win Fraction"})

st.pyplot(fig)
