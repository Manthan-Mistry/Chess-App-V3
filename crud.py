import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
import time
from utils.functions import *

# Supabase credentials
SUPABASE_URL = st.secrets["PROJECT_URL"]
SUPABASE_KEY = st.secrets["API_KEY"]
 
def get_distinct_player_names(supabase_url: str, supabase_key: str) -> list:
    """
    Fetch all distinct player names from the 'player_game_data' table in Supabase.

    Args:
        supabase_url (str): The URL of the Supabase project.
        supabase_key (str): The API key for Supabase.

    Returns:
        list: A list of distinct player names.
    """
    # Initialize the Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Call the Postgres function
    response = supabase.rpc("get_distinct_player_names").execute()
    
    # Extract and return player names
    player_names = [item["player_name"] for item in response.data]
    return player_names

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

selected_player = st.text_input("Enter player name: ")

if st.button("Get Player Data"):
    all_players = get_distinct_player_names(supabase_url= SUPABASE_URL, supabase_key= SUPABASE_KEY)
    if selected_player in all_players:
        df = get_player_data_from_supabase(selected_player, supabase_url= SUPABASE_URL, supabase_key= SUPABASE_KEY)
    else:
        df = get_player_stats_db_live(selected_player, supabase_url= SUPABASE_URL, supabase_key= SUPABASE_KEY)
        
    st.metric(label= "Total Records", value= len(df))
    st.dataframe(df)

