import streamlit as st
import pandas as pd
import dataLoader
from shillelagh.backends.apsw.db import connect

#load data
full_data = dataLoader.loadData_sheets()
scores_dict, gplayed_dict, fraction_dict = dataLoader.processData(full_data)
overall_fraction = scores_dict['Game'].sum()/gplayed_dict['Game'].sum()


#load data minus the last 15 games
past_data = full_data.iloc[0:-15]
past_scores, past_gplayed, past_fraction = dataLoader.processData(past_data)
past_overall_fraction = past_scores['Game'].sum()/past_gplayed['Game'].sum()

st.write(past_scores['Game'].sum()['Sam'])


