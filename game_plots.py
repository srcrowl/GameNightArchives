import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st



def win_fraction_barplot(fraction_by_game, overall_fraction, games_played, players = ['Sam', 'Gabi', 'Reagan', 'Adrian']):
	fig, ax = plt.subplots(figsize = (10,2*len(players)), nrows = len(players), sharex = 'col', sharey = 'all')
	fig.subplots_adjust(hspace = 0.5)
	if len(players) == 1:
		ax = [ax]

	for p, name in enumerate(players):
		ax[p].bar(fraction_by_game.index,fraction_by_game[name])
		#ax[p].axhline(overall_fraction[name], linestyle = 'dashed', color = 'red')
		ax[p].axhline(1/3, linestyle = 'dashed', color = 'red')
		ax[p].set_ylabel('Win Fraction')
		ax[p].set_ylim([0,1])
		ticks = plt.xticks(rotation = 90)
		ax[p].set_title(name)
		for i in range(fraction_by_game.shape[0]):
			index = fraction_by_game.index[i]
			ax[p].annotate(int(games_played.loc[index, name]), (i, fraction_by_game.loc[index,name]), ha = 'center')
			
	return fig
	
	
def win_heatmap(plot_dict, games = None, category = 'Game', metric = 'Win Fraction', players = ['Sam', 'Gabi', 'Reagan', 'Adrian']):
	if category == 'Game':
		fig = plt.figure(figsize = (2.5,6))
	else:
		fig = plt.figure(figsize = (2.5,6))
		
	if metric == 'Win Fraction':
		fraction = plot_dict[category].loc[games, players]
		cmap = 'Reds'
		vmin = 0
		vmax = 1
		label = 'Win Fraction'
	elif metric == 'Fraction Above Expected':
		fraction = plot_dict[category].loc[games, players]
		cmap = 'coolwarm'
		vmin = -1
		vmax = 1
		label = 'Fraction Above Expected'
	elif metric == 'Fraction Above Random':
		fraction = plot_dict[category].loc[games, players]
		cmap = 'coolwarm'
		vmin = -1
		vmax = 1
		label = 'Fraction Above Expected'
	g = sns.heatmap(fraction, cmap = cmap, vmin = vmin, vmax = vmax, cbar_kws = {'label': label})
	g.set_facecolor('black')
	return fig