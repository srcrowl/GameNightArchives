import pandas as pd 
#import dataLoader
from dataLoader import loadData_ratings, processResults, loadData_categories, loadData_results
from game_plots import win_fraction_barplot, win_heatmap
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
import hydralit_components as hc
st.set_page_config(layout='wide')

if 'Full Data' not in st.session_state:
    st.session_state['Full Data'] = loadData_results()
    
if 'Owner' not in st.session_state:
    loadData_categories()
    
if 'Rating' not in st.session_state:
    st.session_state['Ratings'] = loadData_ratings()
    
st.title('Game Night Statistics')

#load data
scores_dict, gplayed_dict_overall, gplayed_dict_player, fraction_dict, pae_dict, par_dict = processResults(st.session_state['Full Data'])
overall_fraction = scores_dict['Game'].sum()/gplayed_dict_player['Game'].sum()

#load data minus the last 15 games
past_data = st.session_state['Full Data'].iloc[0:-15]
past_scores, past_gplayed_overall, past_gplayed_player, past_fraction, past_pae, past_par = processResults(past_data, overall_only = True)
past_overall_fraction = past_scores['Game'].sum()/past_gplayed_player['Game'].sum()

#make it look nice from the start
#st.set_page_config(layout='wide',initial_sidebar_state='collapsed',)
menu_data = [
    {'label':"Overall Stats"},
    {'label':"Breaking Down By Games"},
    {'label': "Tracking Progress Over Time"},{'label':"Ongoing Dynasties"},
    {'label':"You are Due For a Win!"}
]
menu = hc.nav_bar(menu_definition = menu_data, sticky_nav = True, sticky_mode = 'pinned')

if menu == 'Overall Stats':
        #Widget indicating win percentage
    st.header('Number of Wins')
    col1, col2, col3 = st.columns(3)
    current_wins = scores_dict['Game'].sum()
    past_wins = past_scores['Game'].sum()

    #write the overall wins
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sam", current_wins['Sam'], f"{current_wins['Sam'] - past_wins['Sam']}")
    col2.metric("Gabi", current_wins['Gabi'], f"{current_wins['Gabi'] - past_wins['Gabi']}")
    col3.metric("Reagan", current_wins['Reagan'], f"{current_wins['Reagan'] - past_wins['Reagan']}")
    if 'Adrian' in past_wins.index:
        col4.metric('Adrian', current_wins['Adrian'], f"{current_wins['Adrian'] - past_wins['Adrian']}")
    else:
        col4.metric('Adrian', current_wins['Adrian'], current_wins['Adrian'])

    st.header('Win Percentages')
    #write overall percentages
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sam", f"{round(overall_fraction.loc['Sam']*100,2)}%", f"{round((overall_fraction.loc['Sam'] - past_overall_fraction.loc['Sam'])*100, 2)}%")
    col2.metric("Gabi", f"{round(overall_fraction.loc['Gabi']*100,2)}%", f"{round((overall_fraction.loc['Gabi'] - past_overall_fraction.loc['Gabi'])*100, 2)}%")
    col3.metric("Reagan", f"{round(overall_fraction.loc['Reagan']*100,2)}%", f"{round((overall_fraction.loc['Reagan'] - past_overall_fraction.loc['Reagan'])*100, 2)}%")
    if 'Adrian' in past_overall_fraction.index:
        col4.metric('Adrian', f"{round(overall_fraction.loc['Adrian']*100,2)}%", f"{round((overall_fraction.loc['Adrian'] - past_overall_fraction.loc['Adrian'])*100, 2)}%")
    else:
        col4.metric('Adrian', f"{round(overall_fraction.loc['Adrian']*100,2)}%", f"{round(overall_fraction.loc['Adrian']*100, 2)}%")
elif menu == 'Breaking Down By Games':
    st.header('Breaking Down Win Percentage By Game')
    cols = st.columns(spec = [0.3,0.7])
    #give option to choose specific players
    cols[0].write('Select players to plot:')
    sam = cols[0].checkbox('Sam', value = True)
    gabi = cols[0].checkbox('Gabi', value = True)
    reagan = cols[0].checkbox('Reagan', value = True)
    adrian = cols[0].checkbox('Adrian', value = True)
    players = []
    if sam:
        players.append('Sam')
    if gabi:
        players.append('Gabi')
    if reagan:
        players.append('Reagan')
    if adrian:
        players.append('Adrian')

    #set plot type and category to plot
    chart_type = cols[0].selectbox('Chart Type:', ['Bar', 'Heatmap'])
    category = cols[0].selectbox('Break down stats by:', ['Game','Format',"Game Length", "Team Size", "Primary Classification","Win Condition", "Luck Score", "Sam's Mechanisms", 'Owner', 'Location','Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism'])
    fraction = fraction_dict[category][players]
    #restrict by number of games played
    games_played = gplayed_dict_player[category][players]
    min_gplayed = cols[0].slider('Minimum Number of Times Played', min_value = 0, max_value = 50, value = 0)
    #give option to choose specific players

    games_played = games_played[games_played.max(axis = 1) >= min_gplayed]
    fraction = fraction.loc[games_played.index]

	
    if chart_type == 'Bar':
        fig = win_fraction_barplot(fraction, overall_fraction, games_played, players = players)

    else:
        metric = st.radio('Metric:', ['Win Fraction', 'Fraction Above Expected', 'Fraction Above Random'], horizontal = True)
        if metric == 'Win Fraction':
            plot_dict = fraction_dict
        elif metric == 'Fraction Above Expected':
            plot_dict = pae_dict
        elif metric == 'Fraction Above Random':
            plot_dict = par_dict
        fig = win_heatmap(plot_dict, games = games_played.index, category = category, metric = metric, players = players)

    cols[1].pyplot(fig)
