import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_validate
from sklearn.linear_model import Ridge, Lasso
from dataLoader import loadData_ratings, processResults, loadData_categories, loadData_results
import matplotlib.pyplot as plt

if 'Full Data' not in st.session_state:
    st.session_state['Full Data'] = loadData_results()
    
if 'Type' not in st.session_state:
    loadData_categories()
    
if 'Rating' not in st.session_state:
    st.session_state['Ratings'] = loadData_ratings()

@st.cache(ttl = 600)
def plotAlphaChange(x, y, alpha = None):
    coefs = []
    fig,ax = plt.subplots(nrows = 3, sharex = True)
    plt_x = np.arange(0,5.1,0.1)
    mse = []
    q2 = []
    for alpha in plt_x:
        model = Ridge(alpha = alpha)
        scores = cross_validate(model, x, y, cv = 10, scoring = ['neg_mean_squared_error', 'r2'])
        #st.write(scores)
        model.fit(x,y)
        coefs.append(list(model.coef_))
        mse.append(abs(np.mean(scores['test_neg_mean_squared_error'])))
        q2.append(np.mean(scores['test_r2']))
    ax[0].plot(plt_x,coefs)
    ax[0].set_ylabel('Coefficient')
    #ax[0].set_xlabel('Regularization Parameter')
    ax[0].set_title('Coefficients')
    if alpha is not None:
        plt.axvline(alpha, c = 'black', linestyle = 'dashed', alpha = 0.5)
        
    ax[1].plot(plt_x, mse)
    ax[1].set_ylabel('Mean Squared Error')
    ax[1].set_xlabel('Regularization Parameter')
    #ax[1].set_title('Cross-Validation Error')
    
    ax[2].plot(plt_x, q2)
    ax[2].set_ylabel('Q2')
    ax[2].set_xlabel('Regularization Parameter')
    #ax[2].set_title('Cross-Validation Error')
    return fig
    
