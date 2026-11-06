# Term 1 - Week 6: Language Models

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

**What did I hand in?**
_List the files, or link to them. Notebook exports, screenshots, scripts._

**What did I find difficult, and how did I solve it?**

### Checklist
- [ ] My workshop / homework files are in `homework/`
- [ ] Everything runs without errors, or I explained what does not and why

---


## 2. Hackathon prototype -> [`hackathon/`](hackathon/)

> Your tool and your SDG for this hackathon are announced at the **start of Friday's class**.
> Write them down here once you know them.

**Project title:** Green Transition Pulse (Hackathon 6 – Live Pulse), resubmission

**My pair partner:** none, I worked solo.

**Tool we had to use:** a pre-trained sentiment transformer from Hugging Face, run with `transformers`. I used
`cardiffnlp/twitter-xlm-roberta-base-sentiment` (main) and `DTAI-KULeuven/robbert-v2-dutch-sentiment` (comparison).

**SDG we had to address:** SDG 9 – Industry, Innovation and Infrastructure (target 9.4: retrofitting
infrastructure to be sustainable).

**What problem does it solve, and for whom?**
Dutch households are asked to go green (solar panels, heat pumps, insulation, EV charging) while the electricity
grid is full and the rules are changing. The user is the sustainability team of a municipality, the persona
*Noor Bakker* at the Municipality of The Hague. Each week they decide which green measure to promote and where to
put the subsidy and campaign budget, and today they notice frustration late.

**What did you build?**
A collector that fetches Dutch news (Google News, RSS) and Bluesky posts every hour, keeps the items about five
topics, scores each with two Hugging Face models and stores them with a timestamp. A Streamlit dashboard shows
% negative (or average mood) per topic per day or week, news vs public, and the items behind every peak or dip.
The honest test on 50 labelled items is in `hackathon/eval/`.

**Link to the live thing (if any):** the dashboard runs locally (see below); the hourly collection runs on
GitHub Actions (`.github/workflows/green-pulse.yml`, see the Actions tab of this repository).

**How do I run it?**
See [`hackathon/README.md`](hackathon/README.md#12-how-to-run): install `requirements.txt`, run
`collect.py` once, then `streamlit run app.py`.

**Who did what?**
Solo. Code written with Claude Code (AI coding assistant); all choices of topic, user, sources, models and the
dashboard's measure were mine. Claude drafted the 50 test labels and I checked each one.

**Ethical reflection - what are the risks of your tool? Who could it harm?**
The stream contains journalists and Bluesky users, not the renters, older residents and non-Dutch speakers who
most need help with the energy transition. The main model also misses half of the negative items and misreads
sarcasm, so the lines look calmer than reality. If the team moves budget away from a measure because "the mood is
fine", exactly the households without a voice in this data could be left behind. I store no names, handles or
post links, show the number of items behind every point, hide thin points, show a warning banner, and default to
"% negative", which the honest test showed to be the more trustworthy signal. Full reflection:
[`hackathon/README.md`](hackathon/README.md#10-ethical-reflection).

### Checklist
- [x] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [x] The prototype actually runs, and I wrote down how to run it
- [x] Ethical reflection written above

---

## 3. Presentation -> [`presentation/`](presentation/)

*Only fill this in for the week your group was selected to present. You need at least **one** of these across the whole term.*

- [ ] My group presented in this week
- [ ] Slides are in `presentation/`
- [ ] Proof of the live demo is in `presentation/` (recording, screenshots, or link)

**How did it go? What would I do differently next time?**

---

## 4. Reflection

**What is the most important thing I learned this week?**

**Where does this connect to "AI for Good"?**
_One concrete link to ethics, sustainability or social impact._
