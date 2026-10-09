# Term 1 - Week 5: Machine Learning Basics

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

**Project title:** Tourism investment and revenue

**My pair partner:** Akif Olgun

**Tool we had to use:** scikit-learn (KNN, logistic regression and a model of our choice: random forest)

**SDG we had to address:** SDG 8, Decent Work and Economic Growth (target 8.9, sustainable tourism)

**What problem does it solve, and for whom?**
A national tourism ministry, for example Morocco's, deciding whether to support more hotel building. Our model predicts whether a country's tourism revenue will grow faster than the world over the next 2 years, based on how many hotel rooms it added in the last 3 years plus its economy.

**What did you build?**
A notebook that goes from the raw UN Tourism and World Bank files to a fair comparison of three tuned classifiers on 2,577 country-years (168 countries, 1998 to 2017). The ministry can enter its own numbers and get a yes/no with a probability. Logistic regression did best (test F1 0.60), only a little better than a one-line rule (0.56).

**Link to the live thing (if any):**
[Notebook on GitHub](hackathon/tourism_investment_models.ipynb) · [Open in Colab](https://colab.research.google.com/github/nemoyrolls/ai4g-portfolio-majedalsakkaf/blob/main/Term%201/Week%205/hackathon/tourism_investment_models.ipynb)

**How do I run it?**
Open the notebook in Colab and choose Runtime → Run all. No installs are needed and the data downloads itself. Details are in [`hackathon/README.md`](hackathon/README.md).

**Who did what?**
We came up with the idea together and discussed which data to use. I wrote the README, the ethical reflection and the presentation. Akif wrote the notebook and shared his progress with me along the way.

**Ethical reflection - what are the risks of your tool? Who could it harm?**
The model can influence where public money for tourism goes, so a wrong yes can mean empty hotels, lost jobs and debt for taxpayers. Our group check showed it's too optimistic about poorer countries: 74% of lower-middle income countries that lagged still got a yes, against 18% for high-income countries. Rich countries also make up most of the data. So we recommend it only as a first screen, never for automatic decisions, and say that a yes for a poorer country means "look closer". Full version: [`hackathon/ETHICS.md`](hackathon/ETHICS.md).

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
