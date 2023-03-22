import pandas as pd 
import streamlit as st
from shillelagh.backends.apsw.db import connect

@st.cache(ttl = 600)
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
	results = pd.DataFrame(sheets_query, columns = ['Date', 'Semester', 'Game Title', 'Winner', 'Play Time (min)', 'Scores', 'Game-specific Notes', 'Location'])
	return results
	
def processCategories(data, category_type = 'Game Type'):
	data = data.dropna(subset = category_type)
	data[category_type] = data[category_type].apply(lambda x: x.split(','))
	data = data.explode(category_type)
	data[category_type] = data[category_type].apply(lambda x: x.strip(' '))
	return data
	
	
def loadData_categories():
    #read in categories spreadsheet
	sheets_query = runQuery(st.secrets['category_url'])
	results = pd.DataFrame(sheets_query, columns = ['Data of Entry', 'Game Title', 'Owner', 'Format', 'Type', 'Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism', 'BGG Rating', 'BGG Weight', "Sams Ratings", 'Gabis Ratings', 'Reagans Ratings'])
	st.session_state['Categories'] = results.copy()
	
	#establish owner dataframe
	st.session_state['Owner'] = results[['Game Title', 'Owner']]
	
	#establish format dataframe
	col = 'Format'
	st.session_state['Format'] = processCategories(results[['Game Title', col]], col)
	
	#establish type dataframe
	col = 'Type'
	st.session_state['Type'] = processCategories(results[['Game Title', col]],col)
	
	#establish theme dataframe
	col = 'Theme'
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
    columns = ['Date of Entry', 'Name','Rummikub', 'Trial by Trolley','Sequence', 'Galaxy Trucker', 'Rat-a-tat Cat', 'Quacks of Quedlinberg', 'Uno', 'Phase 10', 'Goat Lords', 'Taboo', 'Qwixx', 'Smart Ass', 'Anomia', 'Spades', 'President', 'ERS', 'Love Letter', 'Codenames', 'Peptide', 'Hangry', "That's Pretty Clever", '5 Second Rule', 'Exploding Kittens', 'Llamas Unleashed', 'Carcassonne', 'Uno Flip', 'Bananagrams', 'Betrayal at the House on the Hill', 'Blokus', 'Azul', 'Calico', 'Unearth', 'Hearts', 'Dominion', 'Happy Little Dinosaurs', 'Balderdash', 'Pictionary', 'Sushi Go Dice', 'Fairy Tale', 'Settlers of Catan', '5 Alive', 'Poetry for Neanderthals', 'Least count', "King's in the Corner", 'Infinity Gauntlet', 'Ten', 'Silver and Gold', 'King of Tokyo', 'Five Crowns', 'Long Shot', 'Bloom', 'Forbidden Desert', 'The Initiative', 'Horrified', 'Hanabi', 'Arkham Horror', 'Mysterium', 'Control', 'Coup', 'Jenga', 'Tower of Arkhanos', 'Dune', 'The Crew:Quest for Planet Nine', 'Superfight']
    results = pd.DataFrame(sheets_query, columns = columns)
    results = results.sort_values(by = 'Date of Entry', ascending = False)
    results_trim = []
    for name in results['Name'].unique():
        results_trim.append(results[results['Name'] == name].iloc[0])
    results_trim = pd.concat(results_trim, axis = 1)
    results_trim.columns = results_trim.loc['Name']
    results_trim = results_trim.drop(['Date of Entry','Name'])
    return results_trim



