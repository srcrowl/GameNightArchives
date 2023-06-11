import pandas as pd 
#import dataLoader
from dataLoader import loadData_ratings, processResults, loadData_categories, loadData_results
from game_plots import win_fraction_barplot, win_heatmap
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st

if 'Full Data' not in st.session_state:
    st.session_state['Full Data'] = loadData_results()
    
if 'Type' not in st.session_state:
    loadData_categories()
    

semester = st.selectbox('Pick a semester to look at:', st.session_state['Full Data']['Semester'].unique())

st.title(f'Game Night Statistics ({semester})')

#load data
full_data = st.session_state['Full Data'][st.session_state['Full Data']['Semester'] == semester]
scores_dict, gplayed_dict, fraction_dict, pae_dict, par_dict = processResults(full_data)
overall_fraction = scores_dict['Game'].sum()/gplayed_dict['Game'].sum()


#Widget indicating win percentage
st.header('Number of Wins')
col1, col2, col3 = st.columns(3)
current_wins = scores_dict['Game'].sum()
col1.metric("Sam", current_wins['Sam'], delta = None)
col2.metric("Gabi", current_wins['Gabi'], delta = None)
col3.metric("Reagan", current_wins['Reagan'], delta = None)

st.header('Win Percentages')
col1, col2, col3 = st.columns(3)
col1.metric("Sam", f"{round(overall_fraction['Sam']*100,2)}%", delta = None)
col2.metric("Gabi", f"{round(overall_fraction['Gabi']*100,2)}%", delta = None)
col3.metric("Reagan", f"{round(overall_fraction['Reagan']*100,2)}%", delta = None)



#Breaking Down By Games
st.header('Breaking Down Win Percentage By Game')
chart_type = st.selectbox('Chart Type:', ['Bar', 'Heatmap'])
category = st.selectbox('Break down stats by:', ['Game','Format',"Game Length", "Team Size", "Primary Classification","Sam's Mechanisms", 'Owner', 'Location','Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism'])
fraction = fraction_dict[category][['Sam', 'Gabi', 'Reagan']]
games_played = gplayed_dict[category]

min_gplayed = st.slider('Minimum Number of Times Played', min_value = 0, max_value = 50, value = 0)
games_played = games_played[games_played >= min_gplayed]
fraction = fraction.loc[games_played.index]
	
if chart_type == 'Bar':
	fig = win_fraction_barplot(fraction, overall_fraction, games_played)

else:
	metric = st.radio('Metric:', ['Win Fraction', 'Fraction Above Expected'], horizontal = True)
	fig = win_heatmap(fraction_dict, pae_dict, games = games_played.index, category = category, metric = metric)

st.pyplot(fig)



#Tracking Progress Over Time
if semester != 'Fall2021':
    st.header('Tracking Wins Over Time')
    st.write("We've been doing this for a while now, how have wins progressed over time?")

    #time = st.radio('Track time by:' , ['Date', 'Number of Games Played'], horizontal = True)
    track = st.radio('What do you want to track?', ['Number of Wins', 'Win Fraction', 'Win Time', 'Number of Games', 'Time Spent Playing Games']) 


    legend = False
    #@st.cache(ttl=300)
    def plotCumulative(track = 'Number of Games'):
        if track == 'Number of Games':
            plot_data = full_data.groupby(['Date']).size().cumsum()
            ylabel = 'Number of Games'
            legend = False
        elif track == 'Time Spent Playing Games':
            plot_data = full_data.groupby(['Date']).sum().cumsum()/60
            ylabel = 'Play Time (Hours)'
            legend = False
        elif track == 'Number of Wins' or track == 'Win Fraction' or track == 'Win Time':
            plot_data = full_data.copy()
            if track == 'Win Fraction':
                gplayed_cumsum = plot_data.groupby('Date').size().cumsum()
                
            plot_data['Winner'] = plot_data['Winner'].apply(lambda x: x.split(';'))
            plot_data = plot_data.explode('Winner')
            plot_data['Wins'] = 1
            if track == 'Number of Wins' or track == 'Win Fraction':
                plot_data = plot_data.groupby(['Winner', 'Date'])['Wins'].sum().reset_index()
                plot_data = plot_data.pivot(columns = 'Winner', index = 'Date', values = 'Wins')
                plot_data = plot_data.replace(np.nan, 0)
                plot_data = plot_data.cumsum()
                plot_data = plot_data[['Sam', 'Gabi', 'Reagan']]
                if track == 'Number of Wins':
                    legend = True
                    ylabel = 'Number of Wins'
                elif track == 'Win Fraction':
                    legend = True
                    ylabel = 'Win Fraction'
                    plot_data = (plot_data.T/gplayed_cumsum).T
            elif track == 'Win Time':
                plot_data = plot_data.groupby(['Winner', 'Date'])['Play Time (min)'].sum().reset_index()
                plot_data = plot_data.pivot(columns = 'Winner', index = 'Date', values = 'Play Time (min)')
                plot_data = plot_data.replace(np.nan, 0)
                plot_data = plot_data.cumsum()
                plot_data = plot_data[['Sam', 'Gabi', 'Reagan']]
                legend = True
                ylabel = 'Win Time (min)'
                
        return plot_data, ylabel, legend

    plot_data, ylabel, legend = plotCumulative(track)
    fig, ax = plt.subplots()
    if legend:
        ax.plot(plot_data.index.values, plot_data.values, label = plot_data.columns)
        ax.legend(bbox_to_anchor = (1.05, 1))
    else:
        ax.plot(plot_data.index.values, plot_data.values)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation = 45, ha = 'center')

    st.pyplot(fig)