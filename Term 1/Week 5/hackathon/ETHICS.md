# Ethical reflection

Our model doesn't decide about one person, but it can influence where public money for tourism goes. That money becomes jobs for hotel staff, cooks, cleaners and drivers, or it becomes debt. So the people affected are workers and small businesses who never appear in our data by name.

## Who is in the data and who is missing

**Rich countries are over-represented.**
42% of our rows are high-income countries and only 6% are low-income. Poorer countries report hotel rooms less often, so many of them drop out.

What that means: the model learned mostly from rich countries like Denmark and the Netherlands, but the ministries that need help most are in poorer countries. The population in our data doesn't match the population we want to use it for.

What we did: we checked performance for every income group instead of reporting one score. We state in the README that low-income countries need extra checks.

**Countries in conflict are almost invisible.**
Countries at war often stop reporting. The few that are in the data, like Iraq, Yemen and Syria around 2000, are among the model's most confident mistakes. The model knows nothing about wars or sanctions.

What that means: for fragile countries the model can look confident while being blind to the biggest risk.

What we would do next: add a conflict or political stability indicator, or exclude fragile states from the model's scope.

**Domestic tourists, Airbnb and everything after 2017.**
Revenue only counts foreign visitors. Rooms only count hotels. Short-term rentals grew a lot after 2015, and Eurostat platform data only starts in 2018. COVID forced us to stop at 2017.

What that means: a country where domestic tourism or rentals are growing looks worse than it is. And tourism after COVID may follow different rules.

What we did: we name these gaps in the notebook and README and say the model must not be used for post-COVID forecasts.

## The mistakes and who pays for them

**A false positive** (the model says "will beat the world" and it doesn't). The ministry backs more hotels, public loans go out, and the visitors don't come. Hotels stand half empty, staff get laid off, and taxpayers carry the debt. In small economies one bad hotel programme can hurt a whole region.

**A false negative** (the model says "will lag" and the country would have done well). Support gets held back, hotels don't get built, and the jobs never exist. This cost is less visible, but it's real, especially for young people in tourism regions with few other jobs.

We chose F1 because both mistakes hurt, and we report precision separately because a wrong yes costs more: money spent is gone, while a delayed decision can still be made later.

## The group check: the model is too optimistic about poorer countries

This was our most important finding. On the test set:

| Income group | Rows | False positive rate (wrong yes) |
|---|---|---|
| Low income | 48 | 63% |
| Lower middle income | 71 | 74% |
| Upper middle income | 197 | 57% |
| High income | 205 | 18% |

For high-income countries the model rarely says yes by mistake. For lower-middle income countries, three out of four countries that lagged still got a yes. That's the opposite of what you want, because poorer countries can least afford a failed investment. The groups are small, so the exact numbers are uncertain, but the gap is too big to be chance alone.

What we did: we put this table and a chart in the notebook. We recommend the model only as a first screen, and say that for low and lower-middle income countries a yes means "look closer", not "go ahead". We would rather the model be used carefully than used widely.

What we would do next: set a stricter cut-off (for example 0.65 instead of 0.5) for these groups and check whether that brings the wrong yeses down without losing all the right ones.

## Is a sensitive variable hiding somewhere?

We include income group and region as features. That means the model partly judges a country by where it is and how rich it is, not only by what it does. A country in a "good" region can get a yes just for its neighbours.

What that means: two countries with the same hotel growth can get different predictions because of their region. That can lock in old patterns.

What we did: we show the model's weights in the notebook, so the effect of region and income is visible instead of hidden. What we would do next: compare a version without region and income group to see how much they drive the result.

## How it could be misused

**As an automatic decision.** A ministry or investor could plug in numbers and treat the probability as an answer. The model is barely better than a one-line rule (F1 0.60 against 0.56). It isn't good enough to decide on its own.

**As proof that hotels cause growth.** It shows that the two go together, not that one causes the other. Hotels are often built *because* tourists are already coming. Someone could use our chart to justify a hotel programme that has nothing to do with demand.

**To judge one hotel project.** The model works at country level. It can't say whether a specific hotel in a specific city will pay off.

**As a public ranking.** A list of countries "likely to lag" could scare investors away and make the prediction come true.

What we did: the README has a clear "do not use it for" list covering all four.

## Were people asked, and does the licence allow this?

The data is national statistics, not personal data, so no individual's privacy is at risk. No person can be identified. The figures come from official reports that countries send to UN Tourism and the World Bank.

World Bank data is CC BY 4.0, so we can use and share it with credit. UN Tourism data is copyrighted and free for student and research use, but not for redistribution. So we don't store it in our repo; the notebook downloads it from UN Tourism's own website. Anyone using this outside a university setting should ask UN Tourism for permission.
