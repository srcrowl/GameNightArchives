import pandas as pd 
#import dataLoader
from dataLoader import processResults
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.title('Game Night Statistics')

#load data
scores_dict, gplayed_dict, fraction_dict, pae_dict = processResults(st.session_state['Full Data'])
overall_fraction = scores_dict['Game'].sum()/gplayed_dict['Game'].sum()

#load data minus the last 15 games
past_data = st.session_state['Full Data'].iloc[0:-15]
past_scores, past_gplayed, past_fraction, past_pae = processResults(past_data, overall_only = True)
past_overall_fraction = past_scores['Game'].sum()/past_gplayed['Game'].sum()


#Widget indicating win percentage
st.header('Number of Wins')
col1, col2, col3 = st.columns(3)
current_wins = scores_dict['Game'].sum()
past_wins = past_scores['Game'].sum()
col1.metric("Sam", current_wins['Sam'], f"{current_wins['Sam'] - past_wins['Sam']}")
col2.metric("Gabi", current_wins['Gabi'], f"{current_wins['Gabi'] - past_wins['Gabi']}")
col3.metric("Reagan", current_wins['Reagan'], f"{current_wins['Reagan'] - past_wins['Reagan']}")

st.header('Win Percentages')
col1, col2, col3 = st.columns(3)
col1.metric("Sam", f"{round(overall_fraction['Sam']*100,2)}%", f"{round((overall_fraction['Sam'] - past_overall_fraction['Sam'])*100, 2)}%")
col2.metric("Gabi", f"{round(overall_fraction['Gabi']*100,2)}%", f"{round((overall_fraction['Gabi'] - past_overall_fraction['Gabi'])*100, 2)}%")
col3.metric("Reagan", f"{round(overall_fraction['Reagan']*100,2)}%", f"{round((overall_fraction['Reagan'] - past_overall_fraction['Reagan'])*100, 2)}%")



#number of games played
#st.header('Number of Games Won')
#fig = plt.figure()
#plt.bar(scores_dict['Game'].columns, scores_dict['Game'].sum())
#plt.ylabel('Number of Games Won')
#st.pyplot(fig)



#Breaking Down By Games
st.header('Breaking Down Win Percentage By Game')
chart_type = st.selectbox('Chart Type:', ['Bar', 'Heatmap'])
category = st.selectbox('Break down stats by:', ['Game','Format','Type', 'Owner', 'Theme'])
if chart_type == 'Bar':
	fraction = fraction_dict[category][['Sam', 'Gabi', 'Reagan']]
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
		fig = plt.figure(figsize = (2,6))
		
	metric = st.radio('Metric:', ['Win Fraction', 'Fraction Above Expected'], horizontal = True)
	if metric == 'Win Fraction':
		fraction = fraction_dict[category][['Sam', 'Gabi', 'Reagan']]
		cmap = 'Reds'
		vmin = 0
		vmax = 1
		label = 'Win Fraction'
	else:
		fraction = pae_dict[category][['Sam','Gabi','Reagan']]
		cmap = 'coolwarm'
		vmin = -1
		vmax = 1
		label = 'Fraction Above Expected'
	sns.heatmap(fraction, cmap = cmap, vmin = vmin, vmax = vmax, cbar_kws = {'label': label})

st.pyplot(fig)
