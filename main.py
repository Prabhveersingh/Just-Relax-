import streamlit as st
from textblob import TextBlob
import sqlite3
import os
import random

DB_PATH = "mood_journal.db"


# ----------------- DB Helpers -----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY,
            mood TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY,
            entry TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_mood(mood_label: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO mood_entries (mood) VALUES (?)", (mood_label,))
    conn.commit()
    conn.close()


def save_journal(entry: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO journal_entries (entry) VALUES (?)", (entry,))
    conn.commit()
    conn.close()


def get_mood_days():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM mood_entries")
    count = c.fetchone()[0] or 0
    conn.close()
    return count


def get_journal_days():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM journal_entries")
    count = c.fetchone()[0] or 0
    conn.close()
    return count


# ----------------- Mood & Journal Logic -----------------
def analyze_mood(text: str):
    text = text.strip()
    if not text:
        return "Please write something.", None

    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.2:
        msg = "You seem positive today! Keep it up! 😊"
        label = "positive"
    elif polarity < -0.2:
        msg = "You're feeling low. It's okay ❤️ Take it slow today."
        label = "negative"
    else:
        msg = "Your mood seems neutral. Stay mindful 😊"
        label = "neutral"

    return msg, label


# ----------------- Pages -----------------
def page_mood():
    st.header("🧠 Mood Check")

    text = st.text_area("How are you feeling today?", height=150, placeholder="Type your thoughts here...")

    if st.button("Analyze Mood"):
        msg, label = analyze_mood(text)
        if label is None:
            st.warning(msg)
        else:
            save_mood(label)
            st.success(msg)
            st.info(f"Saved mood as: **{label.capitalize()}**")


def page_journal():
    st.header("📓 Journal")

    text = st.text_area("Write your journal entry:", height=220, placeholder="Write anything on your mind...")

    col1, col2 = st.columns(2)
    with col1:
        save_clicked = st.button("Save Entry")
    with col2:
        analyze_clicked = st.button("Analyze Only")

    if save_clicked:
        if not text.strip():
            st.warning("Please write something before saving.")
        else:
            save_journal(text)
            msg, _ = analyze_mood(text)
            st.success("Journal entry saved! ✅")
            st.info(msg)

    if analyze_clicked:
        msg, _ = analyze_mood(text)
        if msg == "Please write something.":
            st.warning(msg)
        else:
            st.info(msg)


def page_breathing():
    st.header("🌬️ Breathing Exercise")

    st.write("A simple 4-4-4 breathing cycle to calm yourself:")

    st.markdown(
        """
        1. **Inhale** slowly for 4 seconds  
        2. **Hold** your breath for 4 seconds  
        3. **Exhale** gently for 4 seconds  
        4. Repeat for 5–10 cycles 🧘
        """
    )

    if st.button("Show a random calming tip"):
        tips = [
            "Close your eyes and focus only on your breath.",
            "Relax your shoulders and unclench your jaw.",
            "Notice 3 things you can see, 3 you can hear, 3 you can feel.",
            "It's okay to pause. You're allowed to rest. 💙",
        ]
        st.success(random.choice(tips))


# ----------------- Color Game -----------------
def init_color_game_state():
    if "color_target" not in st.session_state:
        colors = ["Red", "Green", "Blue", "Yellow"]
        st.session_state.color_options = colors
        st.session_state.color_target = random.choice(colors)
        st.session_state.color_result = ""


def reset_color_game():
    colors = ["Red", "Green", "Blue", "Yellow"]
    st.session_state.color_options = colors
    st.session_state.color_target = random.choice(colors)
    st.session_state.color_result = ""


def page_games():
    st.header("🎮 Mini Game – Color Match")

    init_color_game_state()

    st.write(f"Click the button with this color name: **{st.session_state.color_target}**")

    cols = st.columns(2)
    for i, color in enumerate(st.session_state.color_options):
        with cols[i % 2]:
            if st.button(color, key=f"color_btn_{i}"):
                if color == st.session_state.color_target:
                    st.session_state.color_result = "✅ Correct! Great job!"
                    reset_color_game()
                else:
                    st.session_state.color_result = "❌ Wrong! Try again."

    if st.session_state.color_result:
        if "Correct" in st.session_state.color_result:
            st.success(st.session_state.color_result)
        else:
            st.error(st.session_state.color_result)


# ----------------- Progress Page -----------------
def page_progress():
    st.header("📊 Your Progress")

    mood_days = get_mood_days()
    journal_days = get_journal_days()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Days you checked your mood", mood_days)
    with col2:
        st.metric("Days you wrote a journal", journal_days)

    if mood_days == 0 and journal_days == 0:
        st.info("No data yet. Start by adding a mood or journal entry today 😊")


# ----------------- Main -----------------
def main():
    st.set_page_config(
        page_title="Wellness & Mood Tracker",
        page_icon="😊",
        layout="centered",
    )

    init_db()

    st.title("🌈 Wellness & Mood Tracker")

    page = st.sidebar.radio(
        "Navigate",
        ["Mood Check", "Journal", "Breathing Exercise", "Games", "Progress"],
    )

    if page == "Mood Check":
        page_mood()
    elif page == "Journal":
        page_journal()
    elif page == "Breathing Exercise":
        page_breathing()
    elif page == "Games":
        page_games()
    elif page == "Progress":
        page_progress()


if __name__ == "__main__":
    main()
