from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from textblob import TextBlob
import sqlite3
import os
import random
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout

Window.size = (360, 640)


# ------------- Screens -------------
class MainMenuScreen(Screen):
    pass

class MoodScreen(Screen):
    pass

class JournalScreen(Screen):
    pass

class BreathingScreen(Screen):
    pass

class TipsScreen(Screen):
    pass

class GameMenuScreen(Screen):
    pass

class ProgressScreen(Screen):
    pass


# ------------- Main App -------------
class WellnessApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        # Ensure database exists
        self.init_db()
        return Builder.load_file("app.kv")

    # ---------------- Mood/Journal Analysis ----------------
    def analyze_mood(self, text):
        if not text.strip():
            return "Please write something."
        analysis = TextBlob(text).sentiment.polarity
        if analysis > 0.2:
            return "You seem positive today! Keep it up! 😊"
        elif analysis < -0.2:
            return "You're feeling low. It's okay ❤️ Take it slow today."
        else:
            return "Your mood seems neutral. Stay mindful 😊"

    def analyze_journal(self, text):
        return self.analyze_mood(text)

    # ---------------- Database Setup ----------------
    def init_db(self):
        if not os.path.exists("database/mood_journal.db"):
            os.makedirs("database", exist_ok=True)
            conn = sqlite3.connect("database/mood_journal.db")
            c = conn.cursor()
            c.execute("""CREATE TABLE mood_entries (
                            id INTEGER PRIMARY KEY,
                            mood TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )""")
            c.execute("""CREATE TABLE journal_entries (
                            id INTEGER PRIMARY KEY,
                            entry TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )""")
            conn.commit()
            conn.close()

    # ---------------- Progress Tracker ----------------
    def get_mood_count(self):
        conn = sqlite3.connect("database/mood_journal.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM mood_entries")
        count = c.fetchone()[0]
        conn.close()
        return count

    def get_journal_count(self):
        conn = sqlite3.connect("database/mood_journal.db")
        c = conn.cursor()
        c.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM journal_entries")
        count = c.fetchone()[0]
        conn.close()
        return count

    # ---------------- Breathing Exercise ----------------
    def start_breathing(self, label_widget):
        self.breathing_texts = ["Inhale... 🌬️", "Hold... 🤚", "Exhale... 💨", "Relax... 🧘"]
        self.breathing_index = 0
        self.breathing_label = label_widget
        Clock.schedule_interval(self.update_breathing, 2)

    def update_breathing(self, dt):
        self.breathing_label.text = self.breathing_texts[self.breathing_index]
        self.breathing_index = (self.breathing_index + 1) % len(self.breathing_texts)

    # ---------------- Color Game ----------------
    def start_color_game(self, layout_widget):
        layout_widget.clear_widgets()
        self.color_names = ["Red", "Green", "Blue", "Yellow"]
        self.correct_color = random.choice(self.color_names)

        layout_widget.add_widget(MDLabel(
            text=f"Click the button: {self.correct_color}",
            halign="center",
            font_style="H5"
        ))

        grid = GridLayout(cols=2, spacing=10, padding=10)
        for color in self.color_names:
            btn = MDRaisedButton(text=color,
                                 md_bg_color=(random.random(), random.random(), random.random(),1),
                                 on_release=self.check_color)
            grid.add_widget(btn)
        layout_widget.add_widget(grid)

    def check_color(self, instance):
        if instance.text == self.correct_color:
            instance.text = "✔ Correct!"
        else:
            instance.text = "❌ Wrong!"
        # Restart game after 1 second
        Clock.schedule_once(lambda dt: self.start_color_game(instance.parent.parent), 1)

    # ---------------- Memory Puzzle ----------------
    def start_memory_game(self, layout_widget):
        layout_widget.clear_widgets()
        self.memory_grid = GridLayout(cols=4, spacing=5, padding=5)
        self.memory_values = list(range(8)) * 2  # 8 pairs
        random.shuffle(self.memory_values)
        self.memory_buttons = []

        self.first_button = None
        self.second_button = None

        for val in self.memory_values:
            btn = MDRaisedButton(text="?", on_release=lambda b, v=val: self.reveal_memory(b, v))
            self.memory_buttons.append(btn)
            self.memory_grid.add_widget(btn)

        layout_widget.add_widget(self.memory_grid)

    def reveal_memory(self, button, value):
        button.text = str(value)
        if not self.first_button:
            self.first_button = (button, value)
        elif not self.second_button:
            self.second_button = (button, value)
            Clock.schedule_once(self.check_memory_match, 0.5)

    def check_memory_match(self, dt):
        b1, v1 = self.first_button
        b2, v2 = self.second_button
        if v1 == v2:
            b1.disabled = True
            b2.disabled = True
        else:
            b1.text = "?"
            b2.text = "?"
        self.first_button = None
        self.second_button = None


if __name__ == "__main__":
    WellnessApp().run()
