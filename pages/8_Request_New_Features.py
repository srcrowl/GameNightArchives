import streamlit as st

st.title('Updating the web app')

st.text('At this page, several links to google forms are provided. These will allow you to:\n')
st.markdown('1. [Request new/updated features to web app](https://docs.google.com/forms/d/e/1FAIpQLSdlMVLoTVLI2GriO6tPOaPDNdgAGtEAXcL-Hw4gqtQgJB1Nhw/viewform?usp=sf_link)')
st.markdown('2. [Add new or update your game ratings](https://docs.google.com/forms/d/e/1FAIpQLSfZc5IXLWhtUynOdd0c79dwaQBYyPiRDVh2aSpXnBWiMvlz2Q/viewform?usp=sf_link)')
st.markdown('3. [Add a newly bought game to the list of games](https://docs.google.com/forms/d/e/1FAIpQLSdhC1avezkKRWl91ULWUPqt1qDOoWbuk9NRaUyOyTvG5iV4uQ/viewform?usp=sf_link)')
st.markdown('4. [Add Trivia Results](https://docs.google.com/forms/d/e/1FAIpQLSfya9fkNi8Wj_FyzJLVdWvjSI_JzVP5WhnEXO0b8YMZHZbQAQ/viewform?usp=sf_link)')


#new_game = st.checkbox('New Game')
#if new_game:
#    with st.form(key = 'GameNightUpload'):
#        game_title = st.text_input('Game Title:')
#        winner = st.multiselect('Winner (can select multiple):', ['Sam', 'Gabi', 'Reagan'])
#        st.write('Scores (if applicable)')
#        col = st.columns(3)
#        sam_score = col[0].text_input('Sam:')
#        gabi_score = col[1].text_input('Gabi:')
#        reagan_score = col[2].text_input('Reagan:')
#        submitted = st.form_submit_button("Submit")
#        
#else:
#    with st.form(key = 'GameNightUpload'):
#        game_title = st.selectbox('Game Title:', ['Rummikub', 'Uno','Settlers of Catan'])
#        winner = st.multiselect('Winner (can select multiple):', ['Sam', 'Gabi', 'Reagan'])
#        st.write('Scores (if applicable)')
#        col = st.columns(3)
#        sam_score = col[0].text_input('Sam:')
#        gabi_score = col[1].text_input('Gabi:')
#        reagan_score = col[2].text_input('Reagan:')
#        submitted = st.form_submit_button("Submit")