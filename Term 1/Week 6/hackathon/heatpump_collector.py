#!/usr/bin/env python3
"""
Heat Pump Pulse: continuous Bluesky collector (Hackathon 6, step 1 of the pipeline)

Runs non-stop and stores every English Bluesky post about heat pumps in a local SQLite
database (heatpump.db), tagged with themes, a country hint and a first-hand flag.
The sentiment columns are left empty; the analysis step fills them in later.

What it does
  - listens to Bluesky's public Jetstream (open real-time stream; no account, key or quota)
  - keeps posts that mention heat pumps in their own text OR in a shared link card
    (e.g. people sharing a news article with a short comment); EV "car heat pump" posts are skipped
  - skips known aggregator bots, so reposting bots cannot move the sentiment line later
  - stores the author's OWN words in `text` and the headline of a shared article separately
    in `link_title` (the newspaper's tone, not the author's)
  - resumes from the last post it saw after a restart or a dropped connection (no gaps, no duplicates)
  - removes a stored post when its author deletes it on Bluesky
  - never stores account names or IDs: each post is identified only by a salted hash

Run
  python -m pip install websockets
  python heatpump_collector.py                     # start (first run also replays the last 12 hours)
  python heatpump_collector.py --replay-from 2026-10-12T22:00
                                                   # re-read from this UTC time (duplicates are ignored;
                                                   # only works if Jetstream still holds that window)
  python heatpump_collector.py --status            # show what is in the database, without collecting
  python heatpump_collector.py --export posts.csv  # export the stored posts (text, time, tags; no IDs)
  Stop with Ctrl+C; the next start continues where it stopped.
  Every 5 minutes it prints an "alive" line: how far it has read, how many posts it scanned and matched.

Keep the computer awake while it runs. Jetstream only keeps a limited replay window,
so a long sleep can leave a gap; --status shows posts per hour so gaps are visible.
"""

import argparse
import asyncio
import csv
import hashlib
import json
import re
import secrets
import sqlite3
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

DB_PATH = Path(__file__).resolve().with_name("heatpump.db")

ENDPOINTS = [
    "wss://jetstream2.us-east.bsky.network/subscribe",
    "wss://jetstream1.us-east.bsky.network/subscribe",
    "wss://jetstream1.us-west.bsky.network/subscribe",
    "wss://jetstream2.us-west.bsky.network/subscribe",
]
COLLECTION = "app.bsky.feed.post"

# Aggregator / repost bots. Add a handle here when you find another one in your data.
BOT_HANDLES = ["link.skysquare.app"]
AGGREGATOR_TEXT = re.compile(r"^\s*#\d+\s*[·.\-]\s*shared by \d+ accounts", re.I)

# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------
HEAT_PUMP = re.compile(r"heat[ -]?pumps?|air[- ]source|ground[- ]source|\bashps?\b|\bgshps?\b", re.I)

CAR_HEAT_PUMP = re.compile(
    r"heat[ -]?pump (?:car|in (?:my|the|a|your) (?:car|tesla|ev))"
    r"|(?:\bev|\bcar|tesla|model [3y]|ioniq|\bid\.?[347])['’]?s? (?:has a |with a |)heat[ -]?pump", re.I)

THEMES = {
    "cost/grants": r"\bbills?\b|\bcosts?\b|price|expensive|cheap|afford|grant|subsid|boiler upgrade scheme|\bbus\b grant"
                   r"|£\s?7,?500|running costs?|electricity (?:price|cost)|gas (?:price|cost)|tariff",
    "performance/cold": r"\bcold\b|winter|freez|warm|efficien|\bcop\b|radiators?|insulat|underfloor|draughty|old houses?",
    "noise": r"\bnois(?:e|y)\b|\bloud\b|\bhum(?:ming)?\b|decibel",
    "installers": r"install(?:er|ers|ation|ed|ing)?|cowboy|engineer|plumber|fitted|quote",
    "politics/policy": r"reform uk|farage|net zero|miliband|labou?r|tor(?:y|ies)|conservative|government|minister"
                       r"|\bban(?:ned|s)?\b|mandate|gas boiler|trump|republican|democrat|\bmps?\b|defen[cs]e spending",
    "myths/misinformation": r"\bmyths?\b|misinformation|disinformation|don'?t work|doesn'?t work|scam|lies|propaganda",
}
THEMES = {k: re.compile(v, re.I) for k, v in THEMES.items()}

