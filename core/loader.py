import json
import streamlit as st

@st.cache_data
def load_game_data():
    with open("data/game_data.json", "r") as file:
        return json.load(file)