import streamlit as st
import pandas as pd
import numpy as np
from cycler import cycler
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from dataLoader import loadData_ratings, processResults, loadData_categories, loadData_results

if 'Full Data' not in st.session_state:
    st.session_state['Full Data'] = loadData_results()
    
if 'Type' not in st.session_state:
    loadData_categories()
    
if 'Rating' not in st.session_state:
    st.session_state['Ratings'] = loadData_ratings()

#st.write(mpl.rcParams.keys())
#mpl.rcParams['axes.edgecolor'] = 'white'
#mpl.rcParams['axes.labelcolor'] = 'white'
#mpl.rcParams['axes.facecolor'] = 'white'
#mpl.rcParams['axes.prop_cycle'] = cycler('color', ['#001C7F', '#017517', '#8C0900', '#7600A1', '#B8860B', '#006374'])
#mpl.rcParams['grid.color'] = 'white'
#mpl.rcParams['xtick.color'] = 'white'
#mpl.rcParams['ytick.color'] = 'white'
#mpl.rcParams['axes.grid'] = False
#mpl.rcParams['savefig.transparent'] = False
#mpl.rcParams['savefig.edgecolor'] = 'white'
#mpl.rcParams['lines.color'] = 'white'
#mpl.rcParams['patch.edgecolor'] = 'gray'
#mpl.rcParams['axes.titlecolor'] = 'white'
#mpl.rcParams['figure.edgecolor'] = 'white'
#mpl.rcParams['legend.facecolor'] = 'white'



unique_games = np.sort(st.session_state['Full Data']['Game Title'].unique())
game_to_explore = st.selectbox('Pick a game to explore:', unique_games)

game_data = st.session_state['Full Data'].copy()
game_data = game_data[game_data['Game Title'] == game_to_explore]
games_with_scores = game_data.dropna(subset = 'Scores')
games_with_scores = pd.DataFrame(games_with_scores['Scores'].apply(lambda x: x.split(';')).explode()).reset_index()
games_with_scores['Player'] = games_with_scores['Scores'].apply(lambda x: x.split('=')[0])
games_with_scores['Score'] = games_with_scores['Scores'].apply(lambda x: x.split('=')[1])
games_with_scores['Score'] = games_with_scores['Score'].astype(int)
scores_dict, gplayed_dict, fraction_dict, pae_dict = processResults(game_data)

number_of_wins = scores_dict['Game'].T
most_wins = np.max(number_of_wins.values)
person_winner = number_of_wins[number_of_wins[game_to_explore] == most_wins]
if person_winner.shape[0] > 1:
    most_wins_player = ','.join(person_winner.index.values)
else:
    most_wins_player = person_winner.index.values[0]
    
#if games_with_scores.shape[0] > 0:
#    cols = st.columns(3)
#    cols[0].metric('Number of Times Played', game_data.shape[0], delta = None)
#    cols[1].metric('Person with Most Wins', f'{most_wins_player} ({most_wins})', delta = None)
#    golf_games = ['Blokus', 'Hearts']
#    if game_to_explore in golf_games:
#        index_best_score = games_with_scores['Score'].idxmin()
#    else:
#        index_best_score = games_with_scores['Score'].idxmax()
#    best_score = games_with_scores.loc[index_best_score, 'Score']
#    person_with_best_score = games_with_scores.loc[index_best_score, 'Player']
#    cols[2].metric('Best Score', f'{best_score} ({person_with_best_score})', delta = None)
#else:
#    cols = st.columns(2)
#    cols[0].metric('Number of Times Played', game_data.shape[0], delta = None)
#    cols[1].metric('Person with Most Wins', f'{most_wins_player} ({most_wins})', delta = None)
st.header('Summary Statistics')
cols = st.columns(2)
cols[0].metric('Number of Times Played', game_data.shape[0], delta = None)
cols[1].metric('Person with Most Wins', f'{most_wins_player} ({most_wins})', delta = None)
if games_with_scores.shape[0] > 0:
    cols = st.columns(2)
    golf_games = ['Blokus', 'Hearts', "Bananagrams"]
    if game_to_explore in golf_games:
        index_best_score = games_with_scores['Score'].idxmin()
    else:
        index_best_score = games_with_scores['Score'].idxmax()
    best_score = games_with_scores.loc[index_best_score, 'Score']
    person_with_best_score = games_with_scores.loc[index_best_score, 'Player']
    cols[1].metric('Best Score', f'{best_score} ({person_with_best_score})', delta = None)
#cols[1].header('Person with Most Wins')
#cols[2].header('Best Score')


