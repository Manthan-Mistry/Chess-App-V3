import streamlit as st
import pandas as pd
import time
from datetime import datetime
from supabase import create_client, Client
import asyncio
from aiohttp import ClientSession
import asyncio 
import aiohttp
from utils.functions import get_date, get_archives, get_games_from_archive, delete_player_data, get_openings_2

# Supabase credentials (replace with your actual credentials)
SUPABASE_URL = st.secrets["PROJECT_URL"]
SUPABASE_KEY = st.secrets["API_KEY"]

# Functions for asynchronous fetching
async def fetch_archive_urls(player_name, session):
    url = f"https://api.chess.com/pub/player/{player_name}/games/archives"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("archives", [])
        return []

async def fetch_games(archive_url, session):
    async with session.get(archive_url) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("games", [])
        return []

async def fetch_all_games(archives, session):
    tasks = [fetch_games(archive_url, session) for archive_url in archives]
    results = await asyncio.gather(*tasks)
    games = []
    for result in results:
        if result:
            games.extend(result)
    return games

# Old function
def old_get_player_stats_db_live(player_name: str, supabase_url: str, supabase_key: str) -> pd.DataFrame:
    supabase: Client = create_client(supabase_url, supabase_key)
    all_rows = []
    batch_size = 1000
    start = 0

    try:
        while True:
            response = supabase.table("player_game_data").select("*").eq("player_name", player_name).range(start, start + batch_size - 1).execute()
            all_rows.extend(response.data)
            if len(response.data) < batch_size:
                break
            start += batch_size

        if all_rows:
            return pd.DataFrame(all_rows)
    except Exception as e:
        st.write(f"Error fetching data from Supabase: {e}")

    archives = get_archives(player_name)
    all_games = []
    for archive_url in archives:
        games = get_games_from_archive(archive_url)
        if isinstance(games, list):
            all_games.extend(games)

    formatted_games = []
    for game in all_games:
        game_data = {
            "player_name": player_name,
            "game_url": game.get("url"),
            "game_date": get_date(game.get("pgn")),
            "game_time_control": game.get("time_control"),
            "game_time_class": game.get("time_class"),
            "game_variant": game.get("rules"),
            "white_rating": game.get("white", {}).get("rating"),
            "black_rating": game.get("black", {}).get("rating"),
            "last_updated": datetime.now().isoformat()
        }
        formatted_games.append(game_data)

    df = pd.DataFrame(formatted_games)
    try:
        rows = df.to_dict(orient="records")
        for row in rows:
            supabase.table("player_game_data").insert(row).execute()
    except Exception as e:
        st.write(f"Error saving data to Supabase: {e}")

    return df


def run_async_function(async_function, *args):
    """
    Runs an asynchronous function with an aiohttp session in a synchronous environment.

    Args:
        async_function (coroutine): The async function to run.
        *args: Arguments to pass to the async function.

    Returns:
        Any: The result of the async function.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def wrapper():
        async with aiohttp.ClientSession() as session:
            return await async_function(*args, session)

    return loop.run_until_complete(wrapper())


# Optimized function
def optimized_get_player_stats_db_live(player_name: str, supabase_url: str, supabase_key: str) -> pd.DataFrame:
    """
    Retrieves all chess player stats from Supabase if available; fetches live data
    from Chess.com and stores it in Supabase if not available.
    """
    supabase: Client = create_client(supabase_url, supabase_key)

    # Step 1: Fetch existing data from Supabase
    try:
        existing_data = supabase.table("player_game_data").select("*").eq("player_name", player_name).execute().data
        existing_df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
    except Exception as e:
        st.write(f"Error fetching data from Supabase: {e}")
        existing_df = pd.DataFrame()

    # Step 2: Fetch game archives
    archives = run_async_function(fetch_archive_urls, player_name)
    if not archives:
        st.write("No archives found.")
        return existing_df

    # Step 3: Fetch all games
    games = run_async_function(fetch_all_games, archives)

    # Process and format games data
    formatted_games = []
    for game in games:
        game_data = {
            "player_name": player_name,
            "game_url": game.get("url"),
            "game_date": get_date(game.get("pgn")),
            "game_time_control": game.get("time_control"),
            "game_time_class": game.get("time_class"),
            "game_variant": game.get("rules"),
            "opening": get_openings_2(game),
            "white_rating": game.get("white", {}).get("rating"),
            "white_result": game.get("white", {}).get("result"),
            "white_username": game.get("white", {}).get("username"),
            "white_accuracy": game.get("accuracies", {}).get("white", 0.0),
            "black_rating": game.get("black", {}).get("rating"),
            "black_result": game.get("black", {}).get("result"),
            "black_username": game.get("black", {}).get("username"),
            "black_accuracy": game.get("accuracies", {}).get("black", 0.0),
            "last_updated": datetime.now().isoformat()
        }
        formatted_games.append(game_data)

    new_df = pd.DataFrame(formatted_games)

    # Step 4: Save all fetched games to Supabase (avoid duplicate insertion using PK constraints)
    batch_size = 1000  # Define your batch size
    rows = new_df.to_dict(orient="records")

    try:
        # Insert the rows in batches to avoid timeouts
        for start in range(0, len(rows), batch_size):
            batch = rows[start:start + batch_size]
            supabase.table("player_game_data").upsert(batch).execute()
            print(f"Inserted batch {start // batch_size + 1} of {len(rows)} rows.")
    except Exception as e:
        st.write(f"Error saving data to Supabase: {e}")

    # Combine existing data with the newly fetched data
    return pd.concat([existing_df, new_df], ignore_index=True)

# Streamlit App
st.title("Compare Old and Optimized Functions")

player_name = st.text_input("Enter Player Name")
if st.button("Run Old Function"):
    start_time = time.time()
    old_df = old_get_player_stats_db_live(player_name, SUPABASE_URL, SUPABASE_KEY)
    end_time = time.time()
    st.write("Old Function Time Taken:", end_time - start_time, "seconds")
    st.write("Old Function Output:")
    st.dataframe(old_df)

if st.button("Delete Player Data"):
    delete_player_data(player_name, SUPABASE_URL, SUPABASE_KEY)

if st.button("Run Optimized Function"):
    start_time = time.time()
    optimized_df = optimized_get_player_stats_db_live(player_name, SUPABASE_URL, SUPABASE_KEY)
    end_time = time.time()
    st.write("Optimized Function Time Taken:", end_time - start_time, "seconds")
    st.write("Optimized Function Output:")
    st.dataframe(optimized_df)