@st.cache(ttl = 600)
def generateGroupings(use_list):
    groupings = []
    if use_list[0]:
        owner = st.session_state['Owner'].copy().dropna()
        #owner = owner[owner['Owner'].isin(game_lists[0])]
        owner['Owner'] = owner['Owner'].apply(lambda x: 'Owner:'+x)
        owner = owner.rename({'Owner': 'Category'}, axis = 1)
        groupings.append(owner)
    if use_list[1]:
        gformat = st.session_state['Format'].copy().dropna()
        #gformat = gformat[gformat['Format'].isin(game_lists[1])]
        gformat['Format'] = gformat['Format'].apply(lambda x: 'Format:'+x)
        gformat = gformat.rename({'Format': 'Category'}, axis = 1)
        groupings.append(gformat)
    if use_list[2]:
        gteam = st.session_state['Team Size'].copy()
        #gteam = gteam[gteam['Team Size'].isin(team_list)]
        gteam['Team Size'] = gteam['Team Size'].apply(lambda x: 'Size:'+x)
        gteam = gteam.rename({'Team Size': 'Category'}, axis = 1)
        groupings.append(gteam)
    if use_list[3]:
        glength = st.session_state['Game Length'].copy()
        #glength = glength[glength['Game Length'].isin(length_list)]
        glength['Game Length'] = glength['Game Length'].apply(lambda x: 'Length:'+x)
        glength = glength.rename({'Game Length': 'Category'}, axis = 1)
        groupings.append(glength)
    if use_list[4]:
        gclass = st.session_state['Primary Classification'].copy()
        #gclass = gclass[gclass['Primary Classification'].isin(class_list)]
        gclass['Primary Classification'] = gclass['Primary Classification'].apply(lambda x: 'Class:'+x)
        gclass = gclass.rename({'Primary Classification': 'Category'}, axis = 1)
        groupings.append(gclass)
    if use_list[5]:
        gtype = st.session_state["Sam's Mechanisms"].copy()
        #gtype = gtype[gtype["Sam's Mechanisms"].isin(type_list)]
        gtype["Sam's Mechanisms"] = gtype["Sam's Mechanisms"].apply(lambda x: 'Type:'+x)
        gtype = gtype.rename({"Sam's Mechanisms": 'Category'}, axis = 1)
        groupings.append(gtype)
    if use_list[6]:
        gtheme = st.session_state['Theme'].copy().dropna()
        #gtheme = gtheme[gtheme['Theme'].isin(theme_list)]
        gtheme['Theme'] = gtheme['Theme'].apply(lambda x: 'Theme:'+x)
        gtheme = gtheme.rename({'Theme': 'Category'}, axis = 1)
        groupings.append(gtheme)
    if use_list[7]:
        bgg_type = st.session_state['BGG Type'].copy().dropna()
        #bgg_type = bgg_type[bgg_type['BGG Type'].isin(bggtype_list)]
        bgg_type['BGG Type'] = bgg_type['BGG Type'].apply(lambda x: 'BGG_Type:'+x)
        bgg_type = bgg_type.rename({'BGG Type': 'Category'}, axis = 1)
        groupings.append(bgg_type)
    if use_list[8]:
        bgg_cat = st.session_state['BGG Category'].copy().dropna()
        #bgg_cat = bgg_cat[bgg_cat['BGG Category'].isin(bggcat_list)]
        bgg_cat['BGG Category'] = bgg_cat['BGG Category'].apply(lambda x: 'BGG_Cat:'+x)
        bgg_cat = bgg_cat.rename({'BGG Category': 'Category'}, axis = 1)
        groupings.append(bgg_cat)
    if use_list[9]:
        bgg_mech = st.session_state['BGG Mechanism'].copy().dropna()
        #bgg_mech = bgg_mech[bgg_mech['BGG Mechanism'].isin(bggmech_list)]
        bgg_mech['BGG Mechanism'] = bgg_mech['BGG Mechanism'].apply(lambda x: 'BGG_Mech:'+x)
        bgg_mech = bgg_mech.rename({'BGG Mechanism': 'Category'}, axis = 1)
        groupings.append(bgg_mech)
    groupings = pd.concat(groupings)
    return groupings
    
@st.cache(ttl = 600)
def constructInputs(groupings, ratings):
    #construct x
    x = None
    for game in ratings.index:
        #construct x
        if x is None:
            x = pd.DataFrame(data = 0, index = groupings['Category'].unique(), columns = [game])
            game_cats = groupings.loc[groupings['Game Title'] == game, 'Category']
            x.loc[game_cats] = 1
        else:
            game_cats = groupings.loc[groupings['Game Title'] == game, 'Category']
            x[game] = 0
            x.loc[game_cats, game] = 1
                
    x = x.T
    return x

coop_games = ['Forbidden Desert', 'The Initiative', 'Horrified', 'Hanabi', 'Arkham Horror', 'Mysterium', 'The Crew: Quest for Planet Nine']

st.title('Summary of Our Ratings')
gamenight_only = st.checkbox('Restrict ratings to those played during game night', value = True)
allrated_only = st.checkbox('Restrict ratings to games that everyone has rated', value = True)
scores_dict, gplayed_dict, fraction_dict, pae_dict = processResults(st.session_state['Full Data'])
overall_fraction = scores_dict['Game'].sum()/gplayed_dict['Game'].sum()
ratings = st.session_state['Ratings'].copy()
if gamenight_only:
    games_played = list(st.session_state['Full Data']['Game Title'].unique()) + coop_games
    ratings = ratings.loc[games_played]
if allrated_only:
    ratings = ratings.dropna()
st.header('Consensus Preferences')
st.subheader('Favorites')
consensus = ratings.mean(axis = 1)
cols = st.columns(2)
sorting_ratings = consensus.sort_values(ascending = False)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]), sorting_ratings.index):
    if rank > 10 and prev_rating > sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} ({round(sorting_ratings.loc[game],2)})\n'
    prev_rating = sorting_ratings.loc[game]

