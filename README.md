# 📄 About Project - 

![App Flow Diagram](https://github.com/Manthan-Mistry/Chess-App-V3/blob/main/assets/db-diagram-1.svg)

## 🔗 App Link: [Chess-App](https://chess-app-v3.onrender.com/)

## 🔍 Project Overview
The main purpose of this project is to showcase proficiency in:  
- **Data Extraction From API**  
- **Data Manipulation Using Python**  
- **Data Visualization Using Streamlit & Plotly**  

This Streamlit app provides real-time statistics and historical data of chess players in an interactive and visually appealing format. It allows users to explore player profiles, including performance in various time controls like bullet, blitz, and rapid, as well as in game variants like chess, bughouse, three-check, chess960, king-of-the-hill, and crazyhouse.

---

## 💡 Features
- **Dynamic Player Selection**: Users can select any player available in the existing dataframe using a dropdown.  
- **Player Profile Display**: Dynamic player profiles include avatars, names, titles, country flags, and chess-related metrics like followers and ratings, similar to Chess.com's official site.  
- **Data Filtering**: Players' ratings charts can be filtered by specific time periods (e.g., last year, last three years, all time) using styled tabs.  
- **Player Info**: Personal life details, achievements, and chess careers of players are fetched dynamically from the [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page).  
- **Real-time Data**: Real-time statistics are extracted directly from [Chess.com's Public API](https://www.chess.com/news/view/published-data-api) with a progress bar indicating data loading time.  
- **Database Implementation**: Supabase database fetches pre-existing player data, significantly reducing loading time.

---

## 📱 Interactive UI
The app uses Streamlit components for a sleek, interactive interface. Users can select players from a dropdown or text input, view data in an organized multi-column layout, and enjoy custom-styled metrics enhanced with CSS. Real-time data loading is displayed via a progress bar for a more engaging user experience.

---

## 💪 Challenges
- **Handling Slow Loading Times**: Used `st.cache_data` to ensure data does not reload every time the app refreshes.  
- **Image Rendering**: Converted PNG/JPG images to Base64 encoding for proper rendering inside Markdown.  
- **Plotly Chart Visibility**: Adjusted `.stPlotlyChart`'s background to white for better contrast and number visibility on a dark app background.  
- **Showing Player's Country Flag**: Extracted players' country codes and dynamically displayed flags using `flagcdn.com`.  
- **Making `st.selectbox` and `st.tab` text color different**: Solved the issue using a CSS hack suggested by Streamlit creator @andfanilo. [Checkout thread](https://discuss.streamlit.io/t/can-i-change-the-color-of-the-selectbox-widget/9601/2)  
- **Using Upsert in Supabase**: Ensured new records were inserted while existing ones were updated, preventing duplicate entries and maintaining data integrity.  
- **Batch Insert**: Improved performance by sending multiple records to the database in a single query, avoiding 'canceling statement due to statement timeout' errors.

---

## 🔨 Technologies Used
- **Chess.com's Public API** for live data extraction.  
- **Python and Streamlit** for data processing and front-end interaction.  
- **Wikipedia API** for fetching additional player details.  
- **Supabase Database** for saving player data in the live section.  

---

## ⏳ Future Plans
Future updates will include:  
- Additional player vs. player comparison.  
- Dynamic display of the Top 5 Junior and Top 15 Senior players based on live ratings maintained by [FIDE](https://ratings.fide.com/).