def processResults(data, overall_only = False):
	scores_dict = {}
	gplayed_dict = {}
	fraction_dict = {}
	pae_dict = {}
	tmp_data = data.copy()
	games_played = tmp_data.groupby('Game Title').size()
	games_played = games_played.astype(int)
	games_played.name = 'Number of Plays'
	#explode dataframe to separate winners when there were multiple
	tmp_data['Winner'] = tmp_data['Winner'].apply(lambda x: x.split(';'))
	tmp_data = tmp_data.explode('Winner')
	overall_scores = tmp_data.groupby(['Game Title', 'Winner']).size().reset_index()
	overall_scores = overall_scores.pivot(columns = 'Winner', index = 'Game Title', values = 0)
	
	overall_fraction = overall_scores.sum()/games_played.sum()
	#get game-specific results
	scores_dict['Game'] = overall_scores
	gplayed_dict['Game'] = games_played
	fraction_dict['Game'] = getFraction(overall_scores, games_played)
	pae_dict['Game'] = getPercentageAboveExpected(fraction_dict['Game'], overall_fraction)
	if not overall_only:
		#get owner specific results
		scores_dict['Owner'], gplayed_dict['Owner'], fraction_dict['Owner'], pae_dict['Owner'] = getDictionaries('Owner', 'Owner', overall_scores, games_played, overall_fraction)
		
		#get format specific results
		scores_dict['Format'], gplayed_dict['Format'], fraction_dict['Format'], pae_dict['Format'] = getDictionaries('Format', 'Format', overall_scores, games_played, overall_fraction)
		
		#get type specific results
		scores_dict['Type'], gplayed_dict['Type'], fraction_dict['Type'], pae_dict['Type'] = getDictionaries('Type', 'Type', overall_scores, games_played, overall_fraction)
		
		#get theme specific results
		scores_dict['Theme'], gplayed_dict['Theme'], fraction_dict['Theme'], pae_dict['Theme'] = getDictionaries('Theme', 'Theme', overall_scores, games_played, overall_fraction)
		
		#get BGG type
		scores_dict['BGG Type'], gplayed_dict['BGG Type'], fraction_dict['BGG Type'], pae_dict['BGG Type'] = getDictionaries('BGG Type', 'BGG Type', overall_scores, games_played, overall_fraction)
		
		#get BGG category
		scores_dict['BGG Category'], gplayed_dict['BGG Category'], fraction_dict['BGG Category'], pae_dict['BGG Category'] = getDictionaries('BGG Category', 'BGG Category', overall_scores, games_played, overall_fraction)
		
		#get BGG mechanism
		scores_dict['BGG Mechanism'], gplayed_dict['BGG Mechanism'], fraction_dict['BGG Mechanism'], pae_dict['BGG Mechanism'] = getDictionaries('BGG Mechanism', 'BGG Mechanism',overall_scores, games_played, overall_fraction)
		
		#get location specific results
		location_scores = tmp_data.groupby(['Winner', 'Location']).size().reset_index()
		location_scores = location_scores.pivot(columns = 'Winner', index = 'Location', values = 0)
		location_gplayed = data.groupby(['Location']).size()
		scores_dict['Location'] = location_scores
		gplayed_dict['Location'] = location_gplayed
		fraction_dict['Location'] = getFraction(location_scores, location_gplayed)
		pae_dict['Location'] = getPercentageAboveExpected(fraction_dict['Location'], overall_fraction)
	
	return scores_dict, gplayed_dict, fraction_dict, pae_dict
	
	
def getDictionaries(key, col, overall_scores, games_played, overall_fraction):
	scores = st.session_state[key].merge(overall_scores, on = 'Game Title').groupby(col).sum()
	gplayed = st.session_state[key].merge(games_played, left_on = 'Game Title', right_index = True).groupby(col).sum()['Number of Plays']
	fraction = getFraction(scores, gplayed)
	pae = getPercentageAboveExpected(fraction, overall_fraction)
	return scores, gplayed, fraction, pae
	
def getFraction(scores, games_played):
	fraction = scores.copy()
	for col in fraction.columns:
		fraction[col] = fraction[col]/games_played
	return fraction
	
def getPercentageAboveExpected(fraction, overall_fraction):
	pm = fraction.copy()
	for col in pm.columns:
		pm[col] = pm[col] - overall_fraction[col]
	return pm