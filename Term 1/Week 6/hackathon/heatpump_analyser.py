#!/usr/bin/env python3
"""
Heat Pump Pulse: sentiment analysis step (Hackathon 6, step 2 of the pipeline)

Runs next to heatpump_collector.py and works on the same database (heatpump.db).
Every few minutes it picks up all posts that have not been analysed yet and either
  - scores the sentiment of the author's OWN words with a pre-trained Hugging Face transformer, or
  - marks the post as excluded, with the reason, so it does not count in the sentiment line.

Model: cardiffnlp/twitter-roberta-base-sentiment-latest
  RoBERTa-base trained on ~124M tweets (Jan 2018 - Dec 2021), fine-tuned for sentiment on TweetEval.
  English only. Labels: negative / neutral / positive. Licence: CC BY 4.0.
  https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest

What it writes per post (columns in the posts table)
  clean_text       the author's own words, with links removed (this is what the model reads)
  exclude_reason   empty if scored; otherwise automated_source / duplicate / too_short
  sentiment_label  negative / neutral / positive (empty if excluded)
  sentiment_score  P(positive) - P(negative), from -1 (very negative) to +1 (very positive)
  sentiment_model  name of the model used
  analysed_at      when this step processed the post (UTC)

Exclusion rules (the same rules used to draw the 50-post test sample)
  automated_source  shared link from a site that posts automatically (AUTOMATED_DOMAINS below)
  too_short         fewer than 3 words of the author's own (e.g. a bare link share)
  duplicate         the same cleaned text as an earlier post that was scored

Run (Linux, from the project folder)
  venv/bin/pip install transformers                                         (once)
  venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   (once, CPU-only torch)
  nohup venv/bin/python heatpump_analyser.py >> analyser.log 2>&1 &     # keep running, check every 5 min
  venv/bin/python heatpump_analyser.py --once                             # one pass, then stop
  venv/bin/python heatpump_analyser.py --interval 900                     # check every 15 min instead
The collector keeps running separately; both can use the database at the same time.
"""

import argparse
import re
import sqlite3
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().with_name("heatpump.db")
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Sites whose posts are generated automatically (checked by hand in the collected data).
AUTOMATED_DOMAINS = {"marketresearchfuture.com", "dlvr.it", "citizenportal.ai"}
MIN_WORDS = 3
BATCH = 16

NEW_COLUMNS = {"clean_text": "TEXT", "exclude_reason": "TEXT"}

URL = re.compile(r"https?://\S+")
BARE_LINK = re.compile(r"\b[\w.-]+\.[a-z]{2,}/\S*")   # shortened links Bluesky puts in the text, e.g. site.com/article-...
MENTION = re.compile(r"@[\w.\-]+")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] {msg}", flush=True)


def clean(text):
    """The author's own words: links removed, whitespace tidied."""
    t = URL.sub(" ", text or "")
    t = BARE_LINK.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def word_count(text):
    return len(re.findall(r"[A-Za-z]+", text))


def model_input(text):
    """Replace @mentions with '@user', as the cardiffnlp model card recommends."""
    return MENTION.sub("@user", text)


class Scorer:
    def __init__(self, name=MODEL):
        from transformers import pipeline
        log(f"Loading model {name} ...")
        self.name = name
        self.pipe = pipeline("text-classification", model=name, top_k=None, truncation=True, max_length=512)
        log("Model loaded.")

    def score(self, texts):
        out = self.pipe(texts, batch_size=8)
        results = []
        for dist in out:
            p = {d["label"].lower(): float(d["score"]) for d in dist}
            label = max(("negative", "neutral", "positive"), key=lambda k: p.get(k, 0.0))
            results.append((label, round(p.get("positive", 0.0) - p.get("negative", 0.0), 4)))
        return results


def connect(path=DB_PATH):
    if not path.exists():
        sys.exit(f"No database at {path}. Start heatpump_collector.py first.")
    db = sqlite3.connect(path, timeout=60)
    db.execute("PRAGMA journal_mode=WAL")
    existing = {row[1] for row in db.execute("PRAGMA table_info(posts)")}
    for name, kind in NEW_COLUMNS.items():
        if name not in existing:
            db.execute(f"ALTER TABLE posts ADD COLUMN {name} {kind}")
    db.execute("CREATE INDEX IF NOT EXISTS idx_posts_analysed ON posts(analysed_at)")
    db.commit()
    return db


