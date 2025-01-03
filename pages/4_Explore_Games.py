import streamlit as st
import pandas as pd
import numpy as np
from cycler import cycler
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import hydralit_components as hc
from dataLoader import loadData_ratings, processResults, loadData_categories, loadData_results


st.set_page_config(layout='wide')
if 'Full Data' not in st.session_state:
    st.session_state['Full Data'] = loadData_results()
    
if 'Type' not in st.session_state:
    loadData_categories()
    
if 'Rating' not in st.session_state:
    st.session_state['Ratings'] = loadData_ratings()

st.title("Explore the Games We've Played")


type_to_explore = st.radio('Explore:', ['Game', 'Category'], horizontal = True)


#add tabs
if type_to_explore == 'Game':
    unique_games = np.sort(st.session_state['Full Data']['Game'].unique())
    game_to_explore = st.selectbox('Pick a game to explore:', unique_games)

    game_data = st.session_state['Full Data'].copy()
    game_data = game_data[game_data['Game'] == game_to_explore]
    games_with_scores = game_data.dropna(subset = 'Scores')
    games_with_scores = pd.DataFrame(games_with_scores['Scores'].apply(lambda x: x.split(';')).explode()).reset_index()
    games_with_scores['Player'] = games_with_scores['Scores'].apply(lambda x: x.split('=')[0])
    games_with_scores['Score'] = games_with_scores['Scores'].apply(lambda x: x.split('=')[1])
    games_with_scores['Score'] = games_with_scores['Score'].astype(int)
    scores_dict, gplayed_dict, gplayed_dict_player, fraction_dict, pae_dict, par_dict = processResults(game_data)

    number_of_wins = scores_dict['Game'].T
    most_wins = np.max(number_of_wins.values)
    person_winner = number_of_wins[number_of_wins[game_to_explore] == most_wins]
    if person_winner.shape[0] > 1:
        most_wins_player = ','.join(person_winner.index.values)
    else:
        most_wins_player = person_winner.index.values[0]
        


    menu_data = [
        {'label':"Summary Statistics"},
        {'label':"Game Ratings"},
        {'label': "Scores (If Applicable)"},
        {'label':"Game Classifications"}
    ]
    menu = hc.nav_bar(menu_definition = menu_data, sticky_nav = True, sticky_mode = 'pinned')
    if menu == 'Summary Statistics':
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
    elif menu == 'Game Ratings':
        st.header('Game Ratings')
        st.subheader('Board Game Geek')
        cols = st.columns(2)
        game_data = st.session_state['Categories'][st.session_state['Categories']['Game'] == game_to_explore].squeeze()
        cols[0].metric('BGG Rating', game_data['BGG Rating'], delta = None)
        cols[1].metric('BGG Complexity (Out of 5)', game_data['BGG Weight'], delta = None)

        st.subheader('Our Ratings')
        st.metric('Consensus', round(st.session_state['Ratings'].loc[game_to_explore].mean(), 2), delta = None)
        cols = st.columns(3)
        cols[0].metric("Sam's Rating", st.session_state['Ratings'].loc[game_to_explore, 'Sam'], delta = None)
        cols[1].metric("Gabi's Rating", st.session_state['Ratings'].loc[game_to_explore, 'Gabi'], delta = None)
        cols[2].metric("Reagan's Rating", st.session_state['Ratings'].loc[game_to_explore, 'Reagan'], delta = None)



    #results from game
    elif menu == 'Scores (If Applicable)':
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
        else:
            st.write(f'No scores associated with {game_to_explore}')
        
        
    #how game is classified
    if menu == 'Game Classifications':
        st.header('How the game is classified')

        st.markdown(f"**Person who owns the game:** {st.session_state['Owner'].loc[st.session_state['Owner']['Game'] == game_to_explore, 'Owner'].values[0]}")

        game_format = ', '.join(st.session_state['Format'].loc[st.session_state['Format']['Game'] == game_to_explore, 'Format'].values)
        st.markdown(f"**Game Format:** {game_format}")

        st.markdown(f"**Size of the teams:** {st.session_state['Team Size'].loc[st.session_state['Team Size']['Game'] == game_to_explore, 'Team Size'].values[0]}")

        primary_class = st.session_state['Primary Classification'].loc[st.session_state['Primary Classification']['Game'] == game_to_explore, 'Primary Classification']
        if primary_class.shape[0] > 0:
            st.markdown(f"**Primary Classification:** {primary_class.values[0]}")

        st.markdown(f"**Average game length:** {st.session_state['Game Length'].loc[st.session_state['Game Length']['Game'] == game_to_explore, 'Game Length'].values[0]}")

        win_condition = ', '.join(st.session_state["Win Condition"].loc[st.session_state["Win Condition"]["Game"] == game_to_explore, "Win Condition"].values)
        st.markdown(f"**Win Condition:** {win_condition}")

        st.markdown(f"**Luck Score (1 = No Luck, 5 = All Luck):** {st.session_state['Luck Score'].loc[st.session_state['Luck Score']['Game'] == game_to_explore, 'Luck Score'].values[0]}")

        game_type = ', '.join(st.session_state["Sam's Mechanisms"].loc[st.session_state["Sam's Mechanisms"]["Game"] == game_to_explore, "Sam's Mechanisms"].values)
        st.markdown(f"**Game Type(s):** {game_type}")

        game_themes = ', '.join(st.session_state['Theme'].loc[st.session_state['Theme']['Game'] == game_to_explore, 'Theme'].values)
        st.markdown(f"**Game Theme(s):** {game_themes}")

        bgg_type = ', '.join(st.session_state['BGG Type'].loc[st.session_state['BGG Type']['Game'] == game_to_explore, 'BGG Type'].values)
        st.markdown(f"**Board Game Geek Type(s):** {game_themes}")

        bgg_cat = ', '.join(st.session_state['BGG Category'].loc[st.session_state['BGG Category']['Game'] == game_to_explore, 'BGG Category'].values)
        st.markdown(f"**Board Game Geek Categories:** {bgg_cat}")

        bgg_mech = ', '.join(st.session_state['BGG Mechanism'].loc[st.session_state['BGG Mechanism']['Game'] == game_to_explore, 'BGG Mechanism'].values)
        st.markdown(f"**Board Game Geek Mechanism(s):** {bgg_mech}")
