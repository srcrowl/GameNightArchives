import streamlit as st
import pandas as pd
import numpy as np
import dataLoader
from dataLoader import processResults
from shillelagh.backends.apsw.db import connect
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter

#load data
#scores_dict, gplayed_dict, fraction_dict, pae_dict = processResults(st.session_state['Full Data'])
#overall_fraction = scores_dict['Game'].sum()/gplayed_dict['Game'].sum()
track = 'Win Fraction'
legend = False
if track == 'Number of Games':
    plot_data = st.session_state['Full Data'].groupby(['Date']).size().cumsum()
    ylabel = 'Number of Games'
elif track == 'Time Spent Playing Games':
    plot_data = st.session_state['Full Data'].groupby(['Date']).sum().cumsum()/60
    ylabel = 'Play Time (Hours)'
elif track == 'Number of Wins' or track == 'Win Fraction':
    plot_data = st.session_state['Full Data'].copy()
    if track == 'Win Fraction':
        gplayed_cumsum = plot_data.groupby('Date').size().cumsum()
        
    plot_data['Winner'] = plot_data['Winner'].apply(lambda x: x.split(';'))
    plot_data = plot_data.explode('Winner')
    plot_data['Wins'] = 1
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
    
    
st.write(plot_data)
fig, ax = plt.subplots()
if legend:
    ax.plot(plot_data.index.values, plot_data.values, label = plot_data.columns)
    ax.legend(bbox_to_anchor = (1.05, 1))
else:
    ax.plot(plot_data.index.values, plot_data.values)
ax.set_ylabel(ylabel)
plt.xticks(rotation = 45, ha = 'center')


st.pyplot(fig)