#games ranked list
cols[0].write('Games:')
cols[0].write(ranked_list)


#rank by category
group = cols[1].selectbox('Game Grouping (Min 2 Games):', ['Owner', 'Format', 'Team Size', 'Game Length', 'Primary Classification', "Sam's Mechanisms", 'Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism'])
consensus_grouped = consensus.reset_index().merge(st.session_state[group], right_on = 'Game Title', left_on = 'index').groupby(group)
group_sizes = consensus_grouped.size()
min_games = cols[1].slider('Minimum number of Games Required for Inclusion', min_value = 1, max_value = 5, value = 2, key = 'all_most') 
games_to_include = group_sizes[group_sizes >= min_games].index
mean_ratings = consensus_grouped[0].mean()[games_to_include]
sorting_ratings = mean_ratings.sort_values(ascending = False)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]+1), sorting_ratings.index):
    if rank > 10 and prev_rating > sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} = {round(sorting_ratings.loc[game], 2)} ({group_sizes[game]} games)\n'
    prev_rating = sorting_ratings.loc[game]
cols[1].write(ranked_list)


st.subheader(f"Least Favorites")
cols = st.columns(2)
sorting_ratings = consensus.sort_values(ascending = True)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]), sorting_ratings.index):
    if rank > 10 and prev_rating < sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} = {round(sorting_ratings.loc[game],2)}\n'
    prev_rating = sorting_ratings.loc[game]

#games ranked list
cols[0].write('Games:')
cols[0].write(ranked_list)


#rank by category
group = cols[1].selectbox('Game Grouping (Min 2 Games):', ['Owner', 'Format', 'Team Size', 'Game Length', 'Primary Classification', "Sam's Mechanisms", 'Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism'], key = 'Least Favorite')
consensus_grouped = consensus.reset_index().merge(st.session_state[group], right_on = 'Game Title', left_on = 'index').groupby(group)
group_sizes = consensus_grouped.size()
min_games = cols[1].slider('Minimum number of Games Required for Inclusion', min_value = 1, max_value = 5, value = 2, key = 'all_least')
games_to_include = group_sizes[group_sizes >= min_games].index
mean_ratings = consensus_grouped.mean().squeeze()[games_to_include]
sorting_ratings = mean_ratings.sort_values(ascending = True)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]+1), sorting_ratings.index):
    if rank > 10 and prev_rating < sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} = {round(sorting_ratings.loc[game], 2)} ({group_sizes[game]} games)\n'
    prev_rating = sorting_ratings.loc[game]
cols[1].write(ranked_list)
st.write('\n\n\n\n')
st.header('Individual Favorites')
player = st.selectbox('Player',['Sam', 'Gabi', 'Reagan'])



#y = fraction_dict['Game'][player]
y = ratings[player].dropna()
#favorite games
st.subheader(f"{player}'s Favorites")
cols = st.columns(2)
sorting_ratings = y.sort_values(ascending = False)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]), sorting_ratings.index):
    if rank > 10 and prev_rating > sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} ({round(sorting_ratings.loc[game], 2)})\n'
    prev_rating = sorting_ratings.loc[game]

#games ranked list
cols[0].write('Games:')
cols[0].write(ranked_list)


