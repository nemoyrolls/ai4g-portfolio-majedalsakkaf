"""Pick 50 items for the honest test: 10 per line, half news / half Bluesky where possible.

Writes eval/labels.csv with an empty `label` column and NO model outputs,
so the person labelling is not influenced by what the models said.
Run once:  ../.venv/bin/python make_label_sheet.py   (from the eval/ folder)
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
import config  # noqa: E402

OUT = Path(__file__).parent / "labels.csv"
PER_LINE, SEED = 10, 6

if OUT.exists():
    sys.exit(f"{OUT.name} already exists - delete it first if you really want a new sample.")

df = pd.read_csv(config.ITEMS_CSV)
df = df[df["text"].str.len().between(40, 600)]
df["line"] = df["lines"].str.split(",").str[0]          # first matched line

picked = []
for line in config.LINES:
    pool = df[(df["line"] == line) & ~df["id"].isin([p["id"] for p in picked])]
    news = pool[pool["kind"] == "news"].sample(frac=1, random_state=SEED)
    public = pool[pool["kind"] == "public"].sample(frac=1, random_state=SEED)
    n_news = min(PER_LINE // 2, len(news))
    take = pd.concat([news.head(n_news), public.head(PER_LINE - n_news)])
    picked.extend(take[["id", "line", "kind", "source", "published_at", "text"]].to_dict("records"))

sheet = pd.DataFrame(picked)
sheet.insert(0, "nr", range(1, len(sheet) + 1))
sheet["label"] = ""          # positive / neutral / negative  (filled in by a human)
sheet["on_topic"] = ""       # yes / no: is it really about this green measure or the grid?
sheet["note"] = ""
sheet.to_csv(OUT, index=False)
print(f"Wrote {len(sheet)} items to {OUT}")
print(sheet.groupby(["line", "kind"]).size())
