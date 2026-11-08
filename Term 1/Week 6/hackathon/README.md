# 🌱 Green Transition Pulse

**Hackathon 6 – Live Pulse · SDG 9 (Industry, Innovation and Infrastructure) · Majed Al-Sakkaf (solo) · resubmission**

A tool that keeps reading Dutch news and Bluesky posts about **going green at home** (solar panels, heat pumps,
insulation, EV charging) and about **the electricity grid that has to carry it**. Every item is scored by a
pre-trained Hugging Face transformer, stored with a timestamp, and shown as a mood line per topic, so a
municipal sustainability team can see **which green measure people are ready for, and where frustration is building**.

> Not a chatbot. Nobody types questions into it: it reads, measures and shows.

---

## 1. The user and the decision

**User (persona):** *Noor Bakker*, energy-transition advisor in the sustainability team of the Municipality of
The Hague. Noor is a **persona**, not a real employee. The role is real: Dutch municipalities run energy desks
(energieloket), insulation subsidies and "off gas" campaigns for households.

**Noor's decision, every week in the heating season:**
*Which green measure do we promote next, and where do we put the subsidy and campaign budget?*

| Pulse shows | Noor acts |
|---|---|
| Frustration about solar panels rises as net metering ends (1 Jan 2027) | Moves campaign budget from solar to **insulation**: it saves money now and puts no extra load on the grid |
| Heat-pump talk is positive, but grid mood is falling in the same weeks | Promotes **"insulate first, then a heat pump"** and adds a session on grid limits to the info evening |
| Negative peak about one measure (e.g. noise or permit problems with heat pumps) | Opens the items behind the peak, adds the objection to the FAQ and the next info evening |
| Little is written about a measure | Does **not** read silence as satisfaction (see section 9) |

**Why a pulse and not a survey?** Surveys come a few times a year. Prices, rules and grid news change week by
week, and campaigns that land in the wrong week waste budget.

## 2. Problem definition

The Netherlands is electrifying faster than the grid can grow:

- On 30 June 2026, **15,498 requests to take power from the grid** were waiting with the regional grid operators,
  up from 15,154 at the end of 2025. Together they ask for 9,986 MW. Another 8,558 requests were waiting to feed
  power in. *(Netbeheer Nederland half-year figures, reported by [TPO, 5 Oct 2026](https://tpo.nl/2026/10/05/netcongestie-wachtlijst-stroomnet-netbeheer-halfjaarcijfers/))*
- **Net metering for solar panels ends on 1 January 2027.** After that, households can no longer offset the
  electricity they feed in against what they use. *([Rijksoverheid – salderingsregeling](https://www.rijksoverheid.nl/onderwerpen/energie-thuis/salderingsregeling))*
- From **2029**, replacing a central-heating boiler in a suitable home should require at least a hybrid heat pump.
  Who exactly falls under the rule is not yet clear. *([Solar Magazine](https://solarmagazine.nl/nieuws-zonne-energie/i45012/warmtepomp-verplicht-in-2029-installateurs-moeten-klaarstaan-maar-wie-er-precies-onder-valt-wordt-volgend-jaar-pas-duidelijk), [Consumentenbond](https://www.consumentenbond.nl/warmtepomp/hybride-warmtepomp-vanaf-2029-mogelijk-verplicht))*

**What goes wrong today:** households are asked to go green at the same time as they hear the grid is full and
the rules are changing. A municipality notices the resulting frustration late, through complaints or the news,
and runs its campaigns on a fixed calendar. *This last point is our assumption from the user's role; it was not
measured, and should be checked with a real sustainability team.*

## 3. Why SDG 9

SDG target **9.4**: *upgrade infrastructure and retrofit it to make it sustainable, with greater adoption of
clean technologies*. Homes switching from gas to heat pumps, solar and insulation, plus a grid that must keep up,
is exactly that retrofit of infrastructure. Target **9.1** asks for affordable and fair access to that
infrastructure, which is why the tool also tracks the grid bottleneck and its costs. The rubric names energy as
infrastructure for this hackathon. We frame the project around **infrastructure**, not only climate (SDG 13) or
energy prices (SDG 7).

## 4. The data stream and its terms

| Source | What we fetch | Key? | Terms – what we checked | What we store |
|---|---|---|---|---|
| **Google News RSS** (nl-NL) | Headlines for 21 Dutch search terms, last 7 days | No | Public RSS feed. Google's terms allow personal, non-commercial use; we store only headline, outlet and link | Headline, outlet, link, time |
| **Bluesky** public search API (`app.bsky.feed.searchPosts`, `lang=nl`) | Latest Dutch posts for the same terms | No | Public posts through Bluesky's official public API. Bluesky's developer guidelines ask services to honour deletions; we could not load the full guidelines page to check whether that applies to a small research script. To limit the harm we store **no handles, names or post links**, and replace @-mentions with `@user` | Post text, time |
| **RSS feeds**: NOS, NU.nl Economie, Tweakers, Energeia | All items, then filtered on our topic words | No | Public RSS feeds, used for non-commercial study | Title + summary, link, time |

Only items that **contain one of the topic words** are kept (`config.py`, `LINES[...]["match"]`). This removes
search noise such as *sociale isolatie* (social isolation).

## 5. How it works

```
 scheduled hourly (GitHub Actions)
        │
        ▼
 sources.py ── Google News NL · Bluesky (nl) · 4 RSS feeds
        │
        ▼
 collect.py ── keep on-topic items, assign to lines, skip ones we already have
        │
        ▼
 sentiment.py ── XLM-RoBERTa (main) + RobBERT (comparison), both on every item
        │
        ▼
 data/items.csv (one row per item, timestamped)  +  data/runs.csv (one row per round)
        │
        ▼
 app.py ── Streamlit dashboard: % negative or mood per line per day/week,
            volume, media vs public, and the items behind every point
```

**The five lines**

| Line | Side | Example search terms |
|---|---|---|
| Zonnepanelen (solar) | green measure | zonnepanelen, salderingsregeling, terugleverkosten, thuisbatterij |
| Warmtepomp (heat pump) | green measure | warmtepomp, hybride warmtepomp |
| Isolatie (insulation) | green measure | huis isoleren, isolatiesubsidie, spouwmuurisolatie, dakisolatie |
| Laadpalen (EV charging) | green measure | laadpaal, snellader, elektrische auto laden |
| Stroomnet (grid) | bottleneck | netcongestie, stroomnet vol, netbeheerder, wachtrij stroomnet |

An item can belong to more than one line (e.g. *"De laadpaal en warmtepomp terreur op het stroomnet…"*).

## 6. The models (model card summaries)

| | **Main: `cardiffnlp/twitter-xlm-roberta-base-sentiment`** | **Comparison: `DTAI-KULeuven/robbert-v2-dutch-sentiment`** |
|---|---|---|
| Base model | XLM-RoBERTa base, further trained on ~198M tweets | RobBERT v2, a Dutch RoBERTa |
| Fine-tuned on | Tweet sentiment in 8 languages: Arabic, English, French, German, Hindi, Italian, Spanish, Portuguese. **Not Dutch** | Dutch Book Reviews Dataset (DBRD), ~19.5k reviews from hebban.nl |
| Labels | negative / neutral / positive | negative / positive (no neutral) |
| Licence | Not stated on the model card | MIT |
| Known limits | Dutch only through transfer from other languages | The card itself says other domains were "not exactly amazing"; most review authors were women |
| Paper | [XLM-T (Barbieri et al.)](https://arxiv.org/abs/2104.12250) | [RobBERT (Delobelle et al., 2020)](https://www.aclweb.org/anthology/2020.findings-emnlp.292) |

**Why these two:** our stream is short, informal social posts plus neutral news headlines. XLM-RoBERTa was trained
on short social-media text and has a **neutral** class, which most news needs. RobBERT is the opposite bet:
it **knows Dutch well** but was trained on book reviews and can only say positive or negative. Comparing them
answers the question "does knowing the language matter more than knowing the type of text?"

Both models are run on **every** item, so the comparison covers all the data, not only the test set.
The mood score is `P(positive) − P(negative)`, from −1 to +1.

## 7. Honest test

**Method.** 50 items from our own stream: 10 per line, 5 news and 5 Bluesky per line, picked at random
(`eval/make_label_sheet.py`, fixed seed). The label rule: *what tone does this item have about the green measure
or the grid?* Factual announcements are **neutral**. Sarcasm is labelled by what it **means**. We also marked
whether the item is really on topic.

> **Transparency:** the 50 labels were **drafted by Claude (AI assistant) and then checked one by one by me**
> (column `checked_by_majed` in `eval/labels.csv`). The model outputs were not in the sheet while labelling.

Full results: [`eval/RESULTS.md`](eval/RESULTS.md) · every item, label and output: [`eval/test_table.csv`](eval/test_table.csv)

### Agreement with the human labels

| Model | All 50 | Only the 30 non-neutral | News (25) | Bluesky (25) |
|---|---|---|---|---|
| **XLM-RoBERTa (main)** | **64%** | 43% | 76% | 52% |
| RobBERT Dutch (comparison) | 38% | **63%** | 24% | 52% |
| Word list (no-AI baseline) | 62% | 40% | 84% | 40% |

Human labels: 21 negative, 20 neutral, 9 positive.

### What the user actually sees: the average per line

| Line | Human average | XLM-R average mood | RobBERT average mood |
|---|---|---|---|
| Isolatie | 0.00 | −0.08 | −0.09 |
| Laadpalen | −0.10 | +0.06 | +0.42 |
| Stroomnet | **−0.50** | **−0.06** | +0.37 |
| Warmtepomp | −0.30 | +0.01 | +0.08 |
| Zonnepanelen | −0.30 | 0.00 | +0.20 |

### What this shows

1. **XLM-RoBERTa is too mild.** Of the 21 negative items, it called 10 "neutral". The average mood is pulled
   to almost zero: the grid (human −0.50) looks only slightly negative (−0.06). Grid **news** is the worst case:
   *"Deel van Gelderland krijgt aansluitstop op stroomnet"* (connection stop) is clearly bad news for a resident,
   but there is no emotional word in it, so the model says neutral. It got only 30% of the grid items right.
2. **When XLM-RoBERTa says "negative", it was right every time (9 of 9).** It misses negatives, but it does not
   invent them.
3. **RobBERT knows Dutch but not our kind of text.** It was trained on book reviews and must choose positive or
   negative, so 17 of 20 neutral items became "positive". Its average for the grid is **+0.37**: the wrong sign.
4. **The word list nearly equals XLM-RoBERTa on all 50 items, but in a different way.** It does well on news
   headlines (84%) because words like *duurder*, *stop* and *vertraagd* do the work there. It fails on Bluesky
   (40%) where people use sarcasm, insults and slang. Our word list contains only general Dutch sentiment words;
   an earlier version contained words copied from the test items, which made it look better than it is, so we
   removed those.

### Five failures, explained

| # | Item (shortened) | Human | XLM-R | Why it fails |
|---|---|---|---|---|
| 8 | *"…die terugleverkosten… dus door de airco vandaag hele dag aan te zetten ontlasten we het volle stroomnet… Goed bezig. 😎"* | negative | **positive** | **Sarcasm.** "Goed bezig 😎" looks positive, but the writer is mocking the feed-in costs |
| 44 | *"Deel van Gelderland krijgt aansluitstop op stroomnet, stop Utrecht wordt verlengd"* | negative | neutral | **Jargon / domain knowledge.** A connection stop is bad news, but only if you know what it means |
| 13 | *"Een verplichte warmtepomp? De consument verleiden is voor iedereen beter"* | negative | neutral | **Mixed message.** Against the *obligation*, not against heat pumps. One label per item cannot capture this |
| 38 | *"Het resultaat van 15 jaar zonder visie: bedankt Mark!… Rokende puinhopen… Aansluitstop laadpalen door vol stroomnet"* | negative | **positive** | **Sarcastic thanks + political anger.** "bedankt" is read literally |
| 39 | *"Mooie Deal! De INIU 30W USB-C snellader…"* | (off topic) | positive | **Keyword noise.** "snellader" also means a phone charger; this advert is not about EV charging at all |

### Which model would I hand to Noor?

**XLM-RoBERTa**, with two changes that came directly from this test:

1. **The dashboard shows "% negative items" by default**, not the average mood. Because the model's "negative"
   was always right, this share is a trustworthy *lower bound* on frustration, while the average hides it.
2. **Read direction, not level.** A line rising from 20% to 35% negative is a signal worth opening; "29% negative"
   on its own is not a fact about residents.

RobBERT is not usable here: wrong sign on the grid line. The word list is tempting for news headlines but breaks
on public posts. **Next step:** fine-tune on a few hundred labelled items from this stream (allowed by the
brief), especially grid news, where the model misses the most.

## 8. The dashboard

`app.py` (Streamlit), written for someone who does not program:

- **Warning banner** about who is missing from the data
- **Five numbers** at the top: % negative per line, and the change compared with the first half of the period
- **Chart per day or week**, with dot size = number of items; points based on fewer than 5 items are hidden
- **Volume** chart: a peak often means an event
- **Media vs public**: news headlines vs Bluesky posts per line
- **"What's behind a peak or dip?"**: pick a line and a day, see every item sorted from most negative, with both
  models' labels
- A notice when the collector was not running, so straight lines across a gap are not read as trends

## 9. User group

**Who reads the pulse:** the sustainability team (Noor), weekly during the heating season. Secondary readers: the
energy desk (energieloket), which answers residents' questions, and the communications team that plans campaigns.

**Whose voices are in the stream:**
- **Journalists** (Google News, RSS): mostly factual headlines, more often about problems than successes
- **Bluesky users**: people who post publicly online, often engaged with climate or politics, and likely to already own
  solar panels or an EV (our impression from reading the items, not measured). Some are probably not Dutch-based (one test item seems to come from Belgium)
- **Organisations**: municipalities and energy cooperatives announcing info evenings

**Who is missing:**
- **Renters and low-income households**, who often cannot install solar panels or a heat pump, and post less about it
- **Older residents and people who are not online**, many of them homeowners who decide about their own boiler
- **Non-Dutch speakers**: we only fetch Dutch posts (`lang=nl`) and Dutch news
- **Most of the public**: Bluesky is a small, specific platform; X, Facebook and neighbourhood WhatsApp groups are not included
- **Businesses on the grid waiting list**, who complain to the grid operator, not online

## 10. Ethical reflection

The biggest risk is that Noor trusts the line more than is justified. A falling line can mean residents are happier,
or that unhappy people stopped posting, or that Bluesky users are simply not the people who need help. A campaign
budget moved away from a measure because "the mood is fine" could leave exactly the households without a voice
in this data, renters and older people, behind. The model adds its own bias: it under-reads negative grid news and
misreads sarcasm, so it makes things look **calmer** than they are. One very active account, or a bot posting
adverts with the word *snellader*, can move a thin line.

**What we did about it:**
- Store **no names, handles or post links**; mentions become `@user`
- Show the **number of items** next to every point, and **hide points with fewer than 5 items**
- A **warning banner** on the dashboard and a "not for" line at the bottom
- Default to **% negative**, the measure the honest test showed to be trustworthy
- A notice for **collection gaps**, so missing data does not look like a trend

**What it must not be used for:** judging individual people or neighbourhoods; ranking residents or posters;
concluding that no posts means no problem; replacing talking to residents; as evidence for or against a policy
on its own.

## 11. Data collected and how long it ran

**Only items found by automatic rounds count.** As of 8 Nov 2026, 10:20 UTC: **79 items** (48 news, 31 Bluesky posts)
from **7 GitHub Actions rounds** since 7 Nov, 00:28 UTC (the first was started with the "Run workflow" button, the other 6 by the schedule). The dashboard shows only these.

`data/items.csv` also holds 2,360 items from 3 manual test rounds on my laptop (12 Oct and 6 Nov). They are kept
for traceability, but are not counted or shown. `data/runs.csv` lists every round with its time and where it ran
(`github-actions` or `laptop`), and each item's `collected_at` links it to its round.

**Honest note on the timing:** the workflow is scheduled every hour, but GitHub delays scheduled jobs. In the first
34 hours it ran 7 times, with gaps of up to 7.8 hours. Each round looks back over recent items (Bluesky: the latest
100 posts per term; Google News: the last 7 days), so a delay should lose little, but the rounds are not hourly.
Each item keeps both `published_at` (when it was written) and `collected_at` (when we found it).

## 12. How to run

```bash
cd "Term 1/Week 6/hackathon"
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python collect.py          # one collection round (first run downloads both models, ~1.5 GB)
.venv/bin/streamlit run app.py       # dashboard on http://localhost:8501
```

**Continuous collection:** `.github/workflows/green-pulse.yml` (in the repository root) runs `collect.py` every
hour at :17 (GitHub often runs it later) and commits the new rows. It can also be started by hand from the GitHub **Actions** tab ("Run workflow").

**Honest test:** `cd eval && ../.venv/bin/python evaluate.py` recomputes `RESULTS.md` and `test_table.csv`
from `labels.csv`.

| File | Purpose |
|---|---|
| `config.py` | Topics, search terms, sources, model names |
| `sources.py` | Fetchers for Google News, Bluesky, RSS |
| `collect.py` | One collection round |
| `sentiment.py` | Runs both models |
| `app.py` | Dashboard |
| `eval/make_label_sheet.py` | Picks the 50 test items |
| `eval/labels.csv` | The 50 human labels |
| `eval/evaluate.py` | Honest test → `RESULTS.md`, `test_table.csv` |

## 13. Use of AI assistance

The code was written with Claude Code (AI coding assistant), as allowed by the brief. The choices were mine:
the topic, the user, the sources, both models and why, the measure shown to the user, and the label rule. Claude
drafted the 50 test labels and I checked and corrected each one.