elif menu == 'Tracking Progress Over Time':
        #Tracking Progress Over Time
    st.header('Tracking Wins Over Time')
    st.write("We've been doing this for a while now, how have wins progressed over time?")
    cols = st.columns(spec = [0.3,0.7])
    #time = st.radio('Track time by:' , ['Date', 'Number of Games Played'], horizontal = True)
    track = cols[0].radio('What do you want to track?', ['Number of Wins', 'Win Fraction', 'Win Time', 'Number of Games', 'Time Spent Playing Games']) 

    legend = False
    @st.cache_data(ttl=300)
    def plotCumulative(track = 'Number of Games'):
        if track == 'Number of Games':
            plot_data = st.session_state['Full Data'].groupby(['Date']).size().cumsum()
            ylabel = 'Number of Games'
            legend = False
        elif track == 'Time Spent Playing Games':
            plot_data = st.session_state['Full Data'].groupby(['Date']).sum().cumsum()/60
            ylabel = 'Play Time (Hours)'
            legend = False
        elif track == 'Number of Wins' or track == 'Win Fraction' or track == 'Win Time':
            plot_data = st.session_state['Full Data'].copy()
            if track == 'Win Fraction':
                #track games played by each person
                gplayed_cumsum = plot_data.copy()
                players = ['Sam', 'Gabi', 'Reagan', 'Adrian']
                for player in players:
                    gplayed_cumsum[player] = gplayed_cumsum['Players'].apply(lambda x: (player in x)*1)
                gplayed_cumsum = gplayed_cumsum.groupby('Date')[players].sum().cumsum()


            plot_data['Winner'] = plot_data['Winner'].apply(lambda x: x.split(';'))
            plot_data = plot_data.explode('Winner')
            plot_data['Wins'] = 1
            if track == 'Number of Wins' or track == 'Win Fraction':
                plot_data = plot_data.groupby(['Winner', 'Date'])['Wins'].sum().reset_index()
                plot_data = plot_data.pivot(columns = 'Winner', index = 'Date', values = 'Wins')
                plot_data = plot_data.replace(np.nan, 0)
                plot_data = plot_data.cumsum()
                plot_data = plot_data[['Sam', 'Gabi', 'Reagan', 'Adrian']]
                if track == 'Number of Wins':
                    legend = True
                    ylabel = 'Number of Wins'
                elif track == 'Win Fraction':
                    legend = True
                    ylabel = 'Win Fraction'
                    for player in ['Sam', 'Gabi', 'Reagan', 'Adrian']:
                        plot_data[player] = plot_data[player]/gplayed_cumsum[player]

            elif track == 'Win Time':
                plot_data = plot_data.groupby(['Winner', 'Date'])['Play Time (min)'].sum().reset_index()
                plot_data = plot_data.pivot(columns = 'Winner', index = 'Date', values = 'Play Time (min)')
                plot_data = plot_data.replace(np.nan, 0)
                plot_data = plot_data.cumsum()
                plot_data = plot_data[['Sam', 'Gabi', 'Reagan', 'Adrian']]
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
    cols[1].pyplot(fig)

elif menu == 'Ongoing Dynasties':
    st.header('Ongoing Dynasties')
    data = fraction_dict['Game'].copy()
    data = data.melt(ignore_index = False)
    data = data[data['value'] == 1].reset_index()
    data = data.groupby('Winner')['Game Title'].apply(list)
    data = data[['Sam', 'Gabi', 'Reagan']]
    cols = st.columns(3)
    for i in range(data.shape[0]):
        dynasty_string = ''
        player = data.index[i]
        cols[i].header(player)
        gplayed_temp = pd.Series(gplayed_dict_overall['Game']).loc[data[player]].sort_values(ascending = False)
        for game in gplayed_temp.index:
            if gplayed_temp[game] >= 2:
                dynasty_string = dynasty_string + f"{game} ({gplayed_temp[game]})\n"
        cols[i].text(dynasty_string)
            #st.text(f'{player}: {data[player]}')
else:
    st.header('"You are Due": Winless Games')
    data = fraction_dict['Game'].copy()
    data = data.melt(ignore_index = False)
    data = data[data['value'] == 0].reset_index()
    data = data.groupby('Winner')['Game Title'].apply(list)
    data = data[['Sam', 'Gabi', 'Reagan']]
    cols = st.columns(3)
    for i in range(data.shape[0]):
        dynasty_string = ''
        player = data.index[i]
        cols[i].header(player)
        gplayed_temp = pd.Series(gplayed_dict_overall['Game']).loc[data[player]].sort_values(ascending = False)
        for game in gplayed_temp.index:
            if gplayed_temp[game] >= 2:
                dynasty_string = dynasty_string + f"{game} ({gplayed_temp[game]})\n"
        cols[i].text(dynasty_string)
            #st.text(f'{player}: {data[player]}')
