import streamlit as st
import requests

GRAPHQL_URL = "https://cricwidget-graphql-u2sv.vercel.app/"

LANGUAGES = {
    "English": "en",
    "Hindi": "hi"
}

t = {
    "en": {
        "select_match": "🏏 Select a match",
        "refresh": "🔄 Refresh Matches",
        "news": "📰 Show Cricket News",
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
        "select_match": "🏏 कोई मैच चुनें",
        "refresh": "🔄 मैच रीफ़्रेश करें",
        "news": "📰 क्रिकेट समाचार दिखाएं",
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

st.set_page_config(page_title="Live Cricket Score", layout="centered")

language = st.sidebar.selectbox("Language / भाषा:", list(LANGUAGES.keys()))
lang = LANGUAGES[language]
# Theme toggle
is_dark = st.sidebar.toggle("🌙 Dark Mode") if hasattr(st.sidebar, "toggle") else st.sidebar.checkbox("🌙 Dark Mode")

# Apply custom background/text color
if is_dark:
    st.markdown("""
        <style>
        body {
            background-color: #1e1e1e;
            color: white;
        }
        .stApp {
            background-color: #1e1e1e;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body {
            background-color: white;
            color: black;
        }
        .stApp {
            background-color: white;
            color: black;
        }
        </style>
    """, unsafe_allow_html=True)


st.title(t[lang]["select_match"])

if st.button(t[lang]["refresh"]):
    st.session_state.pop("matches", None)

if "matches" not in st.session_state:
    try:
        query = """
        query {
            liveMatches {
                id
                name
                status
            }
        }
        """
        response = requests.post(GRAPHQL_URL, json={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(data["errors"][0]["message"])
        st.session_state.matches = data['data']['liveMatches']
    except:
        st.error(t[lang]["error_fetch"])
        st.stop()

matches = st.session_state.matches
match_names = [match['name'] for match in matches]

selected_name = st.selectbox(t[lang]["select_match"], match_names)
selected_match = next((m for m in matches if m['name'] == selected_name), None)

if selected_match:
    try:
        query = f"""
        query {{
            match(matchId: \"{selected_match['id']}\") {{
                name
                status
                score {{ inning r w o }}
                weather {{ city temperature description }}
            }}
        }}
        """
        response = requests.post(GRAPHQL_URL, json={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(data["errors"][0]["message"])

        match = data['data']['match']
        st.subheader(f"{match['name']} — {match['status']}")

        for s in match['score']:
            st.markdown(f"**{s['inning']}**: {s['r']}/{s['w']} in {s['o']} overs")

        if match['weather']:
            w = match['weather']
            st.info(f"🌦️ Weather in {w['city']}: {w['description']}, {w['temperature']}°C")

    except Exception as e:
        st.error(t[lang]["error_fetch_match"] + str(e))

if st.button(t[lang]["news"]):
    try:
        query = """
        query {
            news(query: "cricket") {
                title
                url
                publishedAt
            }
        }
        """
        response = requests.post(GRAPHQL_URL, json={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = data['data']['news']

        if not articles:
            st.info(t[lang]["no_news"])
        else:
            st.header(t[lang]["news_title"])
            for article in articles:
                st.markdown(f"- [{article['title']}]({article['url']}) _({article['publishedAt']})_")

    except Exception as e:
        st.error(f"Failed to fetch news: {str(e)}")