#rank by category
group = cols[1].selectbox('Game Grouping (Min 2 Games):', ['Owner', 'Format', 'Team Size', 'Game Length', 'Primary Classification', "Sam's Mechanisms", 'Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism'], key = 'Individual Favorite')
y_grouped = y.reset_index().merge(st.session_state[group], right_on = 'Game Title', left_on = 'index').groupby(group)
group_sizes = y_grouped.size()
min_games = cols[1].slider('Minimum number of Games Required for Inclusion', min_value = 1, max_value = 5, value = 2, key = 'player_most')
games_to_include = group_sizes[group_sizes >= min_games].index
mean_ratings = y_grouped.mean().squeeze()[games_to_include]
sorting_ratings = mean_ratings.sort_values(ascending = False)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]+1), sorting_ratings.index):
    if rank > 10 and prev_rating > sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} = {round(sorting_ratings.loc[game], 2)} ({group_sizes[game]} games)\n'
    prev_rating = sorting_ratings.loc[game]
cols[1].write(ranked_list)


st.subheader(f"{player}'s Least Favorites")
cols = st.columns(2)
sorting_ratings = y.sort_values(ascending = True)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]), sorting_ratings.index):
    if rank > 10 and prev_rating < sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} ({sorting_ratings.loc[game]})\n'
    prev_rating = sorting_ratings.loc[game]

#games ranked list
cols[0].write('Games:')
cols[0].write(ranked_list)


#rank by category
group = cols[1].selectbox('Game Grouping (Min 2 Games):', ['Owner', 'Format', 'Team Size', 'Game Length', 'Primary Classification', "Sam's Mechanisms", 'Theme', 'BGG Type', 'BGG Category', 'BGG Mechanism'], key = 'Individual Least Favorite')
y_grouped = y.reset_index().merge(st.session_state[group], right_on = 'Game Title', left_on = 'index').groupby(group)
group_sizes = y_grouped.size()
min_games = cols[1].slider('Minimum number of Games Required for Inclusion', min_value = 1, max_value = 5, value = 2, key = 'player_least')
games_to_include = group_sizes[group_sizes >= min_games].index
mean_ratings = y_grouped.mean().squeeze()[games_to_include]
sorting_ratings = mean_ratings.sort_values(ascending = True)
ranked_list = ''
for rank, game in zip(range(1,sorting_ratings.shape[0]+1), sorting_ratings.index):
    if rank > 10 and prev_rating < sorting_ratings.loc[game]:
        break
    else:
        ranked_list = ranked_list + f'{rank}. {game} = {round(sorting_ratings.loc[game], 2)} ({group_sizes[game]} games)\n'
    prev_rating = sorting_ratings.loc[game]
cols[1].write(ranked_list)

st.subheader(f"Predict {player}'s Rating")
#decide which categories to include
cols = st.columns(4)
use_owner = cols[0].checkbox('Game Owner', value = True)
use_format = cols[1].checkbox('Game Format', value = True)
use_team = cols[2].checkbox('Team Size', value = False)
use_length = cols[3].checkbox('Game Length', value = True)
cols = st.columns(3)
use_class = cols[0].checkbox('Primary Classification', value = True)
use_type = cols[1].checkbox("Sam's Mechanisms", value = True)
use_theme = cols[2].checkbox("Game Theme", value = True)
cols = st.columns(3)
use_bggtype = cols[0].checkbox('BGG Type', value = True)
use_bggcat = cols[1].checkbox('BGG Category', value = True)
use_bggmech = cols[2].checkbox('BGG Mechanism', value = True)
use_list = [use_owner, use_format,use_team, use_length, use_class, use_type, use_theme, use_bggtype, use_bggcat, use_bggmech]

min_games = st.slider('Minimum number of games required for category to be included:', min_value = 0, max_value = 10, value = 0)
#owner_list = gplayed_dict['Owner'][gplayed_dict['Owner'] >= min_games].index.values
#type_list = gplayed_dict['Type'][gplayed_dict['Type'] >= min_games].index.values
#theme_list = gplayed_dict['Theme'][gplayed_dict['Theme'] >= min_games].index.values
#format_list = gplayed_dict['Format'][gplayed_dict['Format'] >= min_games].index.values
#bggtype_list = gplayed_dict['BGG Type'][gplayed_dict['BGG Type'] >= min_games].index.values
#bggcat_list = gplayed_dict['BGG Category'][gplayed_dict['BGG Category'] >= min_games].index.values
#bggmech_list = gplayed_dict['BGG Mechanism'][gplayed_dict['BGG Mechanism'] >= min_games].index.values
#game_lists = [owner_list,format_list, type_list, theme_list, bggtype_list, bggcat_list, bggmech_list]


