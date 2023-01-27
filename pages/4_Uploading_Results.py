import streamlit as st

st.title('Uploading New Results')


new_game = st.checkbox('New Game')
if new_game:
    with st.form(key = 'GameNightUpload'):
        game_title = st.text_input('Game Title:')
        winner = st.multiselect('Winner (can select multiple):', ['Sam', 'Gabi', 'Reagan'])
        st.write('Scores (if applicable)')
        col = st.columns(3)
        sam_score = col[0].text_input('Sam:')
        gabi_score = col[1].text_input('Gabi:')
        reagan_score = col[2].text_input('Reagan:')
        submitted = st.form_submit_button("Submit")
        
else:
    with st.form(key = 'GameNightUpload'):
        game_title = st.selectbox('Game Title:', ['Rummikub', 'Uno','Settlers of Catan'])
        winner = st.multiselect('Winner (can select multiple):', ['Sam', 'Gabi', 'Reagan'])
        st.write('Scores (if applicable)')
        col = st.columns(3)
        sam_score = col[0].text_input('Sam:')
        gabi_score = col[1].text_input('Gabi:')
        reagan_score = col[2].text_input('Reagan:')
        submitted = st.form_submit_button("Submit")