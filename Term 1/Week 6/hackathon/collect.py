"""One collection round: fetch all sources -> keep on-topic items -> score new ones -> store.

Run once:            .venv/bin/python collect.py
Runs automatically:  every hour via GitHub Actions (.github/workflows/green-pulse.yml).

Storage is two CSV files (append-only), so git only stores the new lines each round:
  data/items.csv  one row per item, with both models' scores
  data/runs.csv   one row per collection round (proof that it ran on its own)
"""

import csv
import logging
import time
from datetime import datetime, timezone

import config
import sources

config.DATA_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=config.LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("collect")

ITEM_FIELDS = [
    "id", "source", "kind",           # kind: news | public
    "lines",                          # comma-separated, an item can belong to several lines
    "text", "url",
    "published_at",                   # when it was written (UTC)
    "collected_at",                   # when our collector found it (UTC)
    "main_label", "main_pos", "main_neu", "main_neg",
    "main_mood",                      # P(positive) - P(negative), from -1 to +1
    "cmp_label", "cmp_mood",
]
RUN_FIELDS = ["started_at", "where", "fetched", "new_items", "errors"]


def match_lines(text):
    t = text.lower()
    found = []
    for name, line in config.LINES.items():
        if any(m in t for m in line["match"]):
            if name == "Stroomnet" and not any(c in t for c in config.GRID_CONTEXT):
                continue
            found.append(name)
    return found


def fetch_all():
    items, errors = [], []
    jobs = []
    for line in config.LINES.values():
        for q in line["search"]:
            jobs.append((f"gnews:{q}", sources.google_news, (q,)))
            jobs.append((f"bsky:{q}", sources.bluesky, (q,)))
    for name, url in config.RSS_FEEDS.items():
        jobs.append((f"rss:{name}", sources.rss, (name, url)))

    for label, fn, args in jobs:
        try:
            items.extend(fn(*args))
        except Exception as e:  # one broken source must not stop the round
            errors.append(f"{label}: {e}")
        time.sleep(1)  # be polite to the APIs
    return items, errors


def known_ids():
    if not config.ITEMS_CSV.exists():
        return set()
    with open(config.ITEMS_CSV, newline="", encoding="utf-8") as f:
        return {row["id"] for row in csv.DictReader(f)}


def append(path, fields, rows):
    new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new_file:
            w.writeheader()
        w.writerows(rows)


def main():
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fetched, errors = fetch_all()
    known = known_ids()

    new = {}
    for it in fetched:
        if it["id"] in known or it["id"] in new or len(it["text"]) < 15:
            continue
        lines = match_lines(it["text"])
        if lines:
            it["lines"] = ",".join(lines)
            new[it["id"]] = it
    new = list(new.values())

    if new:
        from sentiment import score  # import late: load the models only when needed
        for it, s in zip(new, score([it["text"] for it in new])):
            it["collected_at"] = started
            it.update({k: round(v, 4) if isinstance(v, float) else v for k, v in s.items()})
        append(config.ITEMS_CSV, ITEM_FIELDS, new)

    append(config.RUNS_CSV, RUN_FIELDS, [{
        "started_at": started, "where": config.RUN_LOCATION,
        "fetched": len(fetched), "new_items": len(new), "errors": " | ".join(errors),
    }])

    msg = f"fetched={len(fetched)} new_on_topic={len(new)} total={len(known) + len(new)} errors={len(errors)}"
    log.info(msg)
    for e in errors:
        log.warning(e)
    print(msg)
    for e in errors:
        print("  error:", e)


if __name__ == "__main__":
    main()
