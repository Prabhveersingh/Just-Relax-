import streamlit as st
from textblob import TextBlob
import sqlite3
import os
import random

# ----------------- DB CONFIG -----------------
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "mood_journal.db")


# ----------------- DB Helpers -----------------
def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
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
    row = c.fetchone()
    count = row[0] if row and row[0] is not None else 0
    conn.close()
    return count


def get_journal_days():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM journal_entries")
    row = c.fetchone()
    count = row[0] if row and row[0] is not None else 0
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


# ----------------- Color Game State -----------------
def init_color_game_state():
    if "color_options" not in st.session_state:
        reset_color_game()
    if "color_result" not in st.session_state:
        st.session_state.color_result = ""


def reset_color_game():
    colors = ["Red", "Green", "Blue", "Yellow"]
    st.session_state.color_options = colors
    st.session_state.color_target = random.choice(colors)
    st.session_state.color_result = ""


def handle_color_click(color_clicked: str):
    target = st.session_state.color_target
    if color_clicked == target:
        st.session_state.color_result = "✅ Correct! Great job!"
        reset_color_game()
    else:
        st.session_state.color_result = "❌ Wrong! Try again."


# ----------------- Memory Game State -----------------
def init_memory_game_state():
    if "memory_values" not in st.session_state:
        values = list(range(8)) * 2  # 8 pairs
        random.shuffle(values)
        st.session_state.memory_values = values
        st.session_state.memory_flipped = [False] * len(values)
        st.session_state.first_index = None
        st.session_state.second_index = None
        st.session_state.memory_message = ""


def reset_memory_game():
    values = list(range(8)) * 2
    random.shuffle(values)
    st.session_state.memory_values = values
    st.session_state.memory_flipped = [False] * len(values)
    st.session_state.first_index = None
    st.session_state.second_index = None
    st.session_state.memory_message = ""


def resolve_previous_pair():
    fi = st.session_state.first_index
    si = st.session_state.second_index
    if fi is None or si is None:
        return

    vals = st.session_state.memory_values
    flipped = st.session_state.memory_flipped

    if vals[fi] != vals[si]:
        flipped[fi] = False
        flipped[si] = False

    st.session_state.first_index = None
    st.session_state.second_index = None


def handle_memory_click(index: int):
    flipped = st.session_state.memory_flipped
    vals = st.session_state.memory_values

    # If previous pair exists, resolve it first
    if st.session_state.first_index is not None and st.session_state.second_index is not None:
        resolve_previous_pair()

    # Ignore click on already flipped button
    if flipped[index]:
        return

    if st.session_state.first_index is None:
        st.session_state.first_index = index
        flipped[index] = True
        st.session_state.memory_message = ""
    else:
        st.session_state.second_index = index
        flipped[index] = True
        if vals[st.session_state.first_index] == vals[index]:
            st.session_state.memory_message = "✅ Match!"
        else:
            st.session_state.memory_message = "❌ Not a match."

    # Check win
    if all(st.session_state.memory_flipped):
        st.session_state.memory_message = "🏆 All pairs found! Click 'Reset game' to play again."


# ----------------- Breathing Exercise State -----------------
BREATH_STEPS = [
    "Inhale... 🌬️ (4 seconds)",
    "Hold... 🤚 (4 seconds)",
    "Exhale... 💨 (4 seconds)",
    "Relax... 🧘 (breathe normally)",
]


def init_breath_state():
    if "breath_index" not in st.session_state:
        st.session_state.breath_index = 0


def next_breath_step():
    st.session_state.breath_index = (st.session_state.breath_index + 1) % len(BREATH_STEPS)


def reset_breath():
    st.session_state.breath_index = 0


# ----------------- Pages -----------------
def page_main_menu():
    st.header("🌈 Wellness & Mood Tracker")

    st.markdown(
        """
Welcome to your **all-in-one wellness app** (web version of your Kivy project) 💚  

Use the **sidebar** to navigate between:

- 🧠 **Mood Check** – analyze how you're feeling  
- 📓 **Journal** – write & reflect  
- 🌬️ **Breathing** – quick calm-down guide  
- 💡 **Tips** – self-care suggestions  
- 🎮 **Games** – Color game & Memory puzzle  
- 📊 **Progress** – see how consistent you are  
        """
    )


