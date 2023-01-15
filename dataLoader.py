import pandas as pd 



def loadData():
	#load data
	scores_dict = {}
	gplayed_dict = {}
	fraction_dict = {}
	
	overall_scores = pd.read_csv('../OverallScore.csv',index_col = 0)
	overall_scores = overall_scores.dropna(how = 'all')
	overall_scores = overall_scores.dropna(how = 'all', axis = 1)
	games_played = overall_scores['# of games played']
	overall_scores = overall_scores.iloc[:,0:3]
	overall_scores = overall_scores.fillna(value = 0)
	overall_scores['Gabi'] = overall_scores['Gabi'].astype(int)
	scores_dict['Game'] = overall_scores
	gplayed_dict['Game'] = games_played
	fraction_dict['Game'] = getFraction(overall_scores, games_played)

	gameformat = pd.read_csv('../GameFormat.csv',index_col = 0, header = 1)
	gameformat = gameformat.dropna(how = 'all')
	gameformat = gameformat.dropna(how = 'all', axis = 1)
	gameformat = gameformat.melt(ignore_index = False)
	gameformat = gameformat.dropna(subset = 'value')
	gameformat.drop('value', axis = 1, inplace = True)
	format_scores = gameformat.merge(overall_scores, left_index = True, right_index = True)
	format_gplayed = gameformat.merge(games_played, left_index = True, right_index = True)
	format_scores = format_scores.groupby('variable').sum()
	format_gplayed = format_gplayed.groupby('variable').sum()['# of games played']
	scores_dict['Game Format'] = format_scores
	gplayed_dict['Game Format'] = format_gplayed
	fraction_dict['Game Format'] = getFraction(format_scores, format_gplayed)

	gametype = pd.read_csv('../GameTypes.csv', header = 1, index_col = 0)
	gametype = gametype.iloc[:,6:]
	gametype = gametype.replace('X', 1)
	gametype = gametype.melt(ignore_index = False)
	gametype = gametype.dropna(subset = 'value')
	gametype = gametype.drop('value', axis = 1)
	type_scores = gametype.merge(overall_scores, left_index = True, right_index = True)
	type_gplayed = gametype.merge(games_played, left_index = True, right_index = True)
	type_scores = type_scores.groupby('variable').sum()
	type_gplayed = type_gplayed.groupby('variable').sum()['# of games played']
	scores_dict['Game Type'] = type_scores
	gplayed_dict['Game Type'] = type_gplayed
	fraction_dict['Game Type'] = getFraction(type_scores, type_gplayed)
	
	gameowner = pd.read_csv('../GameOwners.csv', header = 1, index_col = 0)
	gameowner = gameowner.replace('X', 1)
	gameowner = gameowner.melt(ignore_index = False, var_name = 'Owner')
	gameowner = gameowner.dropna(subset = 'value')
	gameowner = gameowner.drop('value', axis = 1)
	owner_scores = gameowner.merge(overall_scores, left_index = True, right_index = True)
	owner_gplayed = gameowner.merge(games_played, left_index = True, right_index = True)
	owner_scores = owner_scores.groupby('Owner').sum()
	owner_gplayed = owner_gplayed.groupby('Owner').sum()['# of games played']
	scores_dict['Game Owner'] = owner_scores
	gplayed_dict['Game Owner'] = owner_gplayed
	fraction_dict['Game Owner'] = getFraction(owner_scores, owner_gplayed)
	return scores_dict, gplayed_dict, fraction_dict
	
	
def getFraction(scores, games_played):
	fraction = scores.copy()
	for col in fraction.columns:
		fraction[col] = fraction[col]/games_played
	return fraction
	
def getPercentageAboveExpected(fraction, games_played, overall_fraction):
	pm = fraction.copy()
	for col in pm.columns:
		pm[col] = pm[col] - overall_fraction[col]
	return pm