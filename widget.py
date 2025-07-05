import tkinter as tk
from tkinter import ttk, messagebox
import requests

# GraphQL API URL
GRAPHQL_URL = "http://localhost:4000/"

class LiveCricketScoreWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Cricket Score")
        self.root.geometry("500x450")
        self.root.attributes('-topmost', True)

        self.style = ttk.Style()
        self.is_dark_mode = False

        self.match_data = []
        self.selected_match_id = None
        self.selected_match_city = None

        # Match Selection
        self.match_var = tk.StringVar()
        self.match_dropdown = ttk.Combobox(root, textvariable=self.match_var, state='readonly', width=60)
        self.match_dropdown.pack(pady=10)
        self.match_dropdown.bind("<<ComboboxSelected>>", self.on_match_selected)

        # Score Display
        self.score_label = tk.Label(root, text="Select a match", font=("Arial", 14), wraplength=480, justify="left")
        self.score_label.pack(pady=10)

        # Buttons
        self.refresh_button = tk.Button(root, text="Refresh Matches", command=self.fetch_matches)
        self.refresh_button.pack(pady=5)

        self.news_button = tk.Button(root, text="Show Cricket News", command=self.fetch_news)
        self.news_button.pack(pady=5)

        self.dark_mode_button = tk.Button(root, text="🌙 Enable Dark Mode", command=self.toggle_theme)
        self.dark_mode_button.pack(pady=5)

        self.set_light_mode()
        self.fetch_matches()

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
            self.match_dropdown.set("Select a match")
        except requests.exceptions.ConnectionError:
            self.score_label.config(text="🛑 Cannot connect to server. Are you offline?")
        except requests.exceptions.Timeout:
            self.score_label.config(text="⏳ Server took too long to respond.")
        except Exception as e:
            self.score_label.config(text=f"⚠️ Error fetching matches: {str(e)}")

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
                score_text += f"\nWeather in {weather['city']}: {weather['description']}, {weather['temperature']} °C"

            self.score_label.config(text=score_text)
            self.root.after(60000, self.update_score)

        except requests.exceptions.RequestException:
            self.score_label.config(text="⚠️ Could not reach server. Try again later.")
        except Exception as e:
            self.score_label.config(text=f"⚠️ Error fetching match: {str(e)}")

    def fetch_news(self):
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
                messagebox.showinfo("News", "No news found.")
                return

            news_window = tk.Toplevel(self.root)
            news_window.title("Cricket News")
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


if __name__ == "__main__":
    root = tk.Tk()
    app = LiveCricketScoreWidget(root)
    root.mainloop()