def page_mood():
    st.header("🧠 Mood Check")

    text = st.text_area(
        "How are you feeling today?",
        height=150,
        placeholder="Type your thoughts here...",
    )

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

    text = st.text_area(
        "Write your journal entry:",
        height=220,
        placeholder="Write anything on your mind...",
    )

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

    init_breath_state()

    st.write("Follow the 4-step cycle to calm your mind:")

    st.markdown(
        """
1. **Inhale** slowly through your nose  
2. **Hold** your breath gently  
3. **Exhale** through your mouth  
4. **Relax** your body and mind  

You can tap **Next step** to move through the cycle at your own pace.
        """
    )

    st.subheader("Current step:")
    st.info(BREATH_STEPS[st.session_state.breath_index])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next step ➡️"):
            next_breath_step()
    with col2:
        if st.button("Reset cycle 🔁"):
            reset_breath()

    if st.button("Give me a calming tip ✨"):
        tips = [
            "Close your eyes and notice the airflow in your nose.",
            "Relax your shoulders and let them drop down.",
            "Unclench your jaw and soften your face muscles.",
            "Put one hand on your chest and feel it rise and fall.",
            "Tell yourself: 'I am safe in this moment.' 💙",
        ]
        st.success(random.choice(tips))


def page_tips():
    st.header("💡 Self-care Tips")

    st.markdown(
        """
Some quick **wellness tips** you can try today:

- 🕒 Take a **5-minute break** away from your screen  
- 💧 Drink a glass of water slowly  
- 🚶 Go for a **short walk** or stretch your legs  
- 📵 Put your phone away for 10 minutes  
- 🎧 Listen to a song that makes you feel calm  
- ✍️ Write down 3 things you're grateful for  
- 😴 Try to sleep and wake up at a consistent time  
        """
    )

    if st.button("Give me a random tip 🎲"):
        tips = [
            "Message a friend and ask how they are feeling.",
            "Clean a small corner of your room or desk.",
            "Light a candle or smell something pleasant.",
            "Breathe in for 4 seconds, out for 6 seconds – repeat 10 times.",
            "Say out loud: 'It's okay to not be okay all the time.'",
        ]
        st.info(random.choice(tips))


def page_games():
    st.header("🎮 Games")

    tab1, tab2 = st.tabs(["🎨 Color Match", "🧠 Memory Puzzle"])

    # ---------- Color Game ----------
    with tab1:
        init_color_game_state()
        st.subheader("Color Match Game")

        st.write(f"Click the button matching this color name: **{st.session_state.color_target}**")

        # Har color ka proper HTML color
        color_to_hex = {
            "Red": "#FF4B4B",
            "Green": "#22C55E",
            "Blue": "#3B82F6",
            "Yellow": "#EAB308",
        }

        cols = st.columns(2)
        for i, color in enumerate(st.session_state.color_options):
            with cols[i % 2]:
                # Upar ek coloured box dikhayenge
                st.markdown(
                    f"""
                    <div style="
                        width: 100%;
                        height: 36px;
                        background: {color_to_hex.get(color, '#999999')};
                        border-radius: 8px;
                        margin-bottom: 6px;
                    "></div>
                    """,
                    unsafe_allow_html=True,
                )
                # Neeche normal button (text)
                if st.button(color, key=f"color_btn_{i}"):
                    handle_color_click(color)

        if st.session_state.color_result:
            if "Correct" in st.session_state.color_result:
                st.success(st.session_state.color_result)
            else:
                st.error(st.session_state.color_result)

        if st.button("Reset color game 🔁"):
            reset_color_game()
            st.info("New color selected. Play again!")

    # ---------- Memory Game ----------
    with tab2:
        st.subheader("Memory Pair Match")

        init_memory_game_state()

        if st.button("Reset memory game 🔁"):
            reset_memory_game()

        values = st.session_state.memory_values
        flipped = st.session_state.memory_flipped

        # 4 x 4 grid
        for row in range(4):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                label = str(values[idx]) if flipped[idx] else "?"
                with cols[col]:
                    st.button(
                        label,
                        key=f"mem_{idx}",
                        on_click=handle_memory_click,
                        args=(idx,),
                    )

        if st.session_state.memory_message:
            if "✅" in st.session_state.memory_message or "🏆" in st.session_state.memory_message:
                st.success(st.session_state.memory_message)
            else:
                st.warning(st.session_state.memory_message)


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

    # Sidebar navigation (like your ScreenManager)
    page = st.sidebar.radio(
        "Navigate",
        [
            "🏠 Main Menu",
            "🧠 Mood Check",
            "📓 Journal",
            "🌬️ Breathing Exercise",
            "💡 Tips",
            "🎮 Games",
            "📊 Progress",
        ],
    )

    if page == "🏠 Main Menu":
        page_main_menu()
    elif page == "🧠 Mood Check":
        page_mood()
    elif page == "📓 Journal":
        page_journal()
    elif page == "🌬️ Breathing Exercise":
        page_breathing()
    elif page == "💡 Tips":
        page_tips()
    elif page == "🎮 Games":
        page_games()
    elif page == "📊 Progress":
        page_progress()


if __name__ == "__main__":
    main()