COUNTRIES = {
    "UK": r"\buk\b|britain|british|england|scotland|scottish|wales|welsh|northern ireland|ofgem|boiler upgrade"
          r"|\bbus\b (?:grant|scheme)|£|\bmps?\b|westminster|miliband|reform uk|farage|octopus|nesta"
          r"|energy saving trust|\bdesnz\b|council tax|ministers?|chancellor|combi(?: boiler)?|three-bed|semi-detached"
          r"|\bsemi\b|terraced|\bnhs\b|as a nation",
    "US": r"(?-i:\bUSA?\b|\bU\.S\.)|america|inflation reduction act|\bira\b|fahrenheit|°f|\$|propane|furnace",
    "Ireland": r"ireland|irish|\bseai\b",
    "Germany": r"germany|german|heizungsgesetz",
    "Netherlands": r"netherlands|dutch",
    "Canada": r"canada|canadian|ontario|quebec|alberta|nova scotia",
    "Australia/NZ": r"australia|aussie|new zealand",
}
COUNTRIES = {k: re.compile(v, re.I) for k, v in COUNTRIES.items()}

# Domains that give a strong country hint when a news link is shared
COUNTRY_DOMAINS = {
    "theguardian.com": "UK", "bbc.co.uk": "UK", "bbc.com": "UK", "telegraph.co.uk": "UK", "thetimes.co.uk": "UK",
    "independent.co.uk": "UK", "inews.co.uk": "UK", "dailymail.co.uk": "UK", "ft.com": "UK", "gov.uk": "UK",
    "nytimes.com": "US", "washingtonpost.com": "US", "cnn.com": "US", "npr.org": "US",
    "rte.ie": "Ireland", "irishtimes.com": "Ireland", "cbc.ca": "Canada", "abc.net.au": "Australia/NZ",
}

FIRST_HAND = re.compile(
    r"\b(?:my|our) (?:new )?(?:(?:air|ground)[- ]source )?(?:heat[ -]?pump|ashp|gshp|installer|bills?|radiators?)\b"
    r"|\bquoted (?:me|us)\b|\bin (?:my|our) (?:house|home|flat)\b"
    r"|\bwe (?:just )?(?:got|installed|have|had|put in|switched)\b|\bi (?:just )?(?:got|installed|have|had|switched)\b"
    r"|\bsince (?:we|i) (?:got|installed)\b", re.I)


def link_card(record):
    """Return (title, description, domain) of a shared link card, or empty strings."""
    embed = record.get("embed") or {}
    ext = embed.get("external")
    if not ext and isinstance(embed.get("media"), dict):   # link card combined with a quote post
        ext = embed["media"].get("external")
    if not isinstance(ext, dict):
        return "", "", ""
    uri = ext.get("uri") or ""
    domain = re.sub(r"^www\.", "", urlparse(uri).netloc.lower()) if uri else ""
    return (ext.get("title") or "").strip(), (ext.get("description") or "").strip(), domain


