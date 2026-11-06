"""Green Transition Pulse - dashboard for the municipal sustainability team.

Run:  .venv/bin/streamlit run app.py
"""

from datetime import datetime, timedelta, timezone

import altair as alt
import pandas as pd
import streamlit as st

import config

st.set_page_config(page_title="Green Transition Pulse", page_icon="🌱", layout="wide")

LINE_COLORS = {
    "Zonnepanelen": "#e6a100",
    "Warmtepomp": "#d1495b",
    "Isolatie": "#00798c",
    "Laadpalen": "#6a4c93",
    "Stroomnet": "#8d99ae",
}


@st.cache_data(ttl=300)
def load():
    df = pd.read_csv(config.ITEMS_CSV)
    runs = pd.read_csv(config.RUNS_CSV)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    df["collected_at"] = pd.to_datetime(df["collected_at"], utc=True)
    df["line"] = df["lines"].str.split(",")
    return df.explode("line"), runs


df, runs = load()

# ---------------- Sidebar ----------------
st.sidebar.title("🌱 Green Transition Pulse")
st.sidebar.caption("How Dutch news and Bluesky talk about going green at home, and about the grid that has to carry it.")

days = st.sidebar.slider("Period (days)", 7, 60, 21)
bucket = st.sidebar.radio("Group per", ["day", "week"], horizontal=True)
kinds = st.sidebar.multiselect("Voices", ["news", "public"], default=["news", "public"],
                               format_func=lambda k: "News media" if k == "news" else "Public (Bluesky)")
model = st.sidebar.radio("Model", ["main", "cmp"],
                         format_func=lambda m: "XLM-RoBERTa (main, 3 classes)" if m == "main" else "RobBERT Dutch (comparison, 2 classes)")
min_n = st.sidebar.number_input("Hide points based on fewer than … items", 1, 50, 5)

last_run = pd.to_datetime(runs["started_at"]).max() if len(runs) else None
st.sidebar.markdown("---")
st.sidebar.metric("Items stored", f"{df['id'].nunique():,}")
if last_run is not None:
    st.sidebar.caption(f"Last collection: {last_run:%d %b %H:%M} UTC · {len(runs)} rounds so far")

# ---------------- Filter ----------------
since = datetime.now(timezone.utc) - timedelta(days=days)
mood_col = f"{model}_mood"
view = df[(df["published_at"] >= since) & (df["kind"].isin(kinds))].copy()
freq = "D" if bucket == "day" else "W-MON"
view["period"] = view["published_at"].dt.tz_convert(None).dt.to_period(freq[0]).dt.start_time

st.title("Green Transition Pulse")
st.warning(
    "**Read with care.** This shows the tone of what is *written* online, not what all residents think. "
    "Renters, older people and people who don't post online are missing. A line based on a handful of items "
    "can swing on one post. Always look at the items behind a change before acting on it.",
    icon="⚠️",
)

if view.empty:
    st.info("No items in this selection yet.")
    st.stop()

# ---------------- KPI row: now vs before ----------------
half = datetime.now(timezone.utc) - timedelta(days=days / 2)
cols = st.columns(len(config.LINES))
for col, name in zip(cols, config.LINES):
    sub = view[view["line"] == name]
    recent, older = sub[sub["published_at"] >= half], sub[sub["published_at"] < half]
    delta = (recent[mood_col].mean() - older[mood_col].mean()) if len(recent) and len(older) else None
    col.metric(
        f"{name}{' 🔌' if config.LINES[name]['side'] == 'bottleneck' else ''}",
        f"{sub[mood_col].mean():+.2f}" if len(sub) else "–",
        f"{delta:+.2f} vs first half" if delta is not None and pd.notna(delta) else None,
        help=f"{len(sub)} items. Mood = P(positive) − P(negative), from −1 to +1.",
    )

# ---------------- Mood over time ----------------
agg = (view.groupby(["period", "line"])
       .agg(mood=(mood_col, "mean"), n=("id", "count"))
       .reset_index())
agg = agg[agg["n"] >= min_n]

