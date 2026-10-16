# Heat Pump Pulse

**A live sentiment monitor of the UK public debate about heat pumps on Bluesky, built for a consumer advice team that has to decide which concern to address first.**

> AI for Good minor · Hackathon 6: *Live Pulse*

---

## At a glance

| | |
|---|---|
| **Project title** | Heat Pump Pulse |
| **My pair partner** | Haki Abdulovski |
| **Tool we had to use** | A pre-trained sentiment model from Hugging Face, run with the `transformers` library by our own code. We use [`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest). |
| **SDG we had to address** | SDG 9: Industry, Innovation and Infrastructure |
| **Data stream** | Bluesky's public real-time stream (Jetstream): every new English post that mentions heat pumps, in its own text or in a shared news article |
| **Named user** | The consumer advice team at the **Energy Saving Trust** (UK), the team that writes heat pump information for households (intended user, not a partner) |
| **Collection period** | Continuously since 12 October 2026, 11:04 UTC |

---

## 1. What problem does it solve, and for whom?

### The problem

Heat pumps are central to cutting carbon from home heating in the UK, but uptake is far behind plan. There were just over 30,000 certified installations in the first half of 2025, against a government target of 600,000 per year by 2028 ([pv magazine](https://www.pv-magazine.com/2025/08/06/record-uk-heat-pump-installations-for-h1-driven-by-grant-support/)). Two things hold households back:

- **Wrong beliefs are common.** In a 2023 survey, 24% of UK adults thought heat pumps cost more to run than a gas boiler, and 23% thought they are louder than a fridge ([Electrical Times, Opinium for Good Energy](https://www.electricaltimes.co.uk/brits-have-been-bamboozled-by-heat-pump-misinformation)).
- **Cost is the biggest worry.** In a 2025 poll of more than 2,000 people, 56% said heat pumps are "too expensive for most people" ([Irish News, Savanta for the Heating Trades Network](https://www.irishnews.com/news/uk/many-unaware-of-negative-heat-pump-myths-but-cost-is-big-issue-polling-finds-QW42LTVOZVKN7DLEDXIYXI7YWA/)).

Public concern also moves with the news. During our collection, on 12 October 2026, [the Guardian](https://www.theguardian.com/environment/2026/oct/12/ministers-plan-slash-heat-pump-subsidies-fund-defence-spending) and Politico reported that ministers are *considering* cutting the Boiler Upgrade Scheme (the grant of up to £7,500 per heat pump) to fund defence spending ([CIBSE Journal](https://www.cibsejournal.com/news/heat-pump-grants-face-cuts-as-ministers-search-for-billions-to-fund-defence/)). Reports like this create confusion and new questions among households overnight.

On Bluesky alone, around 150 posts about heat pumps appear on a normal day, and more than 200 on a news day, and nobody can read all of them. As the assignment puts it, an organisation usually notices a problem only once it is in the news. An advice team that publishes heat pump information therefore reacts late, and often to the wrong concern.

### The user and their decision

**User:** the consumer advice team at the [Energy Saving Trust](https://energysavingtrust.org.uk/about-us), an independent UK organisation that reaches "over two million people a year" with energy advice across England, Scotland, Wales and Northern Ireland. They already fight heat pump myths: their installer toolkit says "As heat pumps have grown in popularity, so have the myths surrounding them" ([EST toolkit](https://greenheattoolkit.energysavingtrust.org.uk/t/heat-pump-installers-toolkit/information-for-your-customers/heat-pump-information/)), and Home Energy Scotland, which the EST delivers, publishes [11 heat pump myths](https://www.homeenergyscotland.org/11-heat-pump-myths).

**Their decision, every week:**
1. **Which concern to address first** in their heat pump advice: cost and grants, installers, performance in the cold, noise, or myths.
2. **When a news event calls for extra explanation,** because households start worrying or spreading wrong information.

The EST is our *intended* user. We have not worked with them, and they are not using the tool.

### Why this fits SDG 9

SDG 9 is to "build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation" ([UN](https://sdgs.un.org/goals/goal9)). Target 9.4 asks countries to "upgrade infrastructure … with increased resource-use efficiency and greater adoption of clean and environmentally sound technologies".

Home heating is part of the energy infrastructure, and the heat pump is the clean technology replacing the gas boiler in millions of homes. Whether that change happens depends on more than the technology itself: people also have to trust it. Heat Pump Pulse helps the organisation that advises households to see, early, which worries and wrong beliefs slow that adoption down, so it can answer them. This is the "innovation reception" and "energy transition radar" kind of use the assignment describes.

### Why this is not a Google search

A search shows what newspapers write. It does not show how thousands of ordinary people react, how that reaction changes hour by hour, or which concern dominates this week. Heat Pump Pulse reads every post as it appears, scores it, and shows the change over time, with the posts behind every change one click away.

---

## 2. What did we build?

Heat Pump Pulse is three small Python programs that run continuously on one laptop. They collect every new English Bluesky post about heat pumps, score the tone of each post with a pre-trained transformer, and show the result on a live dashboard. On the dashboard the advice team can see how the tone and volume change over time, which theme is most negative, and read the actual posts behind any peak or dip before deciding what to act on.

**What a user can do with it:**
- See the **average tone per 6 hours or per day,** with the number of posts behind every point.
- See **when attention spikes,** with the volume of posts per period.
- See **which concern is most negative right now** (cost/grants, installers, performance/cold, noise, myths, politics/policy). Only themes with enough posts are ranked.
- **Open the posts behind any period** and read them in full, with their score, themes and any shared article.
- **Filter** by time range, country (rough guess) and theme.

### Example from our own data

The most negative period in our data so far is **Tuesday 13 October, 06:00 - 12:00 UK time** (average tone -0.29, 58 posts). That is the morning after the grant cut was reported, and it is also one of the busiest periods. Reading the posts behind the dip shows that several of the most negative posts are anger *about the cut*, from people who support heat pumps. For example:

> *"Together with more gas & oil … are looking to cut back on heat pump subsidy to fund defence … feckless!"* → scored **negative (−0.84)**

This is exactly why the dashboard says "tone is not opinion" at the top. 

---

## 3. Link to the live thing

The dashboard runs locally on our laptop and is not deployed publicly. That is deliberate: it has no login and shows real people's posts (see [section 9](#9-ethical-reflection)).

- **Screenshots:**

<p align="center">
  <img src="image1.png" width="800" alt="Heat Pump Pulse Beginning"><br>
  <em>Heat Pump Pulse Beginning</em>
</p>

<p align="center">
  <img src="image2.png" width="800" alt="Graph Tone per 6 hours"><br>
  <em>Tone per 6 hours</em>
</p>

<p align="center">
  <img src="image3.png" width="800" alt="Themes"><br>
  <em>Themes</em>
</p>

<p align="center">
  <img src="image4.png" width="800" alt="Posts with tone"><br>
  <em>Posts with tone</em>
</p>

- **Video demo:** https://youtu.be/DctY0l1Ure0
- **Live demo:** shown in the presentation.

---

## 4. How it works

```
Bluesky Jetstream (public live stream)
        │  every new post, in real time
        ▼
heatpump_collector.py   keeps heat pump posts, skips bots, stores them
        │
        ▼
   heatpump.db  (SQLite)  ◄──────────────┐
        │                                 │ writes the scores back
        ▼                                 │
heatpump_analyser.py   every 5 min: clean, exclude, score with the transformer
        │
        ▼
heatpump_dashboard.py  (Streamlit)  reads the database read-only, refreshes every 2 min
```

The three programs run independently and only share the database file. If one stops, the others keep working, and the stopped one catches up when it starts again.

### 4.1 `heatpump_collector.py`: fetching the posts

- **Source:** Bluesky's public [Jetstream](https://bsky.network/docs/jetstream-replay), which pushes every new post on the network as it happens. It needs no account, no API key and has no quota.
- **Filter:** a post is kept if "heat pump" (or "heat-pump", "heatpump", "air source", "ground source", "ASHP", "GSHP") appears in **the author's own text or in the title or description of a shared link.** The second part is important: many people share a news article with a short comment that doesn't mention heat pumps itself.
- **Skipped:**
  - posts about heat pumps in electric cars
  - posts in another language (posts without a language tag are kept, because link shares often have none)
  - known aggregator bots (for example `link.skysquare.app`, and posts in the form "#7 · Shared by 116 accounts")
- **Tags per post:** themes (keyword-based), a rough country hint (keywords plus the domain of a shared article, such as theguardian.com → UK), and a rough "first-hand experience" flag.
- **Never stored:** account names, handles or IDs. Each post is identified only by a salted hash, so posts cannot be looked up by account.
- **Deletions:** when an author deletes a post on Bluesky, the collector deletes it from the database too.
- **No gaps:** the collector saves its position in the stream. After a restart or a dropped connection it rewinds Jetstream to that position (Bluesky keeps about 36 hours of history) and continues, without gaps or duplicates.

### 4.2 `heatpump_analyser.py`: the sentiment analysis

Every 5 minutes it takes all posts that have not been analysed yet and:

1. **Cleans the text:** keeps only the author's own words and removes links, including the shortened links Bluesky puts in the text. The headline of a shared article is *not* scored, because it is the newspaper's tone, not the author's.
2. **Excludes posts that should not count,** and records why:
   - `automated_source`: shared from a site that posts automatically (marketresearchfuture.com, dlvr.it, citizenportal.ai, found by checking our data by hand)
   - `too_short`: fewer than 3 words of the author's own (for example a bare link share)
   - `duplicate`: the same text as an earlier scored post
3. **Scores the rest with the model:**
   - **label:** positive, neutral or negative, whichever class the model finds most likely
   - **score:** P(positive) - P(negative), from -1 (very negative) to +1 (very positive)

   Because the label and the score are calculated differently, a post can be labelled *neutral* with a score of +0.33: the model found "neutral" most likely, but with a slightly positive lean.
4. **Writes the results** back to the database, with a timestamp.

The model runs *before* the database is locked for writing, and all results are then written in one short step. This means the analyser never blocks the collector. An earlier version did, and it crashed the collector.

### 4.3 `heatpump_dashboard.py`: the view

A [Streamlit](https://streamlit.io) web page that reads the database read-only and refreshes itself every 2 minutes. Times are shown in UK time, because the user is a UK team; the database stores everything in UTC. From top to bottom:

1. A **warning** that tone is not the same as opinion, and that Bluesky users are not representative.
2. A **status line** showing whether the collector is live and how many posts are waiting for the model.
3. **Filters:** time range, per 6 hours or per day, country, theme.
4. **Headline numbers:** posts analysed, average tone, share negative, and the most negative period.
5. **Tone over time,** with hollow points for periods with fewer than 5 posts ("treat as noise"), and **volume over time** as a separate chart.
6. **"Which concern needs attention?":** tone per theme. Only themes with at least 15 posts are ranked; smaller ones are shown in grey at the bottom.
7. **The posts behind any period,** in full text or as a table. It opens on the most negative period by default.
8. **"How this works and what it cannot tell you":** the method and its limits.

### 4.4 The database (`heatpump.db`)

One SQLite table, `posts`, with one row per post:

| Column | Meaning |
|---|---|
| `post_hash` | salted hash of the post's ID (no account information) |
| `created_at`, `seen_at` | when the author says they posted, and when the stream delivered it (UTC) |
| `text` | the post text as written |
| `link_title`, `link_desc`, `link_domain` | the shared article, if any |
| `matched_in` | where "heat pump" was found: `text`, `link` or `both` |
| `themes`, `country`, `first_hand` | keyword-based tags |
| `clean_text` | the author's own words, as read by the model |
| `exclude_reason` | empty if scored; otherwise why the post was excluded |
| `sentiment_label`, `sentiment_score`, `sentiment_model`, `analysed_at` | the model's output and when it was produced |

SQLite was chosen because the collector and the analyser write to the same file at the same time, which goes wrong easily with a CSV file. For people who want to open the data without a database tool, `--export` writes a CSV file.

---

## 5. The model and why we chose it

**Model:** [`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest)

**From the model card:**
- **Architecture:** RoBERTa-base.
- **Training data:** about 124 million tweets from January 2018 to December 2021, then fine-tuned for sentiment on the TweetEval benchmark.
- **Language:** English only.
- **Labels:** 0 = negative, 1 = neutral, 2 = positive.
- **Licence:** CC BY 4.0.

**Why this one:**
- **Closest match to our text.** Bluesky posts are short, informal social-media posts, very similar to tweets. A model trained on movie or product reviews would be a worse fit.
- **Three classes, including neutral.** A large part of our stream is news sharing and factual statements, which a positive/negative-only model would be forced to push to one side.
- **English fits our stream,** which we filter to English.
- **It runs on an old laptop's CPU** (about 0.7 seconds per post), so it can run continuously without a GPU.

**Preprocessing,** as recommended on the model card: @mentions are replaced with `@user`, and links are removed before scoring.

**Not fine-tuned.** The assignment allows and recommends fine-tuning. We chose not to, because 50 labelled posts are far too few to fine-tune on without overfitting. We used them to test the model instead.

---

## 6. Data collected

*Snapshot of 15 October 2026, 20:47 UK time (19:47 UTC). The collector keeps running, so the live numbers are higher.*

| | |
|---|---|
| Collection period | 12 Oct 2026, 11:04 UTC – 15 Oct 2026, 19:45 UTC (about 3.5 days, without gaps) |
| Posts collected | 668 |
| Posts per day | 155 (12 Oct, from 11:04) · 212 (13 Oct, the day after the grant news) · 151 (14 Oct) · 150 (15 Oct) |
| Scored by the model | 620 |
| Excluded | 47 (14 automated sources, 23 duplicates, 10 too short); 1 more post was still waiting for the model |
| Bot posts skipped by the collector | 18 |
| Found through a shared link only | 48 posts (another 71 mention heat pumps in both the text and the shared link) |
| Most shared site | theguardian.com (19 posts) |
| Tone over all data | average -0.09; 31% negative, 51% neutral, 18% positive |
| Most negative period | Tuesday October 13th 2026 (06:00 - 12:00 UK · tone -0.29 · 58 posts) |
| Themes | cost/grants 262, politics/policy 143, performance/cold 134, installers 99, myths/misinformation 30, noise 5 (a post can have several) |
| Country hint | 63% unknown; UK 152, US 89, Canada 23, other 16 |
| First-hand experience (rough) | 62 posts (9%) |

Both requirements are met: more than 48 hours of continuous collection, and more than 300 items.

**Where the data is:** `heatpump.db` (the full database) and `posts.csv` (an export with times, texts, tags and scores, no account information).

---

## 7. Honest test of the model

### Method
- **Sample:** 50 posts drawn at random from all posts collected up to 14 October, after removing the same posts the analyser excludes:
  - 13 from automated sources
  - 6 with fewer than 3 words of the author's own
  - 10 repeats of a text already in the set

  That left 418 eligible posts. We drew 50 of them, split by day in proportion to the volume (18 from 12 Oct, 23 from 13 Oct, 9 from 14 Oct), with a fixed random seed of 6, so the draw can be repeated.
- **Labelling:** Majed labelled all 50 posts **before seeing any model output.** Each post got two labels:
  - **sentiment:** positive, neutral or negative (the tone, which is what the model measures)
  - **stance:** for, against or unclear (the author's position on heat pumps, which the model does *not* measure)

  Our labels: 18 negative, 22 neutral, 10 positive. Stance: 22 for, 3 against, 25 unclear.
- **Comparison:** `heatpump_test.py` ran the same 50 posts through the transformer and through **VADER**, a word-list sentiment baseline built for social media (standard thresholds of ±0.05). Both read exactly the same cleaned text as the live pipeline.

### Results

| | Agreement with our labels |
|---|---|
| **Transformer** (`twitter-roberta-base-sentiment-latest`) | **36 / 50 = 72%** |
| **VADER** (word-list baseline) | **24 / 50 = 48%** |

Both models were right on 19 posts. The transformer alone was right on 17, VADER alone on 5, and both were wrong on 9.

**Transformer: where it goes wrong** (rows = our label, columns = model)

| | model: negative | model: neutral | model: positive |
|---|---|---|---|
| **ours: negative** (18) | **13** | 4 | 1 |
| **ours: neutral** (22) | 4 | **16** | 2 |
| **ours: positive** (10) | 0 | 3 | **7** |

The transformer is about equally good on all three classes (70–73% of each found). Almost all its mistakes are one step off: negative vs neutral, or neutral vs positive. It turned a negative post into a positive one only **once** in 50.

**VADER: where it goes wrong**

| | VADER: negative | VADER: neutral | VADER: positive |
|---|---|---|---|
| **ours: negative** (18) | **8** | 0 | 10 |
| **ours: neutral** (22) | 2 | **8** | 12 |
| **ours: positive** (10) | 1 | 1 | **8** |

VADER calls 30 of the 50 posts positive, while we labelled only 10 as positive. It even called **10 of our 18 negative posts positive.** For example, it scores the headline *"Ministers preparing to slash heat pump subsidies…"* as positive (+0.10): in its word list, "energy" (+1.1) and "defence" (+0.4) outweigh "slash" (−1.1). A word list has no idea what the sentence is about.

**Tone is not opinion**

| | stance: for | stance: against | stance: unclear |
|---|---|---|---|
| **model: negative** (17) | **7** | 2 | 8 |
| **model: neutral** (23) | 9 | 1 | 13 |
| **model: positive** (10) | 6 | 0 | 4 |

**Of the 17 posts the transformer scored negative, 7 (41%) were written by someone in favour of heat pumps.** Only 2 were written by someone against them. Of the posts *we* labelled negative, the same 7 were in favour too. So the model is right that these posts are negative; they are just negative about something else (mostly the grant cut). This is the most important finding for our user: a dip in the line usually means people are *upset*, not that they are *turning against* heat pumps.

### Three failures, explained

**1. A complaint that sounds cheerful (the only negative → positive mistake)**
> *"But I'm still paying off the heat pump through 7 year no interest loan, so $336 every month for next 3.5 years!"*

- **Ours:** negative. **Transformer:** positive (+0.58). **VADER:** negative (−0.54).
- **Why it went wrong:** the post is a complaint about a long, expensive loan, but it ends with an exclamation mark and contains "no interest", which looks upbeat on the surface. The model reads the excited punctuation, not the frustration behind it. This is close to sarcasm. VADER got this one right, but for the wrong reason: it reads "no interest" as *a lack of interest* ("interest" is positive in its word list, and "no" flips it), not as an interest-free loan.

**2. Criticism hidden in questions and suggestions**
> *"Are they going to m date heat pumps in all new builds? Look at district heating schemes, heat capture from industrial processes, sewage works, mine shafts etc etc. Lots of solutions are possible if you not bothered about keeping bigoilhappy."*

- **Ours:** negative (stance: for). **Transformer:** neutral (−0.08). **VADER:** positive (+0.39).
- **Why it went wrong:** the anger is implicit. It's phrased as a question and a list of alternatives, with the real point in an accusation at the end ("keeping big oil happy"). There are no clearly negative words, and the typos ("m date" for *mandate*, "bigoilhappy" written as one word) hide the key phrase from both models. VADER even calls it positive: "solutions" counts as positive, and "not bothered" is read as the opposite of "bothered", so as positive too.

**3. A mixed message: looking forward to a heat pump, unhappy with the present**
> *"I can't wait until I can get a heat pump installed in this place but until then it's propane and wood and plastic film on the windows."*

- **Ours:** neutral (stance: for). **Transformer:** negative (−0.66). **VADER:** neutral.
- **Why it went wrong:** the post contains two feelings: eagerness about a heat pump ("I can't wait") and a grim description of the current situation. The model gives most weight to the second half and calls it negative. For our user this matters: the author is a *future heat pump owner*, yet the post pulls the line down.

**Some "mistakes" are arguable.** For example, we labelled the plain news headline *"Ministers preparing to slash heat pump subsidies…"* as negative, while the transformer called it neutral. A headline that reports bad news can reasonably be seen either way. With only one person labelling, part of the 28% disagreement is about how to label, not just model error.

### Which model would we hand to the user, and why?

**The transformer.**
- **It agrees with a human far more often:** 72% against 48%.
- **Its mistakes are small:** mostly one step (negative vs neutral), and only one complete flip in 50 posts.
- **VADER would paint a dangerously rosy picture.** It calls 30 of 50 posts positive where we found 10, and labels more than half of the negative posts positive, including news about the grant cut. An advice team using VADER would see a calm, positive line exactly when people are worried.

**But not without its limits,** and the dashboard says so:
- **72% means about 1 in 4 posts is labelled differently from how a human would.** That's fine for spotting *trends* across dozens of posts, but not for judging a single post.
- **50 posts is a small test.** The true agreement on all our posts could reasonably be anywhere between about 60% and 85%.
- **Tone ≠ stance.** 41% of the "negative" posts came from supporters of heat pumps, which is why the dashboard warns against reading the line as support or opposition, and why every dip can be opened.

The full test table, with our 50 labels, both models' output and the disagreements, is in `test_table.csv`; the summary is in `test_summary.txt`.

---

## 8. How do I run it?

You need Python 3.10 or newer. Everything runs on one machine and uses one `heatpump.db`. **Never run two collectors on two machines at the same time,** or your data is split across two databases.

### Install (once)

**Linux**
```bash
python3 -m venv venv
venv/bin/pip install websockets transformers streamlit vaderSentiment openpyxl
venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\pip install websockets transformers streamlit vaderSentiment openpyxl
venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu
```

The second command installs the CPU-only version of PyTorch, which is a much smaller download. The first time the analyser runs, it downloads the model (about 500 MB).

### Start the three programs

**Linux:** each one keeps running in the background, with its output in a log file.
```bash
nohup venv/bin/python -u heatpump_collector.py >> collector.log 2>&1 &
nohup venv/bin/python heatpump_analyser.py >> analyser.log 2>&1 &
venv/bin/streamlit run heatpump_dashboard.py --browser.gatherUsageStats false
```

**Windows:** use one PowerShell window per program.
```powershell
venv\Scripts\python heatpump_collector.py
venv\Scripts\python heatpump_analyser.py
venv\Scripts\streamlit run heatpump_dashboard.py --browser.gatherUsageStats false
```

Then open **http://localhost:8501** in a browser. To open the dashboard from another device on the same network, add `--server.address 0.0.0.0` and open `http://<ip of the machine>:8501`.

`--browser.gatherUsageStats false` stops Streamlit from sending usage statistics.

### Start automatically after a restart

- **Linux:** add these two lines with `crontab -e`, using your own folder:
  ```
  @reboot cd /home/<you>/heatpump && venv/bin/python -u heatpump_collector.py >> collector.log 2>&1
  @reboot cd /home/<you>/heatpump && venv/bin/python heatpump_analyser.py >> analyser.log 2>&1
  ```
- **Windows:** Task Scheduler → Create Basic Task → trigger "When I log on" → start `venv\Scripts\python.exe` with argument `heatpump_collector.py` and the project folder as "Start in". Make a second task for the analyser.

### Useful commands

| Command | What it does |
|---|---|
| `python heatpump_collector.py --status` | what is in the database, whether the collector is up to date, posts per hour |
| `python heatpump_collector.py --export posts.csv` | export the stored posts to CSV |
| `python heatpump_collector.py --replay-from 2026-10-12T22:00` | re-read the stream from a UTC time (within about 36 hours); posts already stored are skipped |
| `python heatpump_analyser.py --once` | score everything that is waiting, then stop |
| `pgrep -af heatpump` (Linux) | check that the collector and the analyser are running |

### Keeping it running
- **The machine must stay awake.** Turn off sleep mode and Wi-Fi power saving.
- **If the machine is off for less than about 36 hours,** the collector catches up completely when it starts again. Longer than that, and the oldest missed posts are lost.

---

## 9. Ethical reflection

**Who writes in our stream, and who doesn't.** Our stream contains English-speaking Bluesky users who chose to post about heat pumps. That is a small, online, politically engaged slice of the UK, and not the households the Energy Saving Trust most needs to reach. Older people, people without social media, people who don't write in English, and people who are struggling too much to post are missing completely. So "the line is calm" can simply mean that the worried people aren't on Bluesky. Research suggests that Bluesky tends to be [more left-leaning](https://phys.org/news/2025-02-bluesky-similarly-social-media-unusual.html), which means that some political viewpoints may be less represented.

**What the model misreads.** It measures tone, not opinion. In our data, several of the most negative posts are anger *about a cut to heat pump grants*, from people who support heat pumps: in our test, 7 of the 17 posts the model scored negative (41%) were written by people in favour of heat pumps. An advice team that reads a dip as "the public is turning against heat pumps" would draw the opposite of the truth. The model also misses sarcasm and only understands English. Our themes are found with keywords, and some of those keywords (*scam*, *lies*, *loud*) are negative in themselves, so the myths and noise themes lean negative partly by construction.

**Who could be harmed, and how.** Every post was written by a real person, and even without names, anyone can paste a sentence into Bluesky's search and find the author. If the dataset is published, a post someone later deletes stays visible in our copy. If the tool were used to judge or target individual posters rather than to understand the debate, it could single people out. And a team that trusts the line too much could put its effort into the wrong concern, or overlook the households who never post at all.

**What we did about it:**
- **No account names, handles or IDs are stored;** posts are identified only by a salted hash.
- **When an author deletes a post on Bluesky, we delete it too,** as Bluesky's [developer guidelines](https://docs.bsky.app/docs/support/developer-guidelines) require.
- **Bots and automated sources are skipped or excluded,** so they cannot move the line: 18 bot posts skipped, and 14 automated posts, 23 duplicates and 10 too-short posts excluded.
- **The number of posts is shown next to every score;** periods with fewer than 5 posts are marked as noise, and themes with fewer than 15 posts are not ranked.
- **A warning at the top of the dashboard** says that tone is not opinion and that Bluesky is not representative, and every dip can be opened so the user reads the actual posts before acting.
- **The dashboard is not published online,** and the dataset is in a private repository, shared only with our teachers, so the posts are not publicly available.

### What it must not be used for
- Measuring public **support for or opposition to** heat pumps: it measures tone, not opinion.
- Drawing conclusions about **all UK households:** Bluesky users are not representative.
- Singling out, contacting, or profiling **individual posters.**
- **Regional** decisions: the country tag is a rough guess, and there is no regional information.
- Training other models on the collected posts.

### Terms of the source
Bluesky posts are public by design ("Your posts and comments are public", [Bluesky Privacy Policy](https://bsky.social/about/support/privacy-policy)). Bluesky's [developer guidelines](https://docs.bsky.app/docs/support/developer-guidelines) do not forbid reading the public stream. They do require that content a user deletes is deleted (we do this) and that end-user data is protected (we store no account information and keep the data locally). Bluesky itself notes that it cannot enforce how outside developers use public posts ([TechCrunch](https://techcrunch.com/2024/11/27/blueskys-open-api-means-anyone-can-scrape-your-data-for-ai-training)); the responsibility is ours.

---

## 10. What went wrong, and what we learned

- **Missed posts through link shares.** At first the collector only looked at the post's own text. A search on Bluesky showed that most reactions to the grant story were *shares of a news article* with a short comment, and the words "heat pump" were only in the article's title. The collector now also checks the shared link.
- **A crash caused by our own analyser.** The first version of the analyser kept the database locked while the model was working (about 20 seconds per batch on an old laptop). The collector could not write, gave up after 30 seconds and stopped. We noticed it within an hour through the status check. The analyser now runs the model first and writes everything in one short step. The collector caught up the missed 47 minutes from Bluesky's buffer, so no data was lost.
- **Keeping a laptop awake.** Collection moved from a Windows laptop to an old Linux laptop that can stay on. We also had to turn off Wi-Fi power saving, which made the laptop unreachable over SSH even though it kept collecting.
- **Spam in the data.** Market-research sites and auto-posting services appeared in the stream. We found them by reading the data, and the analyser now excludes them.

---

## 11. Limitations

- **English only.** Welsh, Gaelic and posts by non-native speakers in other languages are not covered.
- **Mostly public debate, not owners' experience.** Only about 10% of posts read as first-hand experience; most are reactions to news and policy.
- **Country is a rough keyword guess,** and about 60% of posts have none. UK and US posts are mixed unless filtered.
- **Small numbers per hour,** especially at night, so the dashboard groups per 6 hours or per day.
- **Keyword-based themes** miss posts that use other words, and some keywords lean negative by themselves.
- **The 600,000-a-year target** was set by the previous government; in 2025 it was reported that the current government was “poised to ditch” it [Telegraph via Yahoo](https://www.yahoo.com/news/miliband-poised-scrap-600-000-111814676.html). We use it only to show how far uptake lags behind earlier plans, not as current policy.
- **The grant cut** was a reported plan, not a decision, at the time of collection.
- **The surveys we cite** were commissioned by the heat pump industry.

---

## 12. Who did what?

| | Haki | Majed |
|---|---|---|
| Choosing the topic, stream and user |✔ |✔ |
| Collector (fetching and storing) |✔ | |
| Analyser (model) and dashboard | ✔| |
| Running and monitoring the pipeline |✔ | |
| Labelling the 50 test posts | | ✔ |
| Test table and model comparison |✔ | |
| README and ethical reflection | |✔ |
| Presentation | |✔ |

**Use of an AI coding assistant:** we used Claude (Anthropic) as a coding assistant to help write the code and to research sources, as the assignment allows. The choices of topic, data stream, user, model and design are ours, and we can explain each of them.

---

## 13. Files in this repository

| File | What it is |
|---|---|
| `heatpump_collector.py` | collects heat pump posts from Bluesky and stores them |
| `heatpump_analyser.py` | scores every new post with the sentiment model |
| `heatpump_dashboard.py` | the live dashboard |
| `requirements.txt` | the Python packages needed |
| `heatpump.db` | the collected and scored data (SQLite) |
| `posts.csv` | the same data as CSV |
| `label_sample_50.xlsx` | the 50 test posts with our labels |
| `heatpump_test.py` | runs the honest test: our 50 labels against the transformer and VADER |
| `test_table.csv` | our labels next to both models' output |
| `test_summary.txt` | agreement, confusion tables and the disagreements |
| `README.md` | this file |

---

## Sources

- Energy Saving Trust, *About us*: https://energysavingtrust.org.uk/about-us
- Energy Saving Trust, *Heat pump information* (installer toolkit): https://greenheattoolkit.energysavingtrust.org.uk/t/heat-pump-installers-toolkit/information-for-your-customers/heat-pump-information/
- Home Energy Scotland, *11 heat pump myths*: https://www.homeenergyscotland.org/11-heat-pump-myths
- Electrical Times, *Brits have been bamboozled by heat pump misinformation* (Opinium for Good Energy, 2023): https://www.electricaltimes.co.uk/brits-have-been-bamboozled-by-heat-pump-misinformation
- Irish News, *Many unaware of negative heat pump myths but cost is big issue, polling finds* (Savanta for the Heating Trades Network, 2025): https://www.irishnews.com/news/uk/many-unaware-of-negative-heat-pump-myths-but-cost-is-big-issue-polling-finds-QW42LTVOZVKN7DLEDXIYXI7YWA/
- pv magazine, *Record UK heat pump installations for H1 driven by grant support*: https://www.pv-magazine.com/2025/08/06/record-uk-heat-pump-installations-for-h1-driven-by-grant-support/
- CIBSE Journal, *Heat pump grants face cuts as ministers search for billions to fund defence* (13 Oct 2026): https://www.cibsejournal.com/news/heat-pump-grants-face-cuts-as-ministers-search-for-billions-to-fund-defence/
- Hugging Face, `cardiffnlp/twitter-roberta-base-sentiment-latest` model card: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest
- Bluesky, *Developer Guidelines*: https://docs.bsky.app/docs/support/developer-guidelines
- Bluesky, *Privacy Policy*: https://bsky.social/about/support/privacy-policy
- Bluesky, *Network Replay with Jetstream*: https://bsky.network/docs/jetstream-replay
- TechCrunch, *Bluesky's open API means anyone can scrape your data for AI training* (Nov 2024): https://techcrunch.com/2024/11/27/blueskys-open-api-means-anyone-can-scrape-your-data-for-ai-training
- United Nations, *Goal 9*: https://sdgs.un.org/goals/goal9
- Researchers find Bluesky is similarly structured to other social media, but with some unusual features: https://phys.org/news/2025-02-bluesky-similarly-social-media-unusual.html
- Ministers preparing to slash heat pump subsidies to fund defence spending: https://www.theguardian.com/environment/2026/oct/12/ministers-plan-slash-heat-pump-subsidies-fund-defence-spending
- Miliband poised to scrap 600,000-a-year heat pump target: https://www.yahoo.com/news/miliband-poised-scrap-600-000-111814676.html