def classify(own, title, desc, domain):
    """Return tags for a heat-pump post, or None if it is not about home heat pumps."""
    link = f"{title}\n{desc}"
    in_text, in_link = bool(HEAT_PUMP.search(own)), bool(HEAT_PUMP.search(link))
    combined = f"{own}\n{link}"
    if not (in_text or in_link) or CAR_HEAT_PUMP.search(combined):
        return None
    themes = [k for k, r in THEMES.items() if r.search(combined)]
    countries = [k for k, r in COUNTRIES.items() if r.search(combined)]
    if domain in COUNTRY_DOMAINS and COUNTRY_DOMAINS[domain] not in countries:
        countries.append(COUNTRY_DOMAINS[domain])
    return {
        "themes": "|".join(themes),
        "country": "|".join(countries or ["unknown"]),
        "first_hand": int(bool(FIRST_HAND.search(own))),        # only the author's own words count
        "matched_in": "both" if in_text and in_link else ("text" if in_text else "link"),
    }


def is_english(record):
    """English posts, plus posts without a language tag (common for link-only shares)."""
    langs = [l.split("-")[0].lower() for l in (record.get("langs") or [])]
    return not langs or "en" in langs


def resolve_bot_dids():
    dids = set()
    for handle in BOT_HANDLES:
        url = f"https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle?handle={handle}"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                dids.add(json.load(r)["did"])
        except Exception as exc:
            print(f"Warning: could not look up bot account {handle} ({exc.__class__.__name__}); "
                  f"its posts are still caught by the text pattern.")
    return dids


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    post_hash       TEXT UNIQUE NOT NULL,   -- salted hash of the post's ID; no account names are stored
    created_at      TEXT,                   -- time the author says they posted (UTC, ISO 8601)
    seen_at         TEXT NOT NULL,          -- time Bluesky's stream delivered it (UTC, ISO 8601)
    text            TEXT NOT NULL,          -- the author's own words (may be empty for a bare link share)
    themes          TEXT,                   -- e.g. "cost/grants|politics/policy"
    country         TEXT,                   -- rough keyword hint, e.g. "UK" or "unknown"
    first_hand      INTEGER,                -- 1 if it reads like personal experience (rough)
    sentiment_label TEXT,                   -- filled in by the analysis step
    sentiment_score REAL,                   
    sentiment_model TEXT,
    analysed_at     TEXT
);
CREATE INDEX IF NOT EXISTS idx_posts_seen ON posts(seen_at);
CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT);
"""

# Columns added in this version; older databases are upgraded automatically.
NEW_COLUMNS = {
    "link_title": "TEXT",     # headline of a shared article (the newspaper's words, not the author's)
    "link_desc": "TEXT",
    "link_domain": "TEXT",    # e.g. theguardian.com
    "matched_in": "TEXT",     # text / link / both: where "heat pump" was found
}


def columns(db):
    return {row[1] for row in db.execute("PRAGMA table_info(posts)")}


class ReadOnly:
    """Opens the database read-only, so --status can run while the collector is writing."""
    def __init__(self, path=DB_PATH):
        self.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=30)

    def count(self):
        return self.db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]

    def get(self, key, default=None):
        row = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def close(self):
        self.db.close()


class Store:
    def __init__(self, path=DB_PATH):
        self.db = sqlite3.connect(path, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")  # readers (e.g. --status) never block the collector
        self.db.executescript(SCHEMA)
        existing = columns(self.db)
        for name, kind in NEW_COLUMNS.items():
            if name not in existing:
                self.db.execute(f"ALTER TABLE posts ADD COLUMN {name} {kind}")
        # posts stored by the old version were only ever matched on their own text
        self.db.execute("UPDATE posts SET matched_in='text' WHERE matched_in IS NULL")
        self.salt = self.get("salt")
        if not self.salt:
            self.salt = secrets.token_hex(16)  # local secret: makes the hashes impossible to look up
            self.set("salt", self.salt)
        self.db.commit()

    def get(self, key, default=None):
        row = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set(self, key, value):
        self.db.execute("INSERT INTO state(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, str(value)))

    def post_hash(self, did, rkey):
        return hashlib.sha256(f"{self.salt}:{did}/{rkey}".encode()).hexdigest()

    def add(self, h, created_at, seen_at, text, tags, title, desc, domain):
        cur = self.db.execute(
            "INSERT OR IGNORE INTO posts(post_hash, created_at, seen_at, text, themes, country, first_hand, "
            "link_title, link_desc, link_domain, matched_in) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (h, created_at, seen_at, text, tags["themes"], tags["country"], tags["first_hand"],
             title, desc, domain, tags["matched_in"]))
        return cur.rowcount == 1

    def delete(self, h):
        return self.db.execute("DELETE FROM posts WHERE post_hash=?", (h,)).rowcount

    def count(self):
        return self.db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]

    def commit(self):
        try:
            self.db.commit()
            return True
        except sqlite3.OperationalError as exc:  # e.g. "database is locked": try again at the next checkpoint
            print(f"  database busy ({exc}); will retry")
            return False

    def close(self):
        self.db.commit()
        self.db.close()


# ---------------------------------------------------------------------------
# Collector
# ---------------------------------------------------------------------------
class Collector:
    def __init__(self, store, bot_dids):
        self.store = store
        self.bot_dids = bot_dids
        self.cursor = int(store.get("cursor", 0) or 0)
        self.read = self.kept = self.removed = 0
        self.bots_skipped = int(store.get("bots_skipped", 0) or 0)
        self.kept_this_hour = 0
        self.scanned_5min = self.matched_5min = 0
        self.last_save = time.time()
        self.last_status = time.time()
        self.last_heartbeat = time.time()

    def handle(self, raw):
        try:
            ev = json.loads(raw)
        except (ValueError, TypeError):
            return
        ts = ev.get("time_us")
        if ts:
            self.cursor = ts
        if ev.get("kind") != "commit":
            return
        c = ev.get("commit") or {}
        if c.get("collection") != COLLECTION:
            return
        did, rkey, op = ev.get("did"), c.get("rkey"), c.get("operation")
        if not did or not rkey:
            return
        if op == "delete":
            self.removed += self.store.delete(self.store.post_hash(did, rkey))
            return
        if op != "create":
            return
        self.read += 1
        self.scanned_5min += 1
        record = c.get("record") or {}
        if not is_english(record):
            return
        text = (record.get("text") or "").strip()
        title, desc, domain = link_card(record)
        tags = classify(text, title, desc, domain)
        if not tags:
            return
        self.matched_5min += 1
        if did in self.bot_dids or AGGREGATOR_TEXT.match(text):
            self.bots_skipped += 1
            return
        seen = datetime.fromtimestamp(ts / 1e6, tz=timezone.utc).isoformat(timespec="seconds") if ts \
            else datetime.now(timezone.utc).isoformat(timespec="seconds")
        if self.store.add(self.store.post_hash(did, rkey), record.get("createdAt"), seen, text, tags,
                          title, desc, domain):
            self.kept += 1
            self.kept_this_hour += 1

    def checkpoint(self, force=False):
        now = time.time()
        if force or now - self.last_save >= 10:
            if self.cursor:
                self.store.set("cursor", self.cursor)
            self.store.set("bots_skipped", self.bots_skipped)
            self.store.commit()
            self.last_save = now
        if now - self.last_heartbeat >= 300:
            self.last_heartbeat = now
            pos = datetime.fromtimestamp(self.cursor / 1e6, tz=timezone.utc) if self.cursor else None
            behind = (now - self.cursor / 1e6) / 60 if self.cursor else 0
            where = f"reading posts from {pos:%Y-%m-%d %H:%M} UTC" if pos else "waiting for posts"
            lag = "live" if behind < 5 else f"{behind:.0f} min behind live, catching up"
            print(f"[{datetime.now():%H:%M}] alive: {where} ({lag}) | last 5 min: {self.scanned_5min:,} posts "
                  f"scanned, {self.matched_5min} heat-pump matches | {self.store.count()} stored")
            self.scanned_5min = self.matched_5min = 0
        if force or now - self.last_status >= 3600:
            behind = (time.time() - self.cursor / 1e6) / 60 if self.cursor else 0
            print(f"[{datetime.now():%Y-%m-%d %H:%M}] stored {self.kept_this_hour} new posts this hour | "
                  f"{self.store.count()} in database | {self.read:,} posts scanned since start | "
                  f"{self.removed} removed after deletion | {self.bots_skipped} bot posts skipped in total"
                  + (f" | catching up, {behind:.0f} min behind" if behind > 5 else ""))
            self.kept_this_hour = 0
            self.last_status = now


async def stream(collector, rewind_hours):
    import websockets  # imported here so --status/--export work without it

    if collector.cursor:
        start = collector.cursor
        print(f"Resuming from {datetime.fromtimestamp(start / 1e6, tz=timezone.utc):%Y-%m-%d %H:%M} UTC.")
    else:
        start = int((time.time() - rewind_hours * 3600) * 1e6)
        print(f"First run: replaying the last {rewind_hours:g} hours, then continuing live.")
    attempt = 0
    while True:
        url = ENDPOINTS[attempt % len(ENDPOINTS)]
        cursor = collector.cursor or start
        full = f"{url}?wantedCollections={COLLECTION}&cursor={cursor}"
        try:
            async with websockets.connect(full, max_size=2**22, open_timeout=15, ping_interval=20) as ws:
                pos = datetime.fromtimestamp(cursor / 1e6, tz=timezone.utc)
                print(f"Connected to {url.split('/subscribe')[0].replace('wss://', '')}, "
                      f"continuing from {pos:%Y-%m-%d %H:%M} UTC")
                attempt = 0
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=45)  # silence = stalled connection
                    collector.handle(msg)
                    collector.checkpoint()
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException) as exc:
            collector.checkpoint(force=False)
            name = "NoDataFor45Seconds" if isinstance(exc, asyncio.TimeoutError) else exc.__class__.__name__
            attempt += 1
            wait = min(60, 3 * attempt)
            print(f"Connection problem ({name}); retrying in {wait}s on another server...")
            await asyncio.sleep(wait)


# ---------------------------------------------------------------------------
# --status and --export
# ---------------------------------------------------------------------------
def show_status(store):
    db = store.db
    cols = columns(db)
    upgraded = "matched_in" in cols
    n = store.count()
    print(f"Database: {DB_PATH}\nPosts stored: {n}")
    cur = store.get("cursor")
    if cur:
        pos = datetime.fromtimestamp(int(cur) / 1e6, tz=timezone.utc)
        behind = (time.time() - int(cur) / 1e6) / 60
        state = "up to date" if behind < 10 else f"{behind:.0f} min behind: is the collector running?"
        print(f"Collector position: {pos:%Y-%m-%d %H:%M} UTC ({state})")
    print(f"Bot posts skipped: {store.get('bots_skipped', 0)}")
    if not upgraded:
        print("(Old database format: start the collector once to upgrade it and see the new sections.)")
    if not n:
        return
    first, last = db.execute("SELECT MIN(seen_at), MAX(seen_at) FROM posts").fetchone()
    print(f"From {first} to {last} (UTC)")
    fh = db.execute("SELECT SUM(first_hand) FROM posts").fetchone()[0] or 0
    print(f"First-hand (rough): {fh} ({fh / n:.0%})")

    analysed = db.execute("SELECT COUNT(*) FROM posts WHERE sentiment_label IS NOT NULL").fetchone()[0]
    print(f"With sentiment: {analysed}")
    if upgraded:
        m = Counter(dict(db.execute("SELECT matched_in, COUNT(*) FROM posts GROUP BY 1")))
        print(f"Matched in: own text {m['text']} | link card only {m['link']} | both {m['both']}")
        doms = db.execute("SELECT link_domain, COUNT(*) FROM posts WHERE link_domain <> '' "
                          "GROUP BY 1 ORDER BY 2 DESC LIMIT 5").fetchall()
        if doms:
            print("Most shared sites: " + ", ".join(f"{d} {k}" for d, k in doms))

    print("\nPosts per day (UTC):")
    for day, k in db.execute("SELECT substr(seen_at,1,10) d, COUNT(*) FROM posts GROUP BY d ORDER BY d"):
        print(f"  {day}  {k:5}  " + "#" * min(60, k // 5 + 1))

    themes, countries = Counter(), Counter()
    for t, c in db.execute("SELECT themes, country FROM posts"):
        themes.update(x for x in (t or "").split("|") if x)
        countries.update(x for x in (c or "unknown").split("|") if x)
    print("\nThemes:   " + ", ".join(f"{k} {v}" for k, v in themes.most_common()))
    print("Countries: " + ", ".join(f"{k} {v}" for k, v in countries.most_common()))

    print("\nLast 24 hours, posts per hour (UTC; 0 = collector was off or stream was quiet):")
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(hours=23)
    per_hour = dict(db.execute("SELECT substr(seen_at,1,13), COUNT(*) FROM posts WHERE seen_at >= ? GROUP BY 1",
                               (start.isoformat(timespec="seconds"),)).fetchall())
    for i in range(24):
        h = start + timedelta(hours=i)
        k = per_hour.get(h.strftime("%Y-%m-%dT%H"), 0)
        print(f"  {h:%Y-%m-%d %H}:00  {k:4}  " + "#" * min(60, k))


def export_csv(store, path):
    rows = store.db.execute("SELECT created_at, seen_at, text, link_title, link_domain, matched_in, themes, country, "
                            "first_hand, sentiment_label, sentiment_score, sentiment_model "
                            "FROM posts ORDER BY seen_at").fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["created_at", "seen_at", "text", "link_title", "link_domain", "matched_in", "themes", "country",
                    "first_hand", "sentiment_label", "sentiment_score", "sentiment_model"])
        w.writerows(rows)
    print(f"Exported {len(rows)} posts to {path} (no account names or post IDs).")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rewind-hours", type=float, default=12,
                    help="first run only: how many hours back to start (default 12)")
    ap.add_argument("--replay-from", metavar="UTC_TIME",
                    help="re-read the stream from this UTC time, e.g. 2026-10-12T22:00 (duplicates are ignored)")
    ap.add_argument("--status", action="store_true", help="show what is in the database and exit")
    ap.add_argument("--export", metavar="FILE.csv", help="export stored posts to CSV and exit")
    args = ap.parse_args()

    if args.status:
        if not DB_PATH.exists():
            sys.exit("No database yet. Start the collector first.")
        ro = ReadOnly()
        show_status(ro)
        ro.close()
        return
    store = Store()
    if args.export:
        export_csv(store, args.export)
        store.close()
        return

    try:
        import websockets  # noqa: F401
    except ImportError:
        sys.exit("Install the websocket library first:  python -m pip install websockets")

    if args.replay_from:
        try:
            t = datetime.fromisoformat(args.replay_from)
        except ValueError:
            sys.exit("Use a time like 2026-10-12T22:00 (UTC).")
        t = t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t
        store.set("cursor", int(t.timestamp() * 1e6))
        store.commit()
        print(f"Replaying from {t:%Y-%m-%d %H:%M} UTC; posts already stored are skipped.")

    collector = Collector(store, resolve_bot_dids())
    print(f"Heat Pump Pulse collector. Database: {DB_PATH.name} ({store.count()} posts so far). Ctrl+C to stop.")
    try:
        asyncio.run(stream(collector, args.rewind_hours))
    except KeyboardInterrupt:
        pass
    finally:
        collector.checkpoint(force=True)
        store.close()
        print("Stopped. Run the same command again to continue where it left off.")


if __name__ == "__main__":
    main()