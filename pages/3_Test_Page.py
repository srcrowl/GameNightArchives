import streamlit as st
from shillelagh.backends.apsw.db import connect

@st.cache(ttl = 600)
def runQuery(sheets_link):
	connection = connect(":memory:")
	cursor = connection.cursor()
	
	query = f'SELECT * FROM "{sheets_link}"'
	
	
	for row in cursor.execute(query):
		st.write(row)
	
#def loadFullData()
sheet_url = st.secrets['sheet_url']
runQuery(sheet_url)