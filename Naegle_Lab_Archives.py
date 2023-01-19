import streamlit as st
from dataLoader import loadData_sheets

st.title('Naegle Lab Game Night: A Battle of Wills')

st.write('Yes, yes, we are all here to complete are dissertation and get a doctorate. But of equal importance, who is the best board game player? Who can claim to place pieces the best? Have the most effective dice rool? Who can come up with a single word that indicates water but also a campfire? These questions and more get addressed once a week, and we have accumulated the results from the long battle here.')

if 'Full Data' not in st.session_state:
    st.session_state['Full Data'] = loadData_sheets()
    
number_of_games = st.session_state['Full Data'].shape[0]
number_of_unique_games = st.session_state['Full Data']['Game Title'].nunique()
time_spent = st.session_state['Full Data']['Play Time (min)'].sum()

st.header('Our Most Played Games!')

#get the most played games by time
games_played_by_time = st.session_state['Full Data'].groupby('Game Title')['Play Time (min)'].sum().sort_values(ascending = False)

st.write(f' We have played a total of {number_of_games} games over the course of {time_spent/60} hours. Across these games, we have played {number_of_unique_games} different games. Here are some of our most played:')
metric = st.selectbox('By:', ['Time','Number of Plays'])
if metric == 'Time':
    games_played_by_total = st.session_state['Full Data'].groupby('Game Title')['Play Time (min)'].sum().sort_values(ascending = False)
    games_played_by_recent = st.session_state['Full Data'].iloc[-50:].groupby('Game Title')['Play Time (min)'].sum().sort_values(ascending = False)
    unit = 'minutes'
else:
    games_played_by_total = st.session_state['Full Data'].groupby('Game Title').size().sort_values(ascending = False)
    games_played_by_recent = st.session_state['Full Data'].iloc[-50:].groupby('Game Title').size().sort_values(ascending = False)
    unit = 'times played'
cols = st.columns(2)
#All time
cols[0].write('All Time:')
rankings = ''
for i in range(10):
    row = games_played_by_total[i]
    rankings = rankings + f'{i+1}. {games_played_by_total.index[i]} = {games_played_by_total.iloc[i]} {unit}\n'
cols[0].write(rankings)


cols[1].write('Recent Favorites (Last 50 games)')
rankings = ''
for i in range(10):
    if i > games_played_by_recent.shape[0]:
        break
    else:
        row = games_played_by_recent[i]
        rankings = rankings + f'{i+1}. {games_played_by_recent.index[i]} = {games_played_by_recent.iloc[i]} {unit}\n'
cols[1].write(rankings)


#st.title('Naegle Lab Archives')

#st.header('Welcome!')

#st.write('We may be scientists and researchers, but we are far more concerned about who is winning game night and whether we created the best gingerbread house. Come for the phosphorylation puns, stay for the phosphorylaughs (oof). Come join the phosphotyroteam!')