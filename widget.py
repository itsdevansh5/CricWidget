import tkinter as tk
from tkinter import ttk, messagebox
import requests

GRAPHQL_URL = "http://localhost:4000/"

class LiveCricketScoreWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Cricket Score")
        self.root.geometry("500x480")
        self.root.attributes('-topmost', True)

        self.style = ttk.Style()
        self.is_dark_mode = False
        self.language = "en"

        self.translations = {
            "en": {
                "select_match": "Select a match",
                "refresh": "Refresh Matches",
                "news": "Show Cricket News",
                "loading_matches": "⏳ Loading live matches...",
                "loading_match": "⏳ Loading match info...",
                "offline": "🛑 Cannot connect to server. Are you offline?",
                "timeout": "⏳ Server took too long to respond.",
                "error_fetch": "⚠️ Error fetching matches: ",
                "no_news": "No news found.",
                "news_title": "Cricket News",
                "server_fail": "⚠️ Could not reach server. Try again later.",
                "error_fetch_match": "⚠️ Error fetching match: ",
            },
            "hi": {
                "select_match": "कोई मैच चुनें",
                "refresh": "मैच रीफ़्रेश करें",
                "news": "क्रिकेट समाचार दिखाएं",
                "loading_matches": "⏳ लाइव मैच लोड हो रहे हैं...",
                "loading_match": "⏳ मैच जानकारी लोड हो रही है...",
                "offline": "🛑 सर्वर से कनेक्ट नहीं हो सका।",
                "timeout": "⏳ सर्वर ने उत्तर देने में अधिक समय लिया।",
                "error_fetch": "⚠️ मैच प्राप्त करने में त्रुटि: ",
                "no_news": "कोई समाचार नहीं मिला।",
                "news_title": "क्रिकेट समाचार",
                "server_fail": "⚠️ सर्वर से कनेक्ट नहीं हो सका।",
                "error_fetch_match": "⚠️ मैच जानकारी प्राप्त करने में त्रुटि: ",
            }
        }

        self.match_data = []
        self.selected_match_id = None

        self.match_var = tk.StringVar()
        self.match_dropdown = ttk.Combobox(root, textvariable=self.match_var, state='readonly', width=60)
        self.match_dropdown.pack(pady=10)
        self.match_dropdown.bind("<<ComboboxSelected>>", self.on_match_selected)

        self.score_label = tk.Label(root, text="Select a match", font=("Arial", 14), wraplength=480, justify="left")
        self.score_label.pack(pady=10)

        self.refresh_button = tk.Button(root, text="Refresh Matches", command=self.fetch_matches)
        self.refresh_button.pack(pady=5)

        self.news_button = tk.Button(root, text="Show Cricket News", command=self.fetch_news)
        self.news_button.pack(pady=5)

        self.dark_mode_button = tk.Button(root, text="🌙 Enable Dark Mode", command=self.toggle_theme)
        self.dark_mode_button.pack(pady=5)

        self.lang_var = tk.StringVar(value="English")
        self.lang_dropdown = ttk.Combobox(root, textvariable=self.lang_var, values=["English", "Hindi"], state='readonly', width=20)
        self.lang_dropdown.pack(pady=5)
        self.lang_dropdown.bind("<<ComboboxSelected>>", self.change_language)

        self.set_light_mode()
        self.fetch_matches()

    def change_language(self, event=None):
        selected = self.lang_var.get()
        self.language = "hi" if selected == "Hindi" else "en"
        self.update_ui_texts()

    def update_ui_texts(self):
        t = self.translations[self.language]
        self.match_dropdown.set(t["select_match"])
        self.refresh_button.config(text=t["refresh"])
        self.news_button.config(text=t["news"])

    def set_dark_mode(self):
        self.root.configure(bg="#2e2e2e")
        self.style.configure("TCombobox", fieldbackground="#3a3a3a", background="#3a3a3a", foreground="white")
        self.score_label.config(bg="#2e2e2e", fg="white")
        self.dark_mode_button.config(text="☀️ Switch to Light Mode", bg="#444", fg="white")
        self.refresh_button.config(bg="#444", fg="white")
        self.news_button.config(bg="#444", fg="white")

    def set_light_mode(self):
        self.root.configure(bg="SystemButtonFace")
        self.style.configure("TCombobox", fieldbackground="white", background="white", foreground="black")
        self.score_label.config(bg="SystemButtonFace", fg="black")
        self.dark_mode_button.config(text="🌙 Enable Dark Mode", bg="SystemButtonFace", fg="black")
        self.refresh_button.config(bg="SystemButtonFace", fg="black")
        self.news_button.config(bg="SystemButtonFace", fg="black")

    def toggle_theme(self):
        if self.is_dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()
        self.is_dark_mode = not self.is_dark_mode

    def fetch_matches(self):
        t = self.translations[self.language]
        self.score_label.config(text=t["loading_matches"])
        query = """
        query {
            liveMatches {
                id
                name
                status
            }
        }
        """
        try:
            response = requests.post(GRAPHQL_URL, json={"query": query}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                raise Exception(data["errors"][0]["message"])
            self.match_data = data['data']['liveMatches']
            match_names = [match['name'] for match in self.match_data]
            self.match_dropdown['values'] = match_names
            self.match_dropdown.set(t["select_match"])
            self.update_ui_texts()
        except requests.exceptions.ConnectionError:
            self.score_label.config(text=t["offline"])
        except requests.exceptions.Timeout:
            self.score_label.config(text=t["timeout"])
        except Exception as e:
            self.score_label.config(text=t["error_fetch"] + str(e))

    def on_match_selected(self, event):
        match_name = self.match_var.get()
        for match in self.match_data:
            if match['name'] == match_name:
                self.selected_match_id = match['id']
                self.update_score()
                return

    def update_score(self):
        if not self.selected_match_id:
            return

        t = self.translations[self.language]
        self.score_label.config(text=t["loading_match"])

        query = f"""
        query {{
            match(matchId: \"{self.selected_match_id}\") {{
                name
                status
                score {{
                    inning
                    r
                    w
                    o
                }}
                weather {{
                    city
                    temperature
                    description
                }}
            }}
        }}
        """
        try:
            response = requests.post(GRAPHQL_URL, json={"query": query}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                raise Exception(data["errors"][0]["message"])

            match = data['data']['match']
            score_text = f"{match['name']}\nStatus: {match['status']}\n"

            for score in match['score']:
                score_text += f"{score['inning']}: {score['r']}/{score['w']} in {score['o']} overs\n"

            if match['weather']:
                weather = match['weather']
                score_text += f"\n🌦 Weather in {weather['city']}: {weather['description']}, {weather['temperature']} °C"
                self.apply_weather_theme(weather['description'])
            else:
                self.apply_weather_theme("")

            self.score_label.config(text=score_text)
            self.root.after(60000, self.update_score)

        except requests.exceptions.RequestException:
            self.score_label.config(text=t["server_fail"])
        except Exception as e:
            self.score_label.config(text=t["error_fetch_match"] + str(e))

    def fetch_news(self):
        t = self.translations[self.language]
        query = """
        query {
            news(query: "cricket") {
                title
                url
                publishedAt
            }
        }
        """
        try:
            response = requests.post(GRAPHQL_URL, json={"query": query}, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                raise Exception(data["errors"][0]["message"])
            articles = data['data']['news']

            if not articles:
                messagebox.showinfo(t["news_title"], t["no_news"])
                return

            news_window = tk.Toplevel(self.root)
            news_window.title(t["news_title"])
            news_window.geometry("600x400")

            for article in articles:
                label = tk.Label(
                    news_window,
                    text=f"- {article['title']} ({article['publishedAt']})",
                    wraplength=580,
                    justify="left",
                    anchor="w"
                )
                label.pack(anchor='w', padx=10, pady=2)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch news: {str(e)}")

    def apply_weather_theme(self, description):
        description = description.lower()
        if self.is_dark_mode:
            return
        if "rain" in description:
            self.root.configure(bg="#a1c4fd")
        elif "sun" in description or "clear" in description:
            self.root.configure(bg="#fff3b0")
        elif "cloud" in description:
            self.root.configure(bg="#d3d3d3")
        else:
            self.root.configure(bg="SystemButtonFace")

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveCricketScoreWidget(root)
    root.mainloop()
