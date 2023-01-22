import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st



def win_fraction_barplot(fraction_by_game, overall_fraction, games_played):
	fig, ax = plt.subplots(figsize = (10,6), nrows = 3, sharex = 'col', sharey = 'all')
	for p in range(3):
		name = fraction_by_game.columns[p]
		ax[p].bar(fraction_by_game.index,fraction_by_game[name])
		ax[p].axhline(overall_fraction[name], linestyle = 'dashed', color = 'red')
		ax[p].set_ylabel('Win Fraction')
		ax[p].set_ylim([0,1])
		ticks = plt.xticks(rotation = 90)
		ax[p].set_title(name)
		for i in range(fraction_by_game.shape[0]):
			index = fraction_by_game.index[i]
			ax[p].annotate(int(games_played[index]), (i, fraction_by_game.loc[index,name]), ha = 'center')
			
	return fig
	
	
def win_heatmap(fraction_dict, pae_dict, category = 'Game', metric = 'Win Fraction'):
	if category == 'Game':
		fig = plt.figure(figsize = (2,6))
	else:
		fig = plt.figure(figsize = (2,6))
		
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
	return fig