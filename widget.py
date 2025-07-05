import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

# GraphQL API URL
GRAPHQL_URL = "http://localhost:4000/"

class LiveCricketScoreWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Cricket Score")
        self.root.geometry("500x400")
        self.root.attributes('-topmost', True)

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

        # Refresh Button
        self.refresh_button = tk.Button(root, text="Refresh Matches", command=self.fetch_matches)
        self.refresh_button.pack(pady=5)

        # News Button
        self.news_button = tk.Button(root, text="Show Cricket News", command=self.fetch_news)
        self.news_button.pack(pady=5)

        # Initial fetch
        self.fetch_matches()

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
            response = requests.post(GRAPHQL_URL, json={"query": query})
            data = response.json()
            self.match_data = data['data']['liveMatches']
            match_names = [match['name'] for match in self.match_data]
            self.match_dropdown['values'] = match_names
            self.match_dropdown.set("Select a match")
        except Exception as e:
            self.score_label.config(text=f"Error fetching matches: {str(e)}")

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
            response = requests.post(GRAPHQL_URL, json={"query": query})
            match = response.json()['data']['match']

            score_text = f"{match['name']}\nStatus: {match['status']}\n"

            for score in match['score']:
                score_text += f"{score['inning']}: {score['r']}/{score['w']} in {score['o']} overs\n"

            if match['weather']:
                weather = match['weather']
                score_text += f"\nWeather in {weather['city']}: {weather['description']}, {weather['temperature']} °C"

            self.score_label.config(text=score_text)

            self.root.after(60000, self.update_score)

        except Exception as e:
            self.score_label.config(text=f"Error fetching match: {str(e)}")

    def fetch_news(self):
        query = """
        query {
            news(query: \"cricket\") {
                title
                url
                publishedAt
            }
        }
        """
        try:
            response = requests.post(GRAPHQL_URL, json={"query": query})
            articles = response.json()['data']['news']

            if not articles:
                messagebox.showinfo("News", "No news found.")
                return

            news_window = tk.Toplevel(self.root)
            news_window.title("Cricket News")
            news_window.geometry("600x400")

            for article in articles:
                label = tk.Label(news_window, text=f"- {article['title']} ({article['publishedAt']})", wraplength=580, justify="left", anchor="w")
                label.pack(anchor='w', padx=10, pady=2)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch news: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LiveCricketScoreWidget(root)
    root.mainloop()
