"""Fetchers. Each returns a list of dicts: id, source, kind, text, url, published_at (UTC ISO).

We deliberately keep no author names or handles (see README, ethics).
"""

import hashlib
import html
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests

import config

session = requests.Session()
session.headers["User-Agent"] = config.USER_AGENT


def _id(*parts):
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]


def _clean(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"@[\w.\-]+", "@user", text)          # drop handles of mentioned people
    return re.sub(r"\s+", " ", text).strip()[: config.MAX_CHARS]


def _iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def google_news(query):
    """Dutch Google News search, last `window`. Headlines only."""
    g = config.GOOGLE_NEWS
    resp = session.get(
        "https://news.google.com/rss/search",
        params={"q": f"{query} when:{g['window']}", "hl": g["hl"], "gl": g["gl"], "ceid": g["ceid"]},
        timeout=20,
    )
    resp.raise_for_status()
    items = []
    for e in feedparser.parse(resp.content).entries:
        title = _clean(e.title)
        outlet = e.get("source", {}).get("title", "")
        if outlet and title.endswith(" - " + outlet):
            title = title[: -len(outlet) - 3]
        items.append({
            "id": _id("gnews", title.lower()),       # same headline via two queries = one item
            "source": f"Google News ({outlet})" if outlet else "Google News",
            "kind": "news",
            "text": title,
            "url": e.link,
            "published_at": _iso(parsedate_to_datetime(e.published)),
        })
    return items


def bluesky(query):
    """Public Bluesky search, Dutch posts only. No account needed."""
    resp = session.get(
        "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts",
        params={"q": query, "lang": config.BLUESKY_LANG, "sort": "latest", "limit": config.BLUESKY_LIMIT},
        timeout=20,
    )
    resp.raise_for_status()
    items = []
    for p in resp.json().get("posts", []):
        created = datetime.fromisoformat(p["record"]["createdAt"].replace("Z", "+00:00"))
        items.append({
            "id": _id("bsky", p["uri"]),
            "source": "Bluesky",
            "kind": "public",
            "text": _clean(p["record"].get("text", "")),
            "url": None,                              # post URLs contain the author's handle
            "published_at": _iso(created),
        })
    return items


def rss(name, url):
    """A plain news RSS feed. All items are returned; topic filtering happens later."""
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    items = []
    for e in feedparser.parse(resp.content).entries:
        when = e.get("published_parsed") or e.get("updated_parsed")
        published = datetime.fromtimestamp(time.mktime(when), timezone.utc) if when else datetime.now(timezone.utc)
        items.append({
            "id": _id("rss", e.link),
            "source": name,
            "kind": "news",
            "text": _clean(f"{e.title}. {e.get('summary', '')}"),
            "url": e.link,
            "published_at": _iso(published),
        })
    return items
