from sklearn.naive_bayes import BernoulliNB
from dataLoader import loadData_ratings, processResults, loadData_categories, loadData_results
import pandas as pd
import numpy as np
import streamlit as st

if 'Full Data' not in st.session_state:
    st.session_state['Full Data'] = loadData_results()
    
if 'Type' not in st.session_state:
    loadData_categories()
    
if 'Rating' not in st.session_state:
    st.session_state['Ratings'] = loadData_ratings()


st.header('Building a Naive Bayes Classifier')
min_games = st.slider('Minimum number of games required for category to be included:', min_value = 0, max_value = 50, value = 5)
smoothing = st.slider('Smoothing parameter value:', min_value = 0.0, max_value = 1.0, value = 1.0)
#load data
scores_dict, gplayed_dict, fraction_dict, pae_dict, par_dict = processResults(st.session_state['Full Data'])
owner_list = gplayed_dict['Owner'][gplayed_dict['Owner'] >= min_games].index.values
length_list = gplayed_dict['Game Length'][gplayed_dict['Game Length'] >= min_games].index.values
team_list = gplayed_dict["Team Size"][gplayed_dict["Team Size"] >= min_games].index.values
class_list = gplayed_dict["Primary Classification"][gplayed_dict["Primary Classification"] >= min_games].index.values
type_list = gplayed_dict["Sam's Mechanisms"][gplayed_dict["Sam's Mechanisms"] >= min_games].index.values
theme_list = gplayed_dict['Theme'][gplayed_dict['Theme'] >= min_games].index.values
format_list = gplayed_dict['Format'][gplayed_dict['Format'] >= min_games].index.values
bggtype_list = gplayed_dict['BGG Type'][gplayed_dict['BGG Type'] >= min_games].index.values
bggcat_list = gplayed_dict['BGG Category'][gplayed_dict['BGG Category'] >= min_games].index.values
bggmech_list = gplayed_dict['BGG Mechanism'][gplayed_dict['BGG Mechanism'] >= min_games].index.values

#decide which categories to include
cols = st.columns(4)
use_owner = cols[0].checkbox('Game Owner', value = True)
use_format = cols[1].checkbox('Game Format', value = True)
use_team = cols[2].checkbox('Team Size', value = False)
use_length = cols[3].checkbox('Game Length', value = True)
cols = st.columns(3)
use_class = cols[0].checkbox('Primary Classification', value = True)
use_type = cols[1].checkbox("Sam's Mechanisms", value = True)
use_theme = cols[2].checkbox('Game Theme', value = True)
cols = st.columns(3)
use_bggtype = cols[0].checkbox('BGG Type', value = True)
use_bggcat = cols[1].checkbox('BGG Category', value = True)
use_bggmech = cols[2].checkbox('BGG Mechanism', value = True)