else:
    st.write('Work in progress')
    
    category_type = st.selectbox('Category Type:', ['Owner', 'Format', 'Game Length', 'Team Size', 'Primary Classification', 'Win Condition', 'Theme', "Sam's Mechanisms", 'BGG Category', 'BGG Type', 'BGG Mechanism'])
    
    category_data = st.session_state[category_type].copy()
    
    cat_to_explore = st.selectbox('Category to Explore:', np.sort(category_data[category_type].unique()))
    category_data = category_data[category_data[category_type] == cat_to_explore]
    menu_data = [
        {'label':"Summary Statistics"},
        {'label':"Game Ratings"},
        {'label':"Games in Category"}
    ]
    menu = hc.nav_bar(menu_definition = menu_data, sticky_nav = True, sticky_mode = 'pinned')
    if menu == 'Summary Statistics':
        game_data = st.session_state['Full Data'].copy()
        game_data = game_data.merge(category_data, on = 'Game')
        scores_dict, gplayed_dict, gplayed_dict_player, fraction_dict, pae_dict, par_dict = processResults(game_data)
        scores = scores_dict['Game']
        if 'Lionel' in scores.columns:
            scores = scores.drop(columns = 'Lionel', axis = 1)
        scores = scores.melt(ignore_index = False).reset_index()


        if scores_dict['Game'].shape[0] != 0:

            number_of_wins = scores_dict['Game'].sum()
            most_wins = int(np.max(number_of_wins.values))
            person_winner = number_of_wins[number_of_wins == most_wins].index.values
            if len(person_winner) > 1:
                most_wins_player = ','.join(person_winner)
            else:
                most_wins_player = person_winner[0]
                
            #get most played game in category
            gplayed = gplayed_dict['Game']

            #st.header('Summary Statistics')
            cols = st.columns(2)
            st.write(gplayed.idxmax())
            cols[0].metric('Number of Times Played', game_data.shape[0], delta = None)
            cols[0].metric('Most Played Game in Category', f'{gplayed.idxmax()} ({gplayed.max()})', delta = None)
            cols[0].metric('Person with Most Wins', f'{most_wins_player} ({most_wins})', delta = None)
            #cols[1].header('Person with Most Wins')
            #cols[2].header('Best Score')

            #plots
            fig = plt.figure()
            sns.barplot(x = 'Game', y = 'value', hue = 'Winner', data = scores)
            plt.xticks(rotation = 90)
            plt.legend(ncols = 3)
            plt.ylabel('Number of Wins')
            plt.xlabel('')
            cols[1].pyplot(fig)


    #how the game is rated
    elif menu == 'Game Ratings':
        #st.header('Average Game Ratings')
        st.subheader('Board Game Geek')
        full_category_data = st.session_state['Categories'][st.session_state['Categories'][category_type] == cat_to_explore]
        cols = st.columns(2)
        cols[0].metric('BGG Rating', round(full_category_data['BGG Rating'].mean(), 2), delta = None)
        cols[1].metric('BGG Complexity (Out of 5)', round(full_category_data['BGG Weight'].mean(), 2), delta = None)

        st.subheader('Our Ratings')
        ratings = st.session_state['Ratings'].copy()
        games_with_ratings = [game for game in category_data['Game'].unique() if game in ratings.index]
        ratings = ratings.loc[games_with_ratings].mean()
        st.metric('Consensus', round(ratings.mean(), 2), delta = None)
        cols = st.columns(3)
        cols[0].metric("Sam's Rating", round(ratings['Sam'],2), delta = None)
        cols[1].metric("Gabi's Rating", round(ratings['Gabi'],2), delta = None)
        cols[2].metric("Reagan's Rating", round(ratings['Reagan'], 2), delta = None)

    elif menu == 'Games in Category':
        #st.header('Games in Category')
        st.write(', '.join(np.sort(category_data['Game'].unique())))