import pandas as pd 
import numpy as np
import streamlit as st
from shillelagh.backends.apsw.db import connect

@st.cache_data(ttl = 600)
def runQuery(sheets_link):
    connection = connect(":memory:", adapters = 'gsheetsapi')
    cursor = connection.cursor()
    
    query = f'SELECT * FROM "{sheets_link}"'

    query_results = []
    for row in cursor.execute(query):
        query_results.append(row)
    return query_results

def loadData_results():
    sheets_query = runQuery(st.secrets['results_url'])
    results = pd.DataFrame(sheets_query, columns = ['Date', 'Semester', 'Game Title', 'Winner', 'Play Time (min)', 'Scores', 'Game-specific Notes', 'Location', 'First Player', 'Players'])
    return results
    
def processCategories(data, category_type = 'Game Type'):
    data = data.dropna(subset = category_type).copy()
    if data[category_type].dtypes != str:
        data[category_type] = data[category_type].astype(str)
    data[category_type] = data[category_type].apply(lambda x: x.split(','))
    data = data.explode(category_type)
    data[category_type] = data[category_type].apply(lambda x: x.strip(' '))
    return data
    
    
def loadData_categories():
    #read in categories spreadsheet
    sheets_query = runQuery(st.secrets['category_url'])
    results = pd.DataFrame(sheets_query, columns = ['Data of Entry', 'Game Title', 'Owner', 'Format', "Sam's Mechanisms", 'Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism', 'BGG Rating', 'BGG Weight', 'Primary Classification', 'Team Size', 'Game Length', 'Win Condition', 'Luck Score'])
    st.session_state['Categories'] = results.copy()
    
    #establish owner dataframe
    st.session_state['Owner'] = results[['Game Title', 'Owner']]
    
    #establish format dataframe
    col = 'Format'
    st.session_state['Format'] = processCategories(results[['Game Title', col]], col)
    
        #establish format dataframe
    col = 'Primary Classification'
    st.session_state['Primary Classification'] = processCategories(results[['Game Title', col]], col)
    
            #establish length dataframe
    col = 'Game Length'
    st.session_state[col] = processCategories(results[['Game Title', col]], col)
    
                #establish length dataframe
    col = 'Team Size'
    st.session_state[col] = processCategories(results[['Game Title', col]], col)
    
    #establish type dataframe
    col = "Sam's Mechanisms"
    st.session_state[col] = processCategories(results[['Game Title', col]],col)
    
    #establish theme dataframe
    col = 'Theme'
    st.session_state[col] = processCategories(results[['Game Title', col]],col)
    
    #establish BGG mechanism dataframe
    col = 'Win Condition'
    st.session_state[col] = processCategories(results[['Game Title', col]],col)
    
    #establish BGG mechanism dataframe
    col = 'Luck Score'
    st.session_state[col] = processCategories(results[['Game Title', col]],col)
    
    
    #establish BGG type dataframe
    col = 'BGG Type'
    st.session_state[col] = processCategories(results[['Game Title', col]],col)
        
    #establish BGG category dataframe
    col = 'BGG Category'
    st.session_state[col] = processCategories(results[['Game Title', col]],col)
        
    #establish BGG mechanism dataframe
    col = 'BGG Mechanism'
    st.session_state[col] = processCategories(results[['Game Title', col]],col)


def loadData_ratings():
    #read in ratings
    sheets_query = runQuery(st.secrets['ratings_url'])
    columns = ['Date of Entry', 'Name','Rummikub', 'Trial by Trolley','Sequence', 'Galaxy Trucker', 'Rat-a-tat Cat', 'Quacks of Quedlinberg', 'Uno', 'Phase 10', 'Goat Lords', 'Taboo', 'Qwixx', 'Smart Ass', 'Anomia', 'Spades', 'President', 'ERS', 'Love Letter', 'Codenames', 'Peptide', 'Hangry', "That's Pretty Clever", '5 Second Rule', 'Exploding Kittens', 'Llamas Unleashed', 'Carcassonne', 'Uno Flip', 'Bananagrams', 'Betrayal at the House on the Hill', 'Blokus', 'Azul', 'Calico', 'Unearth', 'Hearts', 'Dominion', 'Happy Little Dinosaurs', 'Balderdash', 'Pictionary', 'Sushi Go Dice', 'Fairy Tale', 'Settlers of Catan', '5 Alive', 'Poetry for Neanderthals', 'Least count', "Kings in the Corner", 'Infinity Gauntlet', 'Ten', 'Silver and Gold', 'King of Tokyo', 'Five Crowns', 'Long Shot', 'Bloom', 'Forbidden Desert', 'The Initiative', 'Horrified', 'Hanabi', 'Arkham Horror', 'Mysterium', 'Control', 'Coup', 'Jenga', 'Towers of Arkhanos', 'Dune', 'The Crew: Quest for Planet Nine', 'Superfight', 'Happy Salmon', 'Hand-to-Hand Wombat',
    'The Search for Planet X', 'Doomlings', 'Sagrada', 'Take 5', 'Sushi Go!', 'Gloomhaven: Jaws of the Lion', 'Dixit', 'Nova Luna', 'Railroad Ink', 'Isle of Cats', 'Akropolis', 'SkyJo', 'Arboretum', 'SCOUT', 'Cat in the Box', 'Earth', 'Celestia','Spires','Clever 4Ever', 'Welcome to the Moon', 'Decrypto']
    results = pd.DataFrame(sheets_query, columns = columns)
    results = results.sort_values(by = 'Date of Entry', ascending = False)
    results_trim = []
    for name in results['Name'].unique():
        results_trim.append(results[results['Name'] == name].iloc[0])
    results_trim = pd.concat(results_trim, axis = 1)
    results_trim.columns = results_trim.loc['Name']
    results_trim = results_trim.drop(['Date of Entry','Name'])
    return results_trim