st.subheader(f"Mood per {bucket}")
st.caption("Each dot is one period. Hover to see how many items it is based on. "
           "Green measures in colour, the grid bottleneck in grey-blue.")
color = alt.Color("line:N", title=None,
                  scale=alt.Scale(domain=list(LINE_COLORS), range=list(LINE_COLORS.values())))
base = alt.Chart(agg).encode(
    x=alt.X("period:T", title=None),
    y=alt.Y("mood:Q", title="Mood (−1 negative … +1 positive)", scale=alt.Scale(domain=[-1, 1])),
    color=color,
    tooltip=[alt.Tooltip("period:T", title=bucket), "line:N",
             alt.Tooltip("mood:Q", format="+.2f"), alt.Tooltip("n:Q", title="items")],
)
zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#999", strokeDash=[4, 4]).encode(y="y:Q")
st.altair_chart(
    (zero + base.mark_line(strokeWidth=2.5) + base.mark_circle().encode(size=alt.Size("n:Q", legend=None)))
    .properties(height=380),
    use_container_width=True,
)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Volume")
    st.caption("How much is written. A peak often means something happened.")
    vol = view.groupby(["period", "line"]).size().reset_index(name="n")
    st.altair_chart(
        alt.Chart(vol).mark_bar().encode(x=alt.X("period:T", title=None), y=alt.Y("n:Q", title="items"),
                                         color=color, tooltip=["period:T", "line:N", "n:Q"])
        .properties(height=260),
        use_container_width=True,
    )
with c2:
    st.subheader("Media vs public")
    st.caption("Average mood per line, news headlines vs Bluesky posts.")
    mp = (df[df["published_at"] >= since].groupby(["line", "kind"])
          .agg(mood=(mood_col, "mean"), n=("id", "count")).reset_index())
    mp["voice"] = mp["kind"].map({"news": "News media", "public": "Public (Bluesky)"})
    st.altair_chart(
        alt.Chart(mp).mark_bar().encode(
            y=alt.Y("line:N", title=None), x=alt.X("mood:Q", title="mood", scale=alt.Scale(domain=[-1, 1])),
            yOffset="voice:N",
            color=alt.Color("voice:N", title=None, scale=alt.Scale(range=["#8c8c8c", "#2a9d8f"])),
            tooltip=["line:N", "voice:N", alt.Tooltip("mood:Q", format="+.2f"), "n:Q"],
        ).properties(height=260),
        use_container_width=True,
    )

# ---------------- Drill-down ----------------
st.subheader("What's behind a peak or dip?")
d1, d2, d3 = st.columns([2, 2, 1])
line_pick = d1.selectbox("Line", list(config.LINES))
periods = sorted(view.loc[view["line"] == line_pick, "period"].unique(), reverse=True)
if periods:
    period_pick = d2.selectbox(bucket.capitalize(), periods, format_func=lambda p: pd.Timestamp(p).strftime("%a %d %b %Y"))
    order = d3.radio("Sort", ["most negative", "most positive"])
    items = view[(view["line"] == line_pick) & (view["period"] == period_pick)]
    items = items.sort_values(mood_col, ascending=(order == "most negative"))
    st.caption(f"{len(items)} items · average mood {items[mood_col].mean():+.2f}")
    st.dataframe(
        items[["published_at", "kind", "source", "text", "main_label", "main_mood", "cmp_label", "url"]]
        .rename(columns={"published_at": "time (UTC)", "main_label": "XLM-R", "main_mood": "XLM-R mood",
                         "cmp_label": "RobBERT"}),
        hide_index=True, use_container_width=True,
        column_config={"url": st.column_config.LinkColumn("link"),
                       "XLM-R mood": st.column_config.NumberColumn(format="%+.2f"),
                       "text": st.column_config.TextColumn(width="large")},
    )

st.caption("Not for: judging individual people or neighbourhoods, or concluding that silence means satisfaction. "
           "Sources: Google News NL, Bluesky (public posts, no names stored), NOS, NU.nl, Tweakers, Energeia.")
