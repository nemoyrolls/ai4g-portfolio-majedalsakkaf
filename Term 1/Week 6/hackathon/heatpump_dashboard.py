#!/usr/bin/env python3
"""
Heat Pump Pulse: dashboard (Hackathon 6, step 3 of the pipeline)

Shows how the public debate about heat pumps on Bluesky changes over time, for a
consumer advice team such as the Energy Saving Trust's: which concern (cost, installers,
cold, noise, myths) to address first, and when a news event calls for extra explanation.

Reads heatpump.db READ-ONLY, so it never gets in the way of the collector or the analyser.

Run (Linux, from the project folder)
  venv/bin/pip install streamlit                                   (once)
  venv/bin/streamlit run heatpump_dashboard.py --browser.gatherUsageStats false
                                       # open http://localhost:8501
  venv/bin/streamlit run heatpump_dashboard.py --browser.gatherUsageStats false --server.address 0.0.0.0
                                       # also reachable from other devices on the same Wi-Fi:
                                       # http://<ip of this laptop>:8501  (find the ip with: hostname -I)
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).resolve().with_name("heatpump.db")
LOCAL_TZ = "Europe/London"          # the user is a UK team, so times are shown in UK time
MIN_N = 5                           # time periods with fewer scored posts are marked "few posts"
THEME_MIN_N = 15                    # themes need more posts before they are ranked
THEMES = ["cost/grants", "installers", "performance/cold", "noise", "myths/misinformation", "politics/policy"]

# Colours (validated reference palette): diverging blue (positive) <-> red (negative), grey for neutral.
POS, NEG, NEU = "#2a78d6", "#e34948", "#8a8984"

st.set_page_config(page_title="Heat Pump Pulse", page_icon="🔥", layout="wide")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load():
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=30)
    cols = {r[1] for r in db.execute("PRAGMA table_info(posts)")}
    extra = ", ".join(c for c in ["clean_text", "exclude_reason", "link_title", "link_domain"] if c in cols)
    df = pd.read_sql_query(
        "SELECT seen_at, text, themes, country, sentiment_label, sentiment_score, analysed_at"
        + (f", {extra}" if extra else "") + " FROM posts", db)
    cursor = db.execute("SELECT value FROM state WHERE key='cursor'").fetchone()
    db.close()
    for c in ["clean_text", "exclude_reason", "link_title", "link_domain"]:
        if c not in df:
            df[c] = None
    df["time_utc"] = pd.to_datetime(df["seen_at"], utc=True)
    df["time"] = df["time_utc"].dt.tz_convert(LOCAL_TZ).dt.tz_localize(None)   # naive UK time
    df["themes"] = df["themes"].fillna("")
    df["country"] = df["country"].fillna("unknown")
    df["scored"] = df["sentiment_label"].isin(["positive", "neutral", "negative"])
    collector_at = datetime.fromtimestamp(int(cursor[0]) / 1e6, tz=timezone.utc) if cursor else None
    return df, collector_at, datetime.now(timezone.utc)


def fmt_period(start, hours):
    end = start + timedelta(hours=hours)
    if hours >= 24:
        return start.strftime("%a %d %b")
    return f"{start:%a %d %b %H:%M}–{end:%H:%M}"


def esc(text):
    """Show post text literally: escape characters that Markdown/LaTeX would interpret."""
    out = str(text)
    for ch in "\\`*_{}[]()#+-!$<>|~":
        out = out.replace(ch, "\\" + ch)
    return out


def mood_word(x):
    if pd.isna(x):
        return "–"
    return "negative" if x <= -0.15 else "positive" if x >= 0.15 else "mixed / neutral"


REFRESH_SECONDS = 120                # the page reloads its data by itself every 2 minutes


@st.fragment(run_every=REFRESH_SECONDS)
def page():
    if not DB_PATH.exists():
        st.error(f"No database found at {DB_PATH}. Start heatpump_collector.py first.")
        st.stop()

    df_all, collector_at, loaded_at = load()

    # ---------------------------------------------------------------------------
    # Header
    # ---------------------------------------------------------------------------
    st.title("Heat Pump Pulse")
    st.markdown("**How the UK public talks about heat pumps on Bluesky, and which concern needs attention first.** "
                "Built for a consumer advice team such as the Energy Saving Trust's.")

    st.warning(
        "**Read this first.** The score measures the *tone* of a post, not whether the author is for or against "
        "heat pumps. *\"Cutting heat pump grants is a disgrace\"* scores negative, but the author supports heat pumps. "
        "Always open the posts behind a dip before acting on it. Bluesky users are not a representative sample of "
        "UK households.", icon="⚠️")

    # Pipeline health
    if collector_at:
        lag = (loaded_at - collector_at).total_seconds() / 60
        waiting = int((df_all["analysed_at"].isna()).sum())
        health = (f"🟢 Collector live (read up to {collector_at.astimezone(ZoneInfo(LOCAL_TZ)).strftime('%H:%M')})" if lag < 15
                  else f"🟠 Collector {lag:.0f} min behind, check heatpump_collector.py")
        st.caption(f"{health} · {len(df_all):,} posts collected · {waiting} waiting for the model · "
                   f"refreshes every 2 min · last {loaded_at.astimezone(ZoneInfo(LOCAL_TZ)).strftime('%H:%M:%S')} (UK time)")

    # ---------------------------------------------------------------------------
    # Filters (one row)
    # ---------------------------------------------------------------------------
    f1, f2, f3, f4, f5 = st.columns([1.2, 1, 1.2, 1.4, 0.6], vertical_alignment="bottom")
    period = f1.selectbox("Time range", ["All collected data", "Last 7 days", "Last 48 hours"])
    bucket = f2.selectbox("Group per", ["6 hours", "day"])
    country = f3.selectbox("Country (rough guess)", ["All", "UK", "US", "Other / unknown"])
    theme = f4.selectbox("Theme", ["All themes"] + THEMES)
    if f5.button("↻ Refresh"):
        st.cache_data.clear()
        st.rerun()

    df = df_all.copy()
    if period != "All collected data":
        hours = 7 * 24 if period == "Last 7 days" else 48
        df = df[df["time_utc"] >= loaded_at - timedelta(hours=hours)]
    if country == "UK":
        df = df[df["country"].str.contains("UK")]
    elif country == "US":
        df = df[df["country"].str.contains("US")]
    elif country == "Other / unknown":
        df = df[~df["country"].str.contains("UK|US")]
    if theme != "All themes":
        df = df[df["themes"].str.contains(theme, regex=False)]

    scored = df[df["scored"]].copy()
    excluded = df[df["exclude_reason"].notna()]

    if scored.empty:
        st.info("No scored posts for this selection yet.")
        st.stop()

    # ---------------------------------------------------------------------------
    # Periods
    # ---------------------------------------------------------------------------
    hours = 6 if bucket == "6 hours" else 24
    freq = f"{hours}h"
    scored["period"] = scored["time"].dt.floor(freq)
    df["period"] = df["time"].dt.floor(freq)

    per = (scored.groupby("period")
           .agg(n=("sentiment_score", "size"), mood=("sentiment_score", "mean"),
                neg=("sentiment_label", lambda s: (s == "negative").mean()),
                pos=("sentiment_label", lambda s: (s == "positive").mean()))
           .reset_index())
    vol = df.groupby("period").size().rename("all_posts").reset_index()
    per = per.merge(vol, on="period", how="right").fillna({"n": 0}).sort_values("period")
    per["n"] = per["n"].astype(int)
    per["label"] = per["period"].apply(lambda p: fmt_period(p, hours))
    per["enough"] = per["n"] >= MIN_N
    per["note"] = per["enough"].map({True: "", False: "few posts: don't read too much into this point"})
    per["mood_txt"] = per["mood"].map(lambda x: "–" if pd.isna(x) else f"{x:+.2f}")
    per["neg_txt"] = per["neg"].map(lambda x: "–" if pd.isna(x) else f"{x:.0%}")
    per["pos_txt"] = per["pos"].map(lambda x: "–" if pd.isna(x) else f"{x:.0%}")

    # ---------------------------------------------------------------------------
    # Headline numbers
    # ---------------------------------------------------------------------------
    reliable = per[per["enough"]]
    dip = reliable.loc[reliable["mood"].idxmin()] if not reliable.empty else None
    k1, k2, k3, k4 = st.columns(4)
    avg = scored["sentiment_score"].mean()
    k1.metric("Posts analysed", f"{len(scored):,}")
    k1.caption(f"{len(excluded)} more excluded (bots, duplicates, too short)")
    k2.metric("Average tone", f"{avg:+.2f}", help="From −1 (all very negative) to +1 (all very positive).")
    k2.caption(mood_word(avg))
    k3.metric("Share negative", f"{(scored['sentiment_label'] == 'negative').mean():.0%}")
    k3.caption(f"positive {(scored['sentiment_label'] == 'positive').mean():.0%}")
    if dip is not None:
        k4.metric("Most negative period", dip["period"].strftime("%a %d %b"))
        k4.caption((f"{dip['period']:%H:%M}–{dip['period'] + timedelta(hours=hours):%H:%M} · " if hours < 24 else "")
                   + f"tone {dip['mood']:+.2f} · {dip['n']} posts")
    else:
        k4.metric("Most negative period", "–")

    # ---------------------------------------------------------------------------
    # Charts: tone over time + volume over time (two charts, one shared time axis)
    # ---------------------------------------------------------------------------
    st.subheader(f"Tone per {bucket}")
    st.caption("Each point is the average tone of the posts in that period. Hollow points have fewer than "
               f"{MIN_N} posts: treat them as noise. Hover a point for details.")

    x = alt.X("period:T", title=None, axis=alt.Axis(format="%a %d %b %H:%M" if hours == 6 else "%a %d %b", grid=False))
    tooltip = [alt.Tooltip("label:N", title="Period"), alt.Tooltip("n:Q", title="Posts analysed"),
               alt.Tooltip("mood_txt:N", title="Average tone"), alt.Tooltip("neg_txt:N", title="Negative"),
               alt.Tooltip("pos_txt:N", title="Positive"), alt.Tooltip("note:N", title=" ")]
    base = alt.Chart(per[per["n"] > 0])
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=NEU, strokeDash=[4, 4]).encode(y="y:Q")
    line = base.mark_line(color=NEU, strokeWidth=2).encode(
        x=x, y=alt.Y("mood:Q", title="Average tone (−1 to +1)", scale=alt.Scale(domain=[-1, 1]),
                     axis=alt.Axis()))
    color = alt.condition("datum.mood >= 0", alt.value(POS), alt.value(NEG))
    pts_full = base.transform_filter("datum.enough").mark_point(size=90, filled=True, strokeWidth=2).encode(
        x=x, y="mood:Q", color=color, tooltip=tooltip)
    pts_few = base.transform_filter("!datum.enough").mark_point(size=90, filled=False, strokeWidth=2).encode(
        x=x, y="mood:Q", color=color, tooltip=tooltip)
    st.altair_chart((zero + line + pts_full + pts_few).properties(height=300), width="stretch")

    st.caption(f"Number of posts per {bucket}: how much attention heat pumps get. A spike in attention usually "
               "follows a news story.")
    vol_chart = alt.Chart(per).mark_bar(color=POS, size=16 if hours == 6 else 40, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=x, y=alt.Y("all_posts:Q", title="Posts", axis=alt.Axis()),
        tooltip=[alt.Tooltip("label:N", title="Period"), alt.Tooltip("all_posts:Q", title="Posts collected"),
                 alt.Tooltip("n:Q", title="Posts analysed")])
    st.altair_chart(vol_chart.properties(height=140), width="stretch")

    # ---------------------------------------------------------------------------
    # Themes: which concern needs attention?
    # ---------------------------------------------------------------------------
    st.subheader("Which concern needs attention?")
    st.caption("Tone per theme in the selected time range, most negative first. A theme can be negative because "
               "people are worried about it *or* because they are angry on its behalf: open the posts to check.")
    rows = []
    for t in THEMES:
        s = scored[scored["themes"].str.contains(t, regex=False)]
        if len(s):
            rows.append({"theme": t, "n": len(s), "mood": s["sentiment_score"].mean(),
                         "neg": (s["sentiment_label"] == "negative").mean()})
    themes = pd.DataFrame(rows)
    if not themes.empty:
        themes["enough"] = themes["n"] >= THEME_MIN_N
        # Rank only themes with enough posts; themes with too few posts go to the bottom, greyed out.
        themes = themes.sort_values(["enough", "mood"], ascending=[False, True]).reset_index(drop=True)
        themes["name"] = themes.apply(lambda r: r["theme"] if r["enough"] else f"{r['theme']} (too few posts)", axis=1)
        themes["neg_txt"] = themes["neg"].map(lambda v: f"{v:.0%}")
        themes["bar_color"] = themes.apply(lambda r: NEU if not r["enough"] else POS if r["mood"] >= 0 else NEG, axis=1)
        order = themes["name"].tolist()
        y = alt.Y("name:N", sort=order, title=None, axis=alt.Axis(labelFontSize=13, labelLimit=260))
        bars = alt.Chart(themes).mark_bar(cornerRadius=4, height=18).encode(
            y=y, x=alt.X("mood:Q", title="Average tone (−1 to +1)", scale=alt.Scale(domain=[-1, 1]),
                         axis=alt.Axis()),
            color=alt.Color("bar_color:N", scale=None),
            opacity=alt.condition("datum.enough", alt.value(1), alt.value(0.5)),
            tooltip=[alt.Tooltip("theme:N", title="Theme"), alt.Tooltip("n:Q", title="Posts"),
                     alt.Tooltip("mood:Q", title="Average tone", format="+.2f"),
                     alt.Tooltip("neg_txt:N", title="Negative")])
        st.altair_chart((bars + alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=NEU).encode(x="x:Q"))
                        .properties(height=48 * len(themes)), width="stretch")
        st.dataframe(themes[["theme", "n", "mood", "neg_txt", "enough"]]
                     .rename(columns={"theme": "Theme", "n": "Posts", "mood": "Average tone", "neg_txt": "Negative",
                                      "enough": f"Ranked (≥ {THEME_MIN_N} posts)"}),
                     hide_index=True, column_config={"Average tone": st.column_config.NumberColumn(format="%+.2f")})
        st.caption(f"Themes with fewer than {THEME_MIN_N} posts are not ranked (grey): a few angry posts could put them "
                   "on top. Themes are found with keywords; some of those words are negative themselves (e.g. *scam*, "
                   "*lies* for myths, *loud* for noise), so those themes lean negative partly by construction.")

    # ---------------------------------------------------------------------------
    # The posts behind a peak or dip
    # ---------------------------------------------------------------------------
    st.subheader("Open the posts behind a period")
    choices = per[per["all_posts"] > 0].sort_values("period", ascending=False)
    keys = [p.isoformat() for p in choices["period"]]
    names = {k: f"{r.label} · {r.n} posts · tone {r.mood_txt}" + ("  ← most negative" if dip is not None and
             r.period == dip["period"] else "") for k, r in zip(keys, choices.itertuples())}
    default = keys.index(dip["period"].isoformat()) if dip is not None and dip["period"].isoformat() in keys else 0
    if st.session_state.get("period") not in keys:      # first visit, or the chosen period left the time range
        st.session_state.pop("period", None)
    pick = st.selectbox("Period", keys, index=default, format_func=lambda k: names[k], key="period")
    chosen = pd.Timestamp(pick)

    sel = df[df["period"] == chosen].sort_values("time")
    show = pd.DataFrame({
        "Time (UK)": sel["time"].dt.strftime("%a %H:%M"),
        "Tone": sel.apply(lambda r: r["sentiment_label"] if r["scored"] else f"excluded: {r['exclude_reason']}"
                          if pd.notna(r["exclude_reason"]) else "waiting", axis=1),
        "Score": sel["sentiment_score"],
        "Post (author's own words)": sel["clean_text"].fillna(sel["text"]),
        "Shared article": sel["link_title"].fillna(""),
        "Themes": sel["themes"].str.replace("|", ", ", regex=False),
        "Country": sel["country"].str.replace("|", ", ", regex=False),
    })
    view = st.radio("Show as", ["Full text", "Table"], horizontal=True, label_visibility="collapsed")
    if view == "Table":
        st.dataframe(show, hide_index=True, width="stretch",
                     column_config={"Score": st.column_config.NumberColumn(format="%+.2f"),
                                    "Post (author's own words)": st.column_config.TextColumn(width="large")})
    else:
        icon = {"positive": "🔵", "negative": "🔴", "neutral": "⚪"}
        for r in show.itertuples(index=False):
            tone, score = r[1], r[2]
            head = (f"{icon.get(tone, '⚫')} **{tone}** {score:+.2f}" if pd.notna(score) else f"⚫ *{tone}*")
            meta = " · ".join(x for x in [r[0] + " UK", r[5] or "", r[6] if r[6] != "unknown" else ""] if x)
            with st.container(border=True):
                st.markdown(head)
                st.caption(esc(meta))
                st.markdown(esc(r[3]) if r[3] else "*(no text of their own)*")
                if r[4]:
                    st.caption(f"Shared article: {esc(r[4])}")
    st.caption("No account names are stored or shown.")

    # ---------------------------------------------------------------------------
    # Method
    # ---------------------------------------------------------------------------
    with st.expander("How this works and what it cannot tell you"):
        reasons = df_all["exclude_reason"].value_counts()
        st.markdown(f"""
    - **Source:** English Bluesky posts that mention heat pumps in their own text or in a shared article,
      collected continuously from Bluesky's public stream. Known bot accounts are skipped.
    - **Model:** `cardiffnlp/twitter-roberta-base-sentiment-latest` (trained on ~124M tweets, English only),
      run on each post's own words. Score = P(positive) − P(negative).
    - **Excluded from the tone line:** automated sources ({reasons.get('automated_source', 0)}),
      duplicates ({reasons.get('duplicate', 0)}), posts with fewer than 3 words of their own ({reasons.get('too_short', 0)}).
    - **Country** is a rough keyword guess; most posts have no country.
    - **Not representative:** only people who post on Bluesky, in English. Households that never post online are missing.
    - **Tone is not opinion:** do not read a negative line as "people are against heat pumps".
    """)



page()