import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
password_input = st.text_input("Enter Team Password", type="password")
if password_input != "vinprat":
    st.warning("Please enter the correct password to access the Editorial Dashboard.")
    st.stop() # This freezes the app until the password is right

# --- CONFIGURATION ---
st.set_page_config(page_title="Standard v1.0 | Editorial Dashboard", layout="wide")

# Define weights for scoring
MOVIE_WEIGHTS = {"Story_Screenplay": 0.25, "Characters_Acting": 0.20, "Directing": 0.15, "Visuals": 0.15, "Sound_Music": 0.10, "Editing_Pacing": 0.10, "Impact": 0.05}
BOOK_WEIGHTS = {"Prose_Writing": 0.30, "Plot_Structure": 0.25, "Character_Depth": 0.20, "Pacing": 0.15, "Themes_Impact": 0.10}

# --- GOOGLE SHEETS CONNECTION ---
# This connects to the Sheet URL you will put in your Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        # ttl=0 ensures we always see the most recent submissions
        return conn.read(ttl="0s")
    except:
        # If the sheet is empty or has issues, return an empty table with headers
        return pd.DataFrame(columns=["Date", "Reviewer", "Type", "Title", "Final_Score"])

# --- UI INTERFACE ---
st.title("⚖️ Editorial Review Standard v1.0")

with st.expander("📖 The Standard Rules"):
    st.write("1. 5 is Average. 2. Context matters. 3. 10 is genre-defining.")

tab1, tab2, tab3, tab4 = st.tabs(["✍️ Submit Review", "🤝 Group War Room", "📊 Analytics", "📜 Archive"])

with tab1:
    c1, c2, c3 = st.columns([1, 1, 2])
    reviewer = c1.selectbox("Reviewer", ["Alice", "Bob", "Charlie", "Dave"])
    m_type = c2.radio("Media Type", ["Movie", "Book"])
    title = c3.text_input("Title")

    st.divider()
    current_weights = MOVIE_WEIGHTS if m_type == "Movie" else BOOK_WEIGHTS
    scores = {}
    
    cols = st.columns(2)
    for i, cat in enumerate(current_weights.keys()):
        scores[cat] = cols[i % 2].slider(cat.replace("_", " "), 1, 10, 5, key=f"{m_type}_{cat}")

    if st.button("Submit to Cloud Records"):
        if title:
            final_score = sum(scores[c] * current_weights[c] for c in current_weights)
            
            # Create the new data row
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Reviewer": reviewer,
                "Type": m_type,
                "Title": title.strip().title(),
                "Final_Score": round(final_score, 2)
            }])
            
            # Update the Google Sheet
            existing_data = get_data()
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(data=updated_df)
            
            st.success(f"Saved to Google Sheets! {title} Score: {round(final_score, 2)}")
            st.balloons()
        else:
            st.error("Please enter a title before submitting!")

with tab2:
    st.subheader("Comparison War Room")
    df = get_data()
    if not df.empty and 'Title' in df.columns:
        search = st.selectbox("Select Title to Compare", df['Title'].unique())
        battle_df = df[df['Title'] == search]
        st.dataframe(battle_df, use_container_width=True)
        st.metric("Group Average", round(battle_df['Final_Score'].mean(), 2))

with tab3:
    st.subheader("Personal Rankings")
    df = get_data()
    if not df.empty and 'Title' in df.columns:
        st.bar_chart(df.set_index('Title')['Final_Score'])

with tab4:
    st.subheader("Full History")
    df = get_data()
    st.dataframe(df, use_container_width=True)