show_alpha = st.checkbox('Show Impact of Alpha', key = 'plot_alpha')
#show impact of alpha
if show_alpha:
    groupings = generateGroupings(use_list)
    sizes = groupings.groupby('Category').size()
    groups_to_keep = sizes[sizes >= min_games].index
    groupings = groupings[groupings['Category'].isin(groups_to_keep)]
    x = constructInputs(groupings, ratings)
    fig = plotAlphaChange(x,y)
    st.pyplot(fig)
alpha = st.slider('Regularization Parameter', min_value = 0.00, max_value = 3.0, value = 1.0, step = 0.1)
generate_model = st.checkbox('Build Model From Current Data', value = False, key = 'model_generation')
if generate_model:
    #if it hasn't already been done, construct necessary groupings and x 
    if not show_alpha:
        groupings = generateGroupings(use_list)
        sizes = groupings.groupby('Category').size()
        groups_to_keep = sizes[sizes >= min_games].index
        groupings = groupings[groupings['Category'].isin(groups_to_keep)]
        x = constructInputs(groupings, ratings)
    model = Ridge(alpha = alpha)
    model.fit(x, y)
    score = model.score(x,y)
    st.text('\nModel Built')
    st.markdown(f'$R^2=$:{score}')
    
    show_coef = st.checkbox('Show Model Coefficents')
    #get most predictive categories
    if show_coef:
        coef = pd.Series(data = model.coef_, index = x.columns, name = 'Coefficients')
        coef = coef.sort_values(ascending = False)
        st.write(coef)
    #sort_index = numpy.argsort(vals)

    new_groups = st.multiselect('Groups associated with game to predict rating for:', np.sort(x.columns))
    x_new = [[1 if group in new_groups else 0 for group in x.columns]]
    y = model.predict(x_new)
    st.write(f'Predicted rating = {y[0]}')


#####################################################Exploratory plots


#shared_info = list(set(x.index).intersection(y.index))
#x = x.loc[shared_info]
#y = y.loc[shared_info]
#fig = plt.figure()
#plt.scatter(x, y)
#plt.ylabel('Win Fraction')
#plt.xlabel('Game Rating')
#plt.title('Relationship between Liking Games and Win Percentage')
#cols = st.columns(2)
#cols[0].pyplot(fig)


#data = st.session_state['Full Data'].copy()

#games = ratings.index
#win = []
#loss = []
#for i, res in data.iterrows():
#    game_title = res['Game Title']
#    if game_title in ratings.index:
#        game_winner = res['Winner']
#        if game_winner == player:
#            win.append(ratings.loc[game_title, player])
#        else:
#            loss.append(ratings.loc[game_title, player])
#fig = plt.figure()
#plt.hist(win, alpha = 0.5, label = 'Games Won', density = True)
#plt.hist(loss, alpha = 0.5, label = 'Games Lost', density = True)
#plt.legend()
#plt.xlabel('Game Rating')
#plt.title('Relationship between Liking Games and Wins')
#cols[1].pyplot(fig)


#x = st.session_state['Categories'][['Game Title', 'BGG Weight']]
#x.index = x['Game Title']
#x = x.drop('Game Title', axis = 1)
#y = st.session_state['Ratings'][player]
#shared_info = list(set(x.index).intersection(y.index))
#x = x.loc[shared_info]
#y = y.loc[shared_info]
#fig = plt.figure()
#plt.scatter(x, y)
#plt.xlabel('Game Weight')
#plt.ylabel('Game Rating')
#st.pyplot(fig)