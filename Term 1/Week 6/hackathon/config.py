"""Settings for Green Transition Pulse. Change topics, sources and models here only."""

import os
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
ITEMS_CSV = DATA_DIR / "items.csv"
RUNS_CSV = DATA_DIR / "runs.csv"
LOG_PATH = DATA_DIR / "collector.log"   # local debugging only, not committed

# Recorded in runs.csv so it is visible where each round ran.
RUN_LOCATION = "github-actions" if os.environ.get("GITHUB_ACTIONS") else "laptop"

# --- Models (both are run on every item, so the comparison covers all data) ---
# Main: multilingual, 3 classes incl. neutral, fine-tuned on ~198M tweets.
MAIN_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
# Comparison: Dutch-native RoBERTa, fine-tuned on Dutch book reviews, 2 classes only.
COMPARE_MODEL = "DTAI-KULeuven/robbert-v2-dutch-sentiment"

# --- The five lines on the dashboard ---
# "search": what we ask the sources for.
# "match": an item only counts for a line if its text contains one of these
#          (lowercase) fragments. This filters out search noise, e.g. "sociale isolatie".
LINES = {
    "Zonnepanelen": {
        "side": "green measure",
        "search": ["zonnepanelen", "salderingsregeling", "terugleverkosten", "thuisbatterij"],
        "match": ["zonnepaneel", "zonnepanelen", "saldering", "terugleverkosten",
                  "terugleveren", "thuisbatterij"],
    },
    "Warmtepomp": {
        "side": "green measure",
        "search": ["warmtepomp", "hybride warmtepomp"],
        "match": ["warmtepomp"],
    },
    "Isolatie": {
        "side": "green measure",
        "search": ["huis isoleren", "isolatiesubsidie", "spouwmuurisolatie",
                   "dakisolatie", "vloerisolatie", "woning isoleren"],
        "match": ["isoleren", "isolatiesubsidie", "spouwmuur", "dakisolatie",
                  "vloerisolatie", "na-isolatie", "woningisolatie", "isolatie van woning",
                  "isolatiemaatregel"],
    },
    "Laadpalen": {
        "side": "green measure",
        "search": ["laadpaal", "laadpalen", "snellader", "elektrische auto laden"],
        "match": ["laadpaal", "laadpalen", "laadplein", "snellader", "laadpunt",
                  "elektrische auto laden", "thuisladen"],
    },
    "Stroomnet": {
        "side": "bottleneck",
        "search": ["netcongestie", "stroomnet vol", "netbeheerder", "wachtrij stroomnet"],
        "match": ["netcongestie", "stroomnet", "elektriciteitsnet", "netbeheerder",
                  "transportcapaciteit", "wachtrij", "wachtlijst", "piekuren",
                  "stedin", "liander", "enexis", "tennet"],
    },
}

# Netbeheerder names / "wachtrij" are only relevant together with energy words.
GRID_CONTEXT = ["stroom", "net", "elektric", "energie", "aansluiting", "capaciteit"]

# --- Sources ---
GOOGLE_NEWS = {"hl": "nl", "gl": "NL", "ceid": "NL:nl", "window": "7d"}
BLUESKY_LANG = "nl"
BLUESKY_LIMIT = 100
RSS_FEEDS = {
    "NOS": "https://feeds.nos.nl/nosnieuwsbinnenland",
    "NU.nl Economie": "https://www.nu.nl/rss/Economie",
    "Tweakers": "https://feeds.feedburner.com/tweakers/mixed",
    "Energeia": "https://energeia.nl/feed",
}

USER_AGENT = "GreenTransitionPulse/1.0 (HHS student project)"
MAX_CHARS = 1000  # text stored and scored per item