def is_duplicate(db, pid, key):
    """True if an earlier post with the same cleaned text was already scored."""
    row = db.execute("SELECT 1 FROM posts WHERE id < ? AND exclude_reason IS NULL AND sentiment_label IS NOT NULL "
                     "AND lower(clean_text) = ? LIMIT 1", (pid, key)).fetchone()
    return row is not None


def process_batch(db, scorer):
    """Analyse up to BATCH unprocessed posts, oldest first. Returns a Counter of what happened."""
    rows = db.execute("SELECT id, text, link_domain FROM posts WHERE analysed_at IS NULL "
                      "ORDER BY id LIMIT ?", (BATCH,)).fetchall()
    done = Counter()
    if not rows:
        return done
    db.commit()   # make sure no write transaction is open while the (slow) model runs
    stamp = now()
    excluded, to_score, seen_in_batch = [], [], set()
    for pid, text, domain in rows:
        own = clean(text)
        key = own.lower()
        reason = None
        if (domain or "") in AUTOMATED_DOMAINS:
            reason = "automated_source"
        elif word_count(own) < MIN_WORDS:
            reason = "too_short"
        elif key in seen_in_batch or is_duplicate(db, pid, key):
            reason = "duplicate"
        if reason:
            excluded.append((own, reason, stamp, pid))
            done[reason] += 1
        else:
            seen_in_batch.add(key)
            to_score.append((pid, own))

    # 1. Run the model first, without holding any lock on the database.
    results = scorer.score([model_input(t) for _, t in to_score]) if to_score else []

    # 2. Then write everything in one short transaction, so the collector is never blocked for long.
    with db:
        db.executemany("UPDATE posts SET clean_text=?, exclude_reason=?, sentiment_label=NULL, sentiment_score=NULL, "
                       "sentiment_model=NULL, analysed_at=? WHERE id=?", excluded)
        for (pid, own), (label, score) in zip(to_score, results):
            db.execute("UPDATE posts SET clean_text=?, exclude_reason=NULL, sentiment_label=?, sentiment_score=?, "
                       "sentiment_model=?, analysed_at=? WHERE id=?", (own, label, score, scorer.name, stamp, pid))
            done[label] += 1
    return done


def run_pass(db, scorer):
    """Process everything that is waiting. Returns a Counter for this pass."""
    total = Counter()
    while True:
        try:
            done = process_batch(db, scorer)
        except sqlite3.OperationalError as exc:      # e.g. "database is locked": wait and try again
            log(f"database busy ({exc}); retrying in 10s")
            db.rollback()
            time.sleep(10)
            continue
        if not done:
            return total
        total.update(done)


def summary(db):
    rows = db.execute("SELECT COALESCE(exclude_reason, sentiment_label, 'waiting'), COUNT(*) FROM posts GROUP BY 1")
    c = Counter(dict(rows))
    scored = c["positive"] + c["neutral"] + c["negative"]
    return (f"database: {scored} scored (positive {c['positive']}, neutral {c['neutral']}, negative {c['negative']}) | "
            f"excluded: automated {c['automated_source']}, too short {c['too_short']}, duplicate {c['duplicate']} | "
            f"waiting {c['waiting']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--interval", type=int, default=300, help="seconds between checks (default 300 = 5 minutes)")
    ap.add_argument("--once", action="store_true", help="analyse what is waiting, then stop")
    args = ap.parse_args()

    db = connect()
    try:
        scorer = Scorer()
    except ImportError:
        sys.exit("Install the model libraries first:\n"
                 "  venv/bin/pip install transformers\n"
                 "  venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu")
    log(f"Heat Pump Pulse analyser. Database: {DB_PATH.name}. " +
        ("One pass." if args.once else f"Checking every {args.interval // 60} min. Ctrl+C to stop."))
    try:
        while True:
            done = run_pass(db, scorer)
            if done:
                log(f"analysed {sum(done.values())} new posts: " +
                    ", ".join(f"{k} {v}" for k, v in sorted(done.items())) + f" | {summary(db)}")
            if args.once:
                if not done:
                    log(f"nothing waiting | {summary(db)}")
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
        log("Stopped.")


if __name__ == "__main__":
    main()