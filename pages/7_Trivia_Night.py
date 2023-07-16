import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from dataLoader import loadData_trivia

if 'Trivia' not in st.session_state:
    st.session_state['Trivia'] = loadData_trivia()
    
st.title('Trivia Night Results')
st.markdown('About once a month, we forego game night to go to Trivia at Star Hill Brewery. We recently started recording how well we do each time, and share it here')

st.markdown('Add new trivia results here: [link to google form](https://docs.google.com/forms/d/e/1FAIpQLSfya9fkNi8Wj_FyzJLVdWvjSI_JzVP5WhnEXO0b8YMZHZbQAQ/viewform?usp=sf_link)')

#create tabs
t1, t2 = st.tabs(['Summary Stats', 'Full Data'])
with t1:
    st.header('Summary Stats')
    cols = st.columns([0.2,0.4,0.4])
    cols[0].metric('Number of Trivia Outings', st.session_state['Trivia'].shape[0], delta = None)
    cols[0].metric('Best Finish', f"{st.session_state['Trivia']['Place'].min()}th", delta = None)

    score_columns = [col for col in st.session_state['Trivia'] if 'Score' in col]
    score_data = st.session_state['Trivia'][score_columns]
    score_data.index = st.session_state['Trivia']['Trivia Date']

    total_score = score_data.sum(axis = 1)
    cols[0].metric('Best Score', total_score.max(), delta = None)

    melted_scores = score_data.melt()
    fig,ax = plt.subplots()
    sns.swarmplot(x = 'variable', y = 'value', data = melted_scores, ax = ax, s = 10, palette = 'colorblind')
    #ax.set_xticklabels(['Current Events', 'Music', 'Pop Culture', '3rd Place Pick', 'Random Knowledge', 'Top 10 List'])
    plt.xticks(rotation = 35, ha = 'right')
    ax.set_ylabel('Score')
    ax.set_xlabel('Round')
    ax.set_title('Score by Round')
    cols[1].pyplot(fig)

    max_points = 8+16+8+8+8+10
    fig,ax = plt.subplots(nrows = 2,sharex = True)
    ax[0].plot(total_score.index, total_score.values, color = 'black')
    ax[0].set_ylabel('Total Score')
    ax[0].set_ylim([0,max_points + 1])
    ax[0].axhline(max_points, linestyle = 'dashed', c = 'black', label = "Max Possible")
    ax[0].axhline(np.mean(total_score), linestyle = 'dashed', alpha = 0.5, c = 'green', label = 'Mean Score')
    ax[0].axhline(np.median(total_score), linestyle = 'dashed', alpha = 0.5, c = 'blue', label = 'Median Score')
    ax[0].legend()


    ax[1].plot(st.session_state['Trivia']['Trivia Date'], st.session_state['Trivia']['Place'], color = 'black')
    ax[1].set_xlabel('Trivia Date')
    ax[1].set_ylabel('Final Place')
    ax[1].axhline(np.mean(st.session_state['Trivia']['Place']), linestyle = 'dashed', alpha = 0.5, c = 'green', label = 'Mean Place')
    ax[1].axhline(np.median(st.session_state['Trivia']['Place']), linestyle = 'dashed', alpha = 0.5, c = 'blue', label = 'Median Place')
    ax[1].legend()
    plt.xticks(rotation = 35, ha = 'right')
    ax[0].set_title('Trivia Results Over Time')
    cols[2].pyplot(fig)


with t2:
    st.header('Full Data, for your exploration')
    st.write(st.session_state['Trivia'])