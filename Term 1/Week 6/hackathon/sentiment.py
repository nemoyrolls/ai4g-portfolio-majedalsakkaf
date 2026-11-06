"""Runs both Hugging Face models on a list of texts."""

from transformers import pipeline

import config

_main = pipeline("sentiment-analysis", model=config.MAIN_MODEL, top_k=None, truncation=True, max_length=512)
_cmp = pipeline("sentiment-analysis", model=config.COMPARE_MODEL, top_k=None, truncation=True, max_length=512)


def _probs(result):
    return {r["label"].lower(): r["score"] for r in result}


def score(texts, batch_size=16):
    main = _main(texts, batch_size=batch_size)
    cmp = _cmp(texts, batch_size=batch_size)
    out = []
    for m, c in zip(main, cmp):
        m, c = _probs(m), _probs(c)
        out.append({
            "main_label": max(m, key=m.get),
            "main_pos": m["positive"],
            "main_neu": m["neutral"],
            "main_neg": m["negative"],
            "main_mood": m["positive"] - m["negative"],
            "cmp_label": max(c, key=c.get),
            "cmp_mood": c["positive"] - c["negative"],
        })
    return out
