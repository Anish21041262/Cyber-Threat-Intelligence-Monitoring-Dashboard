import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="Threat Intelligence Dashboard",
    layout="wide",
    page_icon="🛡️"
)

# -----------------------------
# Dashboard Title
# -----------------------------
st.title("🛡️ Threat Intelligence News Dashboard")

# -----------------------------
# Auto Refresh Every 30 Seconds
# -----------------------------
st_autorefresh(
    interval=30000,
    key="threat_news_refresh"
)

# -----------------------------
# Last Refresh Time
# -----------------------------
st.sidebar.success(
    f"Last Refresh: {datetime.now().strftime('%H:%M:%S')}"
)

# -----------------------------
# RSS Feed Sources
# -----------------------------
RSS_FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
    "Dark Reading": "https://www.darkreading.com/rss.xml",
    "SecurityWeek": "https://feeds.feedburner.com/securityweek"
}

# -----------------------------
# Fetch News Function
# -----------------------------
def fetch_news():

    all_news = []

    for source, url in RSS_FEEDS.items():

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:10]:

                published = entry.get(
                    "published",
                    "N/A"
                )

                summary = entry.get(
                    "summary",
                    "No Summary Available"
                )

                news = {
                    "Source": source,
                    "Title": entry.title,
                    "Published": published,
                    "Summary": summary,
                    "Link": entry.link
                }

                all_news.append(news)

        except Exception as e:
            st.error(
                f"Error fetching data from {source}: {e}"
            )

    return pd.DataFrame(all_news)

# -----------------------------
# Severity Classification
# -----------------------------
def assign_severity(title):

    title = title.lower()

    high_keywords = [
        "ransomware",
        "zero-day",
        "breach",
        "critical",
        "exploit",
        "malware",
        "apt",
        "remote code execution"
    ]

    medium_keywords = [
        "phishing",
        "vulnerability",
        "attack",
        "botnet",
        "trojan"
    ]

    for word in high_keywords:
        if word in title:
            return "High"

    for word in medium_keywords:
        if word in title:
            return "Medium"

    return "Low"

# -----------------------------
# Load News Data
# -----------------------------
df = fetch_news()

# -----------------------------
# Check Empty Data
# -----------------------------
if df.empty:

    st.warning(
        "No cybersecurity news fetched from feeds."
    )

    st.stop()

# -----------------------------
# Add Severity Column
# -----------------------------
df["Severity"] = df["Title"].apply(
    assign_severity
)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

selected_source = st.sidebar.multiselect(
    "Select News Sources",
    df["Source"].unique(),
    default=df["Source"].unique()
)

selected_severity = st.sidebar.multiselect(
    "Select Severity",
    df["Severity"].unique(),
    default=df["Severity"].unique()
)

search_term = st.sidebar.text_input(
    "Search News Headlines"
)

# -----------------------------
# Apply Filters
# -----------------------------
filtered_df = df[
    (df["Source"].isin(selected_source)) &
    (df["Severity"].isin(selected_severity))
]

# -----------------------------
# Search Filter
# -----------------------------
if search_term:

    filtered_df = filtered_df[
        filtered_df["Title"].str.contains(
            search_term,
            case=False,
            na=False
        )
    ]

# -----------------------------
# Dashboard Metrics
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "📰 Total News",
    len(filtered_df)
)

col2.metric(
    "🔴 High Severity",
    len(
        filtered_df[
            filtered_df["Severity"] == "High"
        ]
    )
)

col3.metric(
    "🌐 Sources",
    filtered_df["Source"].nunique()
)

# -----------------------------
# Severity Pie Chart
# -----------------------------
fig = px.pie(
    filtered_df,
    names="Severity",
    title="Threat Severity Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------
# Display Latest News
# -----------------------------
st.subheader(
    "📢 Latest Cybersecurity News"
)

for index, row in filtered_df.iterrows():

    severity_color = {
        "High": "🔴",
        "Medium": "🟠",
        "Low": "🟢"
    }

    st.markdown(f"""
    ### {severity_color[row['Severity']]} {row['Title']}

    **Source:** {row['Source']}  
    **Published:** {row['Published']}  
    **Severity:** {row['Severity']}

    {row['Summary'][:300]}...

    [🔗 Read Full Article]({row['Link']})

    ---
    """)