#how the game is rated
st.header('Game Ratings')
st.subheader('Board Game Geek')
cols = st.columns(2)
game_data = st.session_state['Categories'][st.session_state['Categories']['Game Title'] == game_to_explore].squeeze()
cols[0].metric('BGG Rating', game_data['BGG Rating'], delta = None)
cols[1].metric('BGG Complexity (Out of 5)', game_data['BGG Weight'], delta = None)

st.subheader('Our Ratings')
st.metric('Consensus', round(st.session_state['Ratings'].loc[game_to_explore].mean(), 2), delta = None)
cols = st.columns(3)
cols[0].metric("Sam's Rating", st.session_state['Ratings'].loc[game_to_explore, 'Sam'], delta = None)
cols[1].metric("Gabi's Rating", st.session_state['Ratings'].loc[game_to_explore, 'Gabi'], delta = None)
cols[2].metric("Reagan's Rating", st.session_state['Ratings'].loc[game_to_explore, 'Reagan'], delta = None)



#results from game
if games_with_scores.shape[0] > 0:
    st.header('Scores')
    divy_by_player = st.checkbox('Break up by Player')
    show_line = st.checkbox('Show estimated distribution')
    metric = st.selectbox('Metric to display:', ['probability', 'count'])
    if divy_by_player:
        separate = st.checkbox('Seperate plots for each player')
        if separate:
            fig, ax = plt.subplots(ncols = games_with_scores['Player'].nunique(), sharey = 'all', sharex = 'all')
            ax[0].set_ylabel('Number of Games')
            players = games_with_scores['Player'].unique()
            for p in range(len(players)):
                player = players[p]
                plt_data = games_with_scores.loc[games_with_scores['Player'] == player]
                sns.histplot(data = plt_data, x = 'Score', ax = ax[p], kde = show_line)
                ax[p].set_title(players[p])
        else:
            fig = plt.figure()
            if show_line:
                sns.histplot(data = games_with_scores, x = 'Score', hue = 'Player', stat = metric, kde = show_line, element = 'step', alpha = 0.2, edgecolor = None)
            else:
                sns.histplot(data = games_with_scores, x = 'Score', hue = 'Player', stat = metric, kde = show_line, element = 'step', alpha = 0.2, edgecolor = None)
    else:
        fig = plt.figure()
        sns.histplot(data = games_with_scores, x = 'Score', stat = metric, kde = show_line)
    
    st.pyplot(fig)
    
    
#how game is classified
st.header('How the game is classified')

st.markdown(f"**Person who owns the game:** {st.session_state['Owner'].loc[st.session_state['Owner']['Game Title'] == game_to_explore, 'Owner'].values[0]}")

game_format = ', '.join(st.session_state['Format'].loc[st.session_state['Format']['Game Title'] == game_to_explore, 'Format'].values)
st.markdown(f"**Game Format:** {game_format}")

st.markdown(f"**Size of the teams:** {st.session_state['Team Size'].loc[st.session_state['Team Size']['Game Title'] == game_to_explore, 'Team Size'].values[0]}")

primary_class = st.session_state['Primary Classification'].loc[st.session_state['Primary Classification']['Game Title'] == game_to_explore, 'Primary Classification']
if primary_class.shape[0] > 0:
    st.markdown(f"**Primary Classification:** {primary_class.values[0]}")

st.markdown(f"**Average game length:** {st.session_state['Game Length'].loc[st.session_state['Game Length']['Game Title'] == game_to_explore, 'Game Length'].values[0]}")

game_type = ', '.join(st.session_state["Sam's Mechanisms"].loc[st.session_state["Sam's Mechanisms"]["Game Title"] == game_to_explore, "Sam's Mechanisms"].values)
st.markdown(f"**Game Type(s):** {game_type}")

game_themes = ', '.join(st.session_state['Theme'].loc[st.session_state['Theme']['Game Title'] == game_to_explore, 'Theme'].values)
st.markdown(f"**Game Theme(s):** {game_themes}")

bgg_type = ', '.join(st.session_state['BGG Type'].loc[st.session_state['BGG Type']['Game Title'] == game_to_explore, 'BGG Type'].values)
st.markdown(f"**Board Game Geek Type(s):** {game_themes}")

bgg_cat = ', '.join(st.session_state['BGG Category'].loc[st.session_state['BGG Category']['Game Title'] == game_to_explore, 'BGG Category'].values)
st.markdown(f"**Board Game Geek Categories:** {bgg_cat}")

bgg_mech = ', '.join(st.session_state['BGG Mechanism'].loc[st.session_state['BGG Mechanism']['Game Title'] == game_to_explore, 'BGG Mechanism'].values)
st.markdown(f"**Board Game Geek Mechanism(s):** {bgg_mech}")