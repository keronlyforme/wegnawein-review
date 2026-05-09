import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Standard v1.0 | Editorial Dashboard", layout="wide")

# Define weights
MOVIE_WEIGHTS = {"Story_Screenplay": 0.25, "Characters_Acting": 0.20, "Directing": 0.15, "Visuals": 0.15, "Sound_Music": 0.10, "Editing_Pacing": 0.10, "Impact": 0.05}
BOOK_WEIGHTS = {"Prose_Writing": 0.30, "Plot_Structure": 0.25, "Character_Depth": 0.20, "Pacing": 0.15, "Themes_Impact": 0.10}

DATA_FILE = "editorial_data.csv"

def save_data(new_entry):
    df = pd.read_csv(DATA_FILE) if os.path.exists(DATA_FILE) else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- UI ---
st.title("⚖️ Editorial Review Standard v1.0")

# THE RULES SECTION (New)
with st.expander("📖 The Standard Rules (Read First)"):
    st.write("""
    1. The 5-Point Baseline: A score of 5 means 'Average/Fine'. Only go higher if it's special.
    2. Context Matters: Rate a comedy based on how well it 'comedies', not compared to a drama.
    3. The 10 Rule: A '10' in any category must be genre-defining.
    """)

tab1, tab2, tab3, tab4 = st.tabs(["✍️ Submit Review", "🤝 Group War Room", "📊 Analytics", "📜 Archive"])

with tab1:
    c1, c2, c3 = st.columns([1, 1, 2])
    reviewer = c1.selectbox("Reviewer", ["kerod", "gubeleye", "kaleab", "kalsis"])
    m_type = c2.radio("Media Type", ["Movie", "Book"])
    title = c3.text_input("Title (Exact name for group matching)")

    st.divider()
    scores = {}
    current_weights = MOVIE_WEIGHTS if m_type == "Movie" else BOOK_WEIGHTS
    
    st.subheader(f"Category Scoring (1-10) for {m_type}")
    cols = st.columns(2)
    for i, cat in enumerate(current_weights.keys()):
        scores[cat] = cols[i % 2].slider(cat.replace("_", " "), 1, 10, 5, key=f"{m_type}_{cat}")

    if st.button("Submit to Records"):
        if title:
            final_score = sum(scores[c] * current_weights[c] for c in current_weights)
            entry = {"Date": datetime.now().strftime("%Y-%m-%d"), "Reviewer": reviewer, "Type": m_type, "Title": title.strip().title(), "Final_Score": round(final_score, 2)}
            save_data(entry)
            st.success(f"Saved! {title} Final Score: {round(final_score, 2)}")
        else:
            st.error("Missing Title!")

with tab2:
    st.subheader("Comparison War Room")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        search = st.selectbox("Select Title to Compare", df['Title'].unique())
        battle_df = df[df['Title'] == search]
        st.dataframe(battle_df, use_container_width=True)
        st.metric("Group Average", round(battle_df['Final_Score'].mean(), 2))
    else:
        st.info("No data yet.")

with tab3:
    st.subheader("Personal Rankings")
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.bar_chart(df.set_index('Title')['Final_Score'])

with tab4:
    if os.path.exists(DATA_FILE):
        st.dataframe(pd.read_csv(DATA_FILE), use_container_width=True)