generate_classifier = st.checkbox('Build Naive Bayes Classifier', value = False)
if generate_classifier:
    data = st.session_state['Full Data'].copy()
    data['Winner'] = data['Winner'].apply(lambda x: x.split(';'))
    data = data.explode('Winner').reset_index()

    groupings = []
    if use_owner:
        owner = st.session_state['Owner'].copy()
        owner = owner[owner['Owner'].isin(owner_list)]
        owner['Owner'] = owner['Owner'].apply(lambda x: 'Owner:'+x)
        owner = owner.rename({'Owner': 'Category'}, axis = 1)
        groupings.append(owner)
    if use_format:
        gformat = st.session_state['Format'].copy()
        gformat = gformat[gformat['Format'].isin(format_list)]
        gformat['Format'] = gformat['Format'].apply(lambda x: 'Format:'+x)
        gformat = gformat.rename({'Format': 'Category'}, axis = 1)
        groupings.append(gformat)
    if use_team:
        gteam = st.session_state['Team Size'].copy()
        gteam = gteam[gteam['Team Size'].isin(team_list)]
        gteam['Team Size'] = gteam['Team Size'].apply(lambda x: 'Size:'+x)
        gteam = gteam.rename({'Team Size': 'Category'}, axis = 1)
        groupings.append(gteam)
    if use_length:
        glength = st.session_state['Game Length'].copy()
        glength = glength[glength['Game Length'].isin(length_list)]
        glength['Game Length'] = glength['Game Length'].apply(lambda x: 'Length:'+x)
        glength = glength.rename({'Game Length': 'Category'}, axis = 1)
        groupings.append(glength)
    if use_class:
        gclass = st.session_state['Primary Classification'].copy()
        gclass = gclass[gclass['Primary Classification'].isin(class_list)]
        gclass['Primary Classification'] = gclass['Primary Classification'].apply(lambda x: 'Class:'+x)
        gclass = gclass.rename({'Primary Classification': 'Category'}, axis = 1)
        groupings.append(gclass)
    if use_type:
        gtype = st.session_state["Sam's Mechanisms"].copy()
        gtype = gtype[gtype["Sam's Mechanisms"].isin(type_list)]
        gtype["Sam's Mechanisms"] = gtype["Sam's Mechanisms"].apply(lambda x: 'Type:'+x)
        gtype = gtype.rename({"Sam's Mechanisms": 'Category'}, axis = 1)
        groupings.append(gtype)
    if use_theme:
        gtheme = st.session_state['Theme'].copy()
        gtheme = gtheme[gtheme['Theme'].isin(theme_list)]
        gtheme['Theme'] = gtheme['Theme'].apply(lambda x: 'Theme:'+x)
        gtheme = gtheme.rename({'Theme': 'Category'}, axis = 1)
        groupings.append(gtheme)
    if use_bggtype:
        bgg_type = st.session_state['BGG Type'].copy()
        bgg_type = bgg_type[bgg_type['BGG Type'].isin(bggtype_list)]
        bgg_type['BGG Type'] = bgg_type['BGG Type'].apply(lambda x: 'BGG_Type:'+x)
        bgg_type = bgg_type.rename({'BGG Type': 'Category'}, axis = 1)
        groupings.append(bgg_type)
    if use_bggcat:
        bgg_cat = st.session_state['BGG Category'].copy()
        bgg_cat = bgg_cat[bgg_cat['BGG Category'].isin(bggcat_list)]
        bgg_cat['BGG Category'] = bgg_cat['BGG Category'].apply(lambda x: 'BGG_Cat:'+x)
        bgg_cat = bgg_cat.rename({'BGG Category': 'Category'}, axis = 1)
        groupings.append(bgg_cat)
    if use_bggmech:
        bgg_mech = st.session_state['BGG Mechanism'].copy()
        bgg_mech = bgg_mech[bgg_mech['BGG Mechanism'].isin(bggmech_list)]
        bgg_mech['BGG Mechanism'] = bgg_mech['BGG Mechanism'].apply(lambda x: 'BGG_Mech:'+x)
        bgg_mech = bgg_mech.rename({'BGG Mechanism': 'Category'}, axis = 1)
        groupings.append(bgg_mech)
    groupings = pd.concat(groupings)



    #construct x and y
    y = []
    x = None
    for i, result in data.iterrows():
        winner = result['Winner']
        game = result['Game Title']
        if winner != 'Lionel' and winner != 'Alekhya':
            y.append(winner)
            
            #construct x
            if x is None:
                x = pd.DataFrame(data = 0, index = groupings['Category'].unique(), columns = [f'Res{i}'])
                game_cats = groupings.loc[groupings['Game Title'] == game, 'Category']
                x.loc[game_cats] = 1
            else:
                game_cats = groupings.loc[groupings['Game Title'] == game, 'Category']
                x[f'Res{i}'] = 0
                x.loc[game_cats, f'Res{i}'] = 1
                
    x = x.T
    #convert y to numeric
    y = np.array(y)
    y[y == 'Sam'] = 1
    y[y == 'Gabi'] = 2
    y[y == 'Reagan'] = 3
    y = y.reshape(-1,1)
    y = y.astype(int)


    model = BernoulliNB(force_alpha = True, alpha = smoothing)
    fit = model.fit(x, y)
    score = model.score(x,y)
    st.write(f"The mean accuracy on the training data is {round(score*100, 2)}%")
    predictions = model.predict(x)
    #st.write(predictions)
    #st.write(data)
    sam_wins = len(predictions[predictions == 1])/st.session_state['Full Data'].shape[0]
    gabi_wins = len(predictions[predictions == 2])/st.session_state['Full Data'].shape[0]
    reagan_wins = len(predictions[predictions == 3])/st.session_state['Full Data'].shape[0]
    st.subheader('Expected Win Percentages Based on Classifier')
    cols = st.columns(3)
    cols[0].metric('Sam', f'{round(sam_wins*100, 2)}%')
    cols[1].metric('Gabi', f'{round(gabi_wins*100, 2)}%')
    cols[2].metric('Reagan', f'{round(reagan_wins*100, 2)}%')
    
    probabilities = model.predict_proba(x)
    #st.write(probabilities)
    
    st.subheader('Predict Win Probabilities for Played or New Games')
    game = st.selectbox('What game would you like to see estimated win probabilities for?', np.sort(st.session_state['Full Data']['Game Title'].unique()))
    
    x_new = pd.DataFrame(data = 0, index = groupings['Category'].unique(), columns = ['New Pred'])
    game_cats = groupings.loc[groupings['Game Title'] == game, 'Category']
    x_new.loc[game_cats, 'New Pred'] = 1
    x_new = x_new.T
    probs = model.predict_proba(x_new)
    cols = st.columns(3)
    cols[0].metric('Sam', f'{round(probs[0][0]*100, 2)}%')
    cols[1].metric('Gabi', f'{round(probs[0][1]*100, 2)}%')
    cols[2].metric('Reagan', f'{round(probs[0][2]*100, 2)}%')
    #how game is classified
    st.markdown(f'__Labels associated with {game} used for prediction__')
    st.write(game_cats)

    
    
    
    
    
    #st.write('What else would you like to use the classifier to do?')