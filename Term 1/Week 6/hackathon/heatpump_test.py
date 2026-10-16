#!/usr/bin/env python3
"""
Heat Pump Pulse: honest test of the model (Hackathon 6)

Compares our own labels on 50 posts with
  1. the transformer used in the pipeline (cardiffnlp/twitter-roberta-base-sentiment-latest), and
  2. VADER, a simple word-list sentiment baseline built for social media.

Both read exactly the same text as the pipeline does: the author's own words, links removed
(the same cleaning code as heatpump_analyser.py).

Input:   label_sample_50.xlsx   (columns: nr, seen_at, text, link_title, my_sentiment, my_stance, note)
Output:  test_table.csv         one row per post: our labels, both models' output, where they disagree
         test_summary.txt       agreement, confusion tables, tone vs stance, the disagreements

Run (from the project folder, next to heatpump_analyser.py):
  venv/bin/pip install vaderSentiment openpyxl        (once)
  venv/bin/python heatpump_test.py
"""

import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from heatpump_analyser import Scorer, clean, model_input   # same model and same cleaning as the pipeline

HERE = Path(__file__).resolve().parent
LABELS = HERE / "label_sample_50.xlsx"
TABLE = HERE / "test_table.csv"
SUMMARY = HERE / "test_summary.txt"
CLASSES = ["negative", "neutral", "positive"]


def vader_scores(texts):
    """VADER compound score per text, with the standard thresholds (±0.05) from the VADER authors."""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except ImportError:
        sys.exit("Install VADER first:  venv/bin/pip install vaderSentiment")
    analyzer = SentimentIntensityAnalyzer()
    out = []
    for t in texts:
        c = analyzer.polarity_scores(t)["compound"]
        out.append(("positive" if c >= 0.05 else "negative" if c <= -0.05 else "neutral", round(c, 4)))
    return out


def confusion(truth, pred):
    """Rows = our label, columns = model label."""
    table = pd.crosstab(pd.Categorical(truth, CLASSES), pd.Categorical(pred, CLASSES),
                        rownames=["our label"], colnames=["model label"], dropna=False)
    return table


def per_class(truth, pred):
    lines = []
    for c in CLASSES:
        n_true = sum(t == c for t in truth)
        n_pred = sum(p == c for p in pred)
        hit = sum(t == c and p == c for t, p in zip(truth, pred))
        recall = hit / n_true if n_true else float("nan")
        precision = hit / n_pred if n_pred else float("nan")
        lines.append(f"  {c:<9} we labelled {n_true:>2}, model said {n_pred:>2}, both {hit:>2}  "
                     f"(found {recall:.0%} of ours; {precision:.0%} of its '{c}' were right)")
    return "\n".join(lines)


def main():
    if not LABELS.exists():
        sys.exit(f"Not found: {LABELS}")
    df = pd.read_excel(LABELS)
    for col in ["my_sentiment", "my_stance"]:
        df[col] = df[col].astype(str).str.strip().str.lower()
    missing = df[~df["my_sentiment"].isin(CLASSES)]
    if len(missing):
        sys.exit(f"{len(missing)} posts have no valid sentiment label (rows: {missing['nr'].tolist()})")

    df["clean_text"] = df["text"].fillna("").map(clean)

    print("Loading the transformer ...")
    scorer = Scorer()
    t_out = scorer.score([model_input(t) for t in df["clean_text"]])
    v_out = vader_scores(df["clean_text"].tolist())

    df["model_label"] = [l for l, _ in t_out]
    df["model_score"] = [s for _, s in t_out]
    df["vader_label"] = [l for l, _ in v_out]
    df["vader_compound"] = [s for _, s in v_out]
    df["model_agrees"] = df["model_label"] == df["my_sentiment"]
    df["vader_agrees"] = df["vader_label"] == df["my_sentiment"]

    def disagreement(r):
        if r.model_agrees and r.vader_agrees:
            return ""
        if not r.model_agrees and not r.vader_agrees:
            return "both models wrong"
        return "only transformer wrong" if not r.model_agrees else "only VADER wrong"
    df["disagreement"] = df.apply(disagreement, axis=1)

    cols = ["nr", "seen_at", "clean_text", "link_title", "my_sentiment", "my_stance",
            "model_label", "model_score", "model_agrees", "vader_label", "vader_compound", "vader_agrees",
            "disagreement", "note"]
    df[cols].rename(columns={"clean_text": "text (author's own words)"}).to_csv(TABLE, index=False, encoding="utf-8-sig")

    n = len(df)
    truth = df["my_sentiment"].tolist()
    lines = []
    w = lines.append
    w(f"HONEST TEST: {n} posts labelled by hand, compared with two models\n")
    w(f"Our labels: {dict(Counter(truth))}")
    w(f"Our stance labels: {dict(Counter(df['my_stance']))}\n")
    for name, col in [("Transformer (cardiffnlp/twitter-roberta-base-sentiment-latest)", "model_label"),
                      ("VADER (word-list baseline)", "vader_label")]:
        pred = df[col].tolist()
        agree = sum(t == p for t, p in zip(truth, pred))
        w(f"{name}\n  agrees with us on {agree}/{n} posts = {agree / n:.0%}")
        w(per_class(truth, pred))
        w("  confusion table (rows = our label, columns = model):")
        w("  " + confusion(truth, pred).to_string().replace("\n", "\n  ") + "\n")

    both_right = int((df.model_agrees & df.vader_agrees).sum())
    only_t = int((df.model_agrees & ~df.vader_agrees).sum())
    only_v = int((~df.model_agrees & df.vader_agrees).sum())
    both_wrong = int((~df.model_agrees & ~df.vader_agrees).sum())
    w(f"Both right: {both_right} | only transformer right: {only_t} | only VADER right: {only_v} | both wrong: {both_wrong}\n")

    w("TONE IS NOT OPINION: model label vs our stance label")
    w("  " + pd.crosstab(df["model_label"], df["my_stance"]).to_string().replace("\n", "\n  "))
    neg = df[df["model_label"] == "negative"]
    neg_for = int((neg["my_stance"] == "for").sum())
    w(f"  Of the {len(neg)} posts the model scored negative, {neg_for} were written by someone FOR heat pumps "
      f"({neg_for / len(neg):.0%})." if len(neg) else "  The model scored no posts negative.")
    ours_neg = df[df["my_sentiment"] == "negative"]
    on_for = int((ours_neg["my_stance"] == "for").sum())
    w(f"  Of the {len(ours_neg)} posts WE labelled negative, {on_for} were FOR heat pumps.\n")

    w("POSTS WHERE THE TRANSFORMER DISAGREES WITH US (candidates for the failure examples)")
    for r in df[~df.model_agrees].itertuples():
        w(f"\n  #{r.nr}  ours: {r.my_sentiment} (stance {r.my_stance}) | transformer: {r.model_label} {r.model_score:+.2f}"
          f" | VADER: {r.vader_label} {r.vader_compound:+.2f}")
        w(f"  \"{r.clean_text}\"")
        if isinstance(r.link_title, str) and r.link_title.strip():
            w(f"  (shared article: {r.link_title})")

    text = "\n".join(lines)
    SUMMARY.write_text(text, encoding="utf-8")
    print("\n" + text)
    print(f"\nSaved {TABLE.name} and {SUMMARY.name}")


if __name__ == "__main__":
    main()
