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
	results = pd.DataFrame(sheets_query, columns = ['Date', 'Semester', 'Game Title', 'Winner', 'Play Time (min)', 'Scores', 'Game-specific Notes'])
	return results
	
def processCategories(data, category_type = 'Game Type'):
	data = data.dropna(subset = category_type)
	data[category_type] = data[category_type].apply(lambda x: x.split(','))
	data = data.explode(category_type)
	data[category_type] = data[category_type].apply(lambda x: x.strip(' '))
	return data
	
	
def loadData_categories():
	sheets_query = runQuery(st.secrets['category_url'])
	results = pd.DataFrame(sheets_query, columns = ['Data of Entry', 'Game Title', 'Game Owner', 'Game Format', 'Game Type', 'Theme'])
	
	#establish owner dataframe
	st.session_state['Owner'] = results[['Game Title', 'Game Owner']]
	
	#establish format dataframe
	col = 'Game Format'
	st.session_state['Format'] = processCategories(results[['Game Title', col]], col)
	
	#establish type dataframe
	col = 'Game Type'
	st.session_state['Type'] = processCategories(results[['Game Title', col]],col)
	
	#establish theme dataframe
	col = 'Theme'
	st.session_state[col] = processCategories(results[['Game Title', col]],col)

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
		owner_scores = st.session_state['Owner'].merge(overall_scores, on = 'Game Title').groupby('Game Owner').sum()
		owner_gplayed = st.session_state['Owner'].merge(games_played, left_on = 'Game Title', right_index = True).groupby('Game Owner').sum()['Number of Plays']
		scores_dict['Owner'] = owner_scores
		gplayed_dict['Owner'] = owner_gplayed
		fraction_dict['Owner'] = getFraction(owner_scores, owner_gplayed)
		pae_dict['Owner'] = getPercentageAboveExpected(fraction_dict['Owner'], overall_fraction)
		
		#get format specific results
		format_scores = st.session_state['Format'].merge(overall_scores, on = 'Game Title').groupby('Game Format').sum()
		format_gplayed = st.session_state['Format'].merge(games_played, left_on = 'Game Title', right_index = True).groupby('Game Format').sum()['Number of Plays']
		scores_dict['Format'] = format_scores
		gplayed_dict['Format'] = format_gplayed
		fraction_dict['Format'] = getFraction(format_scores, format_gplayed)
		pae_dict['Format'] = getPercentageAboveExpected(fraction_dict['Format'], overall_fraction)
		
		#get type specific results
		type_scores = st.session_state['Type'].merge(overall_scores, on = 'Game Title').groupby('Game Type').sum()
		type_gplayed = st.session_state['Type'].merge(games_played, left_on = 'Game Title', right_index = True).groupby('Game Type').sum()['Number of Plays']
		scores_dict['Type'] = type_scores
		gplayed_dict['Type'] = type_gplayed
		fraction_dict['Type'] = getFraction(type_scores, type_gplayed)
		pae_dict['Type'] = getPercentageAboveExpected(fraction_dict['Type'], overall_fraction)
		
		#get theme specific results
		theme_scores = st.session_state['Theme'].merge(overall_scores, on = 'Game Title').groupby('Theme').sum()
		theme_gplayed = st.session_state['Theme'].merge(games_played, left_on = 'Game Title', right_index = True).groupby('Theme').sum()['Number of Plays']
		scores_dict['Theme'] = theme_scores
		gplayed_dict['Theme'] = theme_gplayed
		fraction_dict['Theme'] = getFraction(theme_scores, theme_gplayed)
		pae_dict['Theme'] = getPercentageAboveExpected(fraction_dict['Theme'], overall_fraction)
	
	return scores_dict, gplayed_dict, fraction_dict, pae_dict
	
	
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