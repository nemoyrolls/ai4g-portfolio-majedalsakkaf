# Tourism investment and revenue

Hackathon 5, Model Showdown. Majed Al-Sakkaf and Akif Olgun.

**Question:** if a country added a lot of hotel rooms over the last 3 years, does its tourism revenue grow faster than the rest of the world over the next 2 years?

**Notebook:** [`tourism_investment_models.ipynb`](tourism_investment_models.ipynb) ([open in Colab](https://colab.research.google.com/github/nemoyrolls/ai4g-portfolio-majedalsakkaf/blob/main/Term%201/Week%205/hackathon/tourism_investment_models.ipynb))
**Ethical reflection:** [`ETHICS.md`](ETHICS.md)

---

## The problem

Many countries try to grow tourism by building hotels. Governments help with permits, tax breaks and public loans, because tourism brings jobs and foreign money. But building rooms doesn't guarantee that visitors come. If they don't, the country is left with empty hotels, debt and jobs that disappear again.

Tourism matters a lot for many economies. In 2019, tourism was directly worth a median of 3.7% of GDP in the 136 countries that reported it, and more than 10% in ten of them (UN Tourism, SDG indicator 8.9.1). For small island states and places like Macao, it's the main industry.

We wanted to know whether past hotel building tells you anything about future revenue. We use hotel rooms as a stand-in for investment because no free dataset has tourism investment in money for all countries.

## SDG

**SDG 8, Decent Work and Economic Growth**, target **8.9**: "devise and implement policies to promote sustainable tourism that creates jobs and promotes local culture and products." Our target is close to indicator 8.9.1, tourism's contribution to GDP. The question is about one specific policy choice (supporting more hotel capacity) and its effect on one outcome (tourism revenue), not about "the economy" in general.

## User and decision

**User:** a national tourism ministry, for example Morocco's Ministry of Tourism, deciding whether to support more hotel building in the coming years.

**What they do with it:** use the prediction as a first screen. If the model says "likely to beat the world," that supports looking further into a hotel programme. If it says "likely to lag," the ministry should first find out why before adding capacity.

**Who is affected:** hotel and restaurant workers, small tourism businesses, local communities near new hotels, and taxpayers who pay for public loans that go wrong.

**Who is not in the data:** countries that don't report hotel rooms (many low-income and conflict-affected countries), domestic tourists, Airbnb-type rentals, and anything after 2017.

## Dataset card

| | |
|---|---|
| **Sources** | [UN Tourism bulk download (May 2026)](https://www.untourism.int/tourism-statistics/tourism-statistics-database): hotel rooms, inbound tourism spending, tourist arrivals. [World Bank WDI](https://data.worldbank.org): exchange rate, GDP, GDP per person, inflation, region, income group. [datasets/country-codes](https://github.com/datasets/country-codes) to match country codes |
| **Who collected it, how** | UN Tourism collects yearly questionnaires from national statistics offices and tourism ministries. Spending comes from each country's balance of payments. The World Bank compiles national accounts, IMF and central bank data |
| **When** | 1995 to 2024. After cleaning, the rows we use cover 1998 to 2017 |
| **Licence** | UN Tourism data is copyrighted and free for student and research use. We don't store it in this repo; the notebook downloads it from UN Tourism. World Bank data is CC BY 4.0. Country codes are public domain |
| **Unit** | one country in one year. The brief asks for one row per person or company, but the decision we model is made by a country. We discussed this with our teacher |
| **Rows and columns** | 2,577 rows, 168 countries. 10 features (8 numeric, 2 categorical) and 1 target |
| **Target** | `target_beats_world`: 1 if the country's inbound tourism revenue grew more from year t to t+2 than the world median for the same years. 1,266 yes (49%) and 1,311 no (51%) |
| **Main feature** | `rooms_growth_3y`: change in hotel rooms over the previous 3 years |
| **Dropped rows** | 2,643 with no target, 1,677 with no room data, 570 whose window touches COVID (2020 to 2022), and 18 with impossible room growth (below −50% or above +200% in 3 years, almost always a change in counting method). The full log is in the notebook |
| **Known limitations** | Rich countries make up 42% of rows and low-income countries only 6%. Revenue is in nominal US$ and counts only foreign visitors. Hotel rooms miss other investment and short-term rentals. Income group is today's classification, applied to past years |

## How we built it

1. **Download** the UN Tourism and World Bank files (cached in `data/raw/`).
2. **Join** them on ISO3 country codes. Drop regional aggregates. Values flagged "low reliability" become missing.
3. **Build features** using only what is known at the end of year t, and the target from t+1 and t+2. Exact year joins only: a missing year stays missing.
4. **Drop rows** with no target or room data, with COVID years in the window, with a time series break, or with impossible room growth.
5. **Split first:** 20% of countries go to the test set with `StratifiedGroupKFold(random_state=42)`. Every year of a country stays on the same side, because neighbouring years share most of their data.
6. **Pipeline:** signed log for growth rates, log10 for money, median imputation with missing flags, scaling, and one-hot encoding of region and income group. Fitted inside every fold.
7. **Baselines:** `DummyClassifier(most_frequent)` and a one-line rule ("yes if room growth is above the training median").
8. **Tuning:** `GridSearchCV` with the same 5 country-grouped folds and F1 for all three models.
9. **Overfitting checks:** validation curves, learning curves and decision boundaries on two features.
10. **Test once,** then a group check by income group and region.

**Why F1:** both mistakes hurt. A wrong yes means public money goes into hotels that stay empty. A wrong no means a country that would have grown misses support and jobs. F1 is only high when precision and recall are both good. We report precision separately because a wrong yes is slightly worse.

## Results

Test set: 521 rows from 33 countries the models never saw.

| Model | Best hyperparameters | CV F1 (mean ± std) | Test precision | Test recall | Test F1 |
|---|---|---|---|---|---|
| Baseline: most frequent | – | 0.118 ± 0.237 | 0.000 | 0.000 | 0.000 |
| Baseline: room growth > median | – | 0.552 ± 0.032 | 0.559 | 0.559 | 0.559 |
| KNN | n_neighbors=11, weights=uniform | 0.516 ± 0.066 | 0.538 | 0.422 | 0.473 |
| **Logistic regression** | **C=0.1** | **0.561 ± 0.050** | **0.597** | **0.604** | **0.600** |
| Random forest | max_depth=None, min_samples_leaf=5 | 0.589 ± 0.040 | 0.609 | 0.578 | 0.593 |

**What we found:**
- Countries that added rooms fastest beat the world 60% of the time, against 41% for the slowest. The pattern is real but weak.
- The models only just beat the one-line rule (0.60 against 0.56). The gap is about the size of the spread over folds.
- KNN is the weakest and loses to the simple rule.
- The random forest overfits: train F1 0.91 against 0.59 in CV.
- Blue and red points overlap almost everywhere on the decision boundary chart, so no model can do much better with these features.

## Recommendation

We recommend the **logistic regression**, as a first screen and never as the final decision.

- Its test F1 is the best (0.60). The random forest is almost the same but memorises the training data.
- It shows the direction of every feature, so the ministry can see why it says yes or no.
- It only beats a simple rule by a little, so it doesn't replace a proper study of each country.
- The group check shows too many wrong yeses for poorer countries. For lower-middle income countries the false positive rate is 74%, for low income 63%, against 18% for high income. For those countries a yes should mean "look closer". See [`ETHICS.md`](ETHICS.md).

**Do not use it for:** automatic funding decisions, low-income countries without extra checks, forecasts after COVID, judging single hotel projects, or claiming that hotels cause growth.

## How to run

**Colab:** open the [notebook in Colab](https://colab.research.google.com/github/nemoyrolls/ai4g-portfolio-majedalsakkaf/blob/main/Term%201/Week%205/hackathon/tourism_investment_models.ipynb) and choose Runtime → Run all. No extra installs are needed, and the data downloads itself (about 18 MB).

**Locally:** run all cells in Jupyter. You need internet the first time, because the files are saved to `data/raw/` and reused after that. A full run takes about 1 to 2 minutes.

Tested with Python 3.13, pandas 2.3.3, numpy 2.3.5, scikit-learn 1.7.2, matplotlib 3.10.6, requests and openpyxl. Colab's default versions work as well. `random_state=42` is set everywhere, so you get the same numbers each run.

## Who did what

- **Together:** we came up with the idea and discussed which data to use and why.
- **Majed:** README, ethical reflection and presentation.
- **Akif:** the notebook (coding), sharing progress along the way.