def loadData_trivia():
    #read in ratings
    sheets_query = runQuery(st.secrets['trivia_url'])
    columns = ['Date of Entry', 'Trivia Date', 'Semester', 'Players', 'Number of Teams', 'Current Events: Topic', 'Current Events: Score', 'Music Round: Topic', 'Music Round: Score', 'Pop culture: Topic', 'Pop culture: Score', '3rd Place Pick: Topic', '3rd Place Pick: Score', 'Random Knowledge: Score', 'List Topic', 'List Score', 'Place']
    results = pd.DataFrame(sheets_query, columns = columns)
    results = results.sort_values(by = 'Date of Entry', ascending = True)
    return results

def processResults(data, overall_only = False):
    scores_dict = {}
    gplayed_overall_dict = {}
    gplayed_player_dict = {}
    fraction_dict = {}
    pae_dict = {}
    par_dict = {}
    tmp_data = data.copy()
    #games played
    games_played_overall = tmp_data.groupby('Game Title').size()
    games_played_overall = games_played_overall.astype(int)
    games_played_overall.name = 'Number of Plays'
    #separate out players
    tmp_data['Players'] = tmp_data['Players'].apply(lambda x: x.split(';'))
    tmp_data = tmp_data.explode('Players')
    games_played_player = tmp_data.groupby(['Players', 'Game Title']).size()
    games_played_player = games_played_player.astype(int)
    games_played_player.name = 'Number of Plays'
    games_played_player = games_played_player.reset_index().pivot(columns = 'Players', index = 'Game Title', values = 'Number of Plays')
    games_played_player = games_played_player.replace(np.nan, 0)
    #explode dataframe to separate winners when there were multiple
    tmp_data['Winner'] = tmp_data['Winner'].apply(lambda x: x.split(';'))
    tmp_data = tmp_data.explode('Winner')
    #get rid of rows where winner does not match player
    tmp_data = tmp_data[tmp_data['Players'] == tmp_data['Winner']]
    #count the number of wins for each game and each player
    overall_scores = tmp_data.groupby(['Game Title', 'Winner']).size().reset_index()
    overall_scores = overall_scores.pivot(columns = 'Winner', index = 'Game Title', values = 0)
    overall_scores = overall_scores.replace(np.nan, 0)
    #get overall win fraction for each player
    overall_fraction = overall_scores.sum()/games_played_player.sum()
    #get game-specific results
    scores_dict['Game'] = overall_scores
    gplayed_overall_dict['Game'] = games_played_overall
    gplayed_player_dict['Game'] = games_played_player
    fraction_dict['Game'] = getFraction(overall_scores, games_played_player)
    pae_dict['Game'] = getPercentageAboveExpected(fraction_dict['Game'], overall_fraction)
    par_dict['Game'] = getPercentageAboveRandom(fraction_dict['Game'])
    if not overall_only:
        #get owner specific results
        scores_dict['Owner'], gplayed_overall_dict['Owner'], gplayed_player_dict['Owner'], fraction_dict['Owner'], pae_dict['Owner'], par_dict['Owner'] = getDictionaries('Owner', 'Owner', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get format specific results
        scores_dict['Format'], gplayed_overall_dict['Format'], gplayed_player_dict['Format'], fraction_dict['Format'], pae_dict['Format'], par_dict['Format'] = getDictionaries('Format', 'Format', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
                #get primary classification specific results
        scores_dict['Primary Classification'], gplayed_overall_dict['Primary Classification'], gplayed_player_dict['Primary Classification'], fraction_dict['Primary Classification'], pae_dict['Primary Classification'], par_dict['Primary Classification'] = getDictionaries('Primary Classification', 'Primary Classification', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
                        #get primary classification specific results
        scores_dict['Game Length'], gplayed_overall_dict['Game Length'], gplayed_player_dict['Game Length'], fraction_dict['Game Length'], pae_dict['Game Length'], par_dict['Game Length'] = getDictionaries('Game Length', 'Game Length', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get team size specific results
        scores_dict['Team Size'], gplayed_overall_dict['Team Size'], gplayed_player_dict['Team Size'], fraction_dict['Team Size'], pae_dict['Team Size'], par_dict['Team Size'] = getDictionaries('Team Size', 'Team Size', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get type specific results
        scores_dict["Sam's Mechanisms"], gplayed_overall_dict["Sam's Mechanisms"], gplayed_player_dict["Sam's Mechanisms"],fraction_dict["Sam's Mechanisms"], pae_dict["Sam's Mechanisms"], par_dict["Sam's Mechanisms"] = getDictionaries("Sam's Mechanisms", "Sam's Mechanisms", overall_scores, games_played_overall, games_played_player, overall_fraction)
        
                
        #get win condition specific results
        scores_dict["Win Condition"], gplayed_overall_dict['Win Condition'], gplayed_player_dict['Win Condition'], fraction_dict["Win Condition"], pae_dict["Win Condition"], par_dict['Win Condition'] = getDictionaries("Win Condition", "Win Condition", overall_scores, games_played_overall, games_played_player, overall_fraction)
        
                        
        #get luck score specific results
        scores_dict["Luck Score"], gplayed_overall_dict['Luck Score'], gplayed_player_dict['Luck Score'], fraction_dict["Luck Score"], pae_dict["Luck Score"], par_dict['Luck Score'] = getDictionaries("Luck Score", "Luck Score", overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get theme specific results
        scores_dict['Theme'], gplayed_overall_dict['Theme'], gplayed_player_dict['Them'], fraction_dict['Theme'], pae_dict['Theme'], par_dict['Theme'] = getDictionaries('Theme', 'Theme', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get BGG type
        scores_dict['BGG Type'], gplayed_overall_dict['BGG Type'], gplayed_player_dict['BGG Type'], fraction_dict['BGG Type'], pae_dict['BGG Type'], par_dict['BGG Type'] = getDictionaries('BGG Type', 'BGG Type', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get BGG category
        scores_dict['BGG Category'], gplayed_overall_dict['BGG Category'], gplayed_player_dict['BGG Category'], fraction_dict['BGG Category'], pae_dict['BGG Category'], par_dict['BGG Category'] = getDictionaries('BGG Category', 'BGG Category', overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get BGG mechanism
        scores_dict['BGG Mechanism'], gplayed_overall_dict['BGG Mechanism'], gplayed_player_dict['BGG Mechanism'], fraction_dict['BGG Mechanism'], pae_dict['BGG Mechanism'], par_dict['BGG Mechanism'] = getDictionaries('BGG Mechanism', 'BGG Mechanism',overall_scores, games_played_overall, games_played_player, overall_fraction)
        
        #get location specific results
        location_scores = tmp_data.groupby(['Winner', 'Location']).size().reset_index()
        location_scores = location_scores.pivot(columns = 'Winner', index = 'Location', values = 0)
        #get gamesplayed per location
        player_data = data.copy()
        player_data['Players'] = player_data['Players'].apply(lambda x: x.split(';'))
        player_data = player_data.explode('Players')
        #get games played at each location
        location_gplayed = player_data.groupby(['Players','Location']).size()
        location_gplayed = location_gplayed.astype(int)
        location_gplayed.name = 'Number of Plays'
        location_gplayed = location_gplayed.reset_index().pivot(columns = 'Players', index = 'Location', values = 'Number of Plays')
        scores_dict['Location'] = location_scores
        gplayed_player_dict['Location'] = location_gplayed
        gplayed_overall_dict['Location'] = data.groupby('Location').size()
        fraction_dict['Location'] = getFraction(location_scores, location_gplayed)
        pae_dict['Location'] = getPercentageAboveExpected(fraction_dict['Location'], overall_fraction)
        par_dict['Location'] = getPercentageAboveRandom(fraction_dict['Location'])
    
    return scores_dict, gplayed_overall_dict, gplayed_player_dict, fraction_dict, pae_dict, par_dict
    
    
def getDictionaries(key, col, overall_scores, games_played_overall, games_played_player, overall_fraction):
    scores = st.session_state[key].merge(overall_scores, on = 'Game Title').groupby(col).sum(numeric_only = True)
    #scores = scores.drop('Game Title', axis = 1)
    gplayed_overall = st.session_state[key].merge(games_played_overall, left_on = 'Game Title', right_index = True).groupby(col).sum()
    gplayed_player = st.session_state[key].merge(games_played_player, on = 'Game Title').groupby(col).sum(numeric_only = True)
    fraction = getFraction(scores, gplayed_player)
    pae = getPercentageAboveExpected(fraction, overall_fraction)
    par = getPercentageAboveRandom(fraction)
    return scores, gplayed_overall, gplayed_player, fraction, pae, par
    
def getFraction(scores, games_played):
    fraction = scores.copy()
    for col in fraction.columns:
        fraction[col] = fraction[col].astype(float)/games_played[col]
    return fraction

def getPercentageAboveRandom(fraction):
    pm = fraction.copy()
    for col in pm.columns:
        pm[col] = pm[col] - 1/3
    return pm
    
def getPercentageAboveExpected(fraction, overall_fraction):
    pm = fraction.copy()
    for col in pm.columns:
        pm[col] = pm[col] - overall_fraction[col]
    return pm