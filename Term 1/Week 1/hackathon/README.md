# Nederlands voor Nieuwkomers

Dutch survival vocabulary for older Arabic-speaking newcomers.

**Live app:** (https://buurt-arabic-dutch-buddy.lovable.app)
**Demo video:** `demo/demo.mp4`
**Slides:** `slides/hackathon1.pdf`
**Ethics:** `ETHICS.md`

Course: AI for Good, Hackathon 1
Tool: Lovable
SDG: 4, Quality Education (target 4.6)
Team: [[NAMES]]

---

## 1. The problem

People who move to the Netherlands after middle age end up with much less Dutch than people who arrive young, and most never catch up.

CBS found that over half of migrants had almost no Dutch when they arrived. It also found that arriving at a younger age predicts a higher level of Dutch later on, and that migrants with less education reach a lower level on average. Someone who arrives at sixty is usually in both groups.

There is a literacy problem behind it too. About 2.5 million people aged 16 and over in the Netherlands are low-literate, roughly one in six. Stichting Lezen en Schrijven names two causes that apply here: ageing, because language skill drops off with age, and the rising number of migrants who do not yet speak Dutch. Low literacy is linked to more GP and hospital visits, estimated at €257 million a year.

The problem shows up in a small number of places: the supermarket checkout, the doctor, the pharmacy, the gemeente desk, and letters that arrive in the post. Getting a dosage or an appointment time wrong has real consequences.

An example. In Dutch, *half negen* is 8:30, not 9:30. Numbers are said backwards, so 21 is *eenentwintig*, "one-and-twenty". These are not hard, but you cannot guess them, and missing one costs you an appointment.

Sources:
- CBS (2023), *Nederlandse taalvaardigheid van migranten en hun positie op de arbeidsmarkt*
- Stichting Lezen en Schrijven, *Factsheet Laaggeletterdheid in Nederland*
- CBS (2022), *Migrantenouderen in Nederland*

---

## 2. Who it is for

The user is an Arabic speaker, around 55 or older, who moved to the Netherlands in the last few years, often through family reunification, and now has to handle their own appointments, shopping and post in Dutch.

They read Arabic fluently but read Latin script slowly or not at all, so seeing a Dutch word written down does not tell them how to say it. They have a smartphone, usually set up by a child or grandchild, and not much confidence using apps. Many are past the age where inburgering is required, so nobody is teaching them. They use the phone up close, one-handed, in short sessions, often with worse eyesight and less steady hands than a younger user.

This app is not for:

- Learners studying for an inburgering or NT2 exam. There is no grammar and no writing here, so it will not get anyone through an exam.
- Learners who do not read Arabic. Everything is built on Arabic script, so a Ukrainian or Eritrean newcomer gets nothing out of it.
- People who cannot read at all in any script. They are the worst affected by the problem we described and the ones our app helps least. We deal with this in `ETHICS.md` rather than pretending otherwise.
- People without a smartphone or without data.

---

## 3. What we built

A web app with 100 Dutch words and phrases across 10 topics, practised in two directions, with audio and Arabic-script pronunciation on every item. No account, no login, no data collected.

| Level | Topics |
|---|---|
| A1 | supermarket, doctor, pharmacy, directions, gemeente, time and appointments |
| A2 | asking for clarification, talking about yourself, official letters, moeten and mogen |

Ten items per topic, so 100 in total. Because each one can be practised both ways, that is 200 questions. Each topic also has 8 language facts that rotate between sessions, 80 in total.

Every item is stored with five fields: the Dutch word, the Arabic meaning, the Dutch pronunciation written in Arabic letters, an Arabic sentence containing the Dutch word, and a Dutch sentence containing the Arabic word.

### How it works

1. The app opens on the topic list. It does not ask for a name or anything else.
2. The user picks a topic, then picks a direction: Dutch to Arabic (recognition) or Arabic to Dutch (recall).
3. A language fact appears in both languages, with audio. It changes each time the topic is opened.
4. The user answers 10 questions by tapping one of three options.
5. The app checks the answer against the stored pair, records it, and locks the options.
6. Feedback appears straight away: the correct pair, the pronunciation in Arabic letters, and audio.
7. After 10 questions the user gets a score and a list of the words they missed.
8. From there they can redo only the missed words, redo the same words in the other direction, or pick a new topic.
9. Progress is saved in localStorage on the device and survives a refresh.

### Two things we did on purpose

Every Dutch word is written out phonetically in Arabic letters, so *goedemorgen* appears as خُودَه‌مورخن. Somebody who reads Arabic well but cannot decode Latin script has no way to get from Dutch spelling to Dutch sound. This gives them one.

Practice runs in both directions because recognising a word and producing it are separate skills. Understanding *brood* when the cashier says it does not mean you can say it yourself when you need bread.

### Where Lovable comes in

There is no hand-written code in this project. The whole app was built with Lovable from written prompts. Lovable produced the React components, the routing, the scoring logic, the localStorage saving, the speech synthesis and the layout.

We wrote the course content and the accessibility requirements. Lovable built everything that runs.

The prompts are in `prompts/` and screenshots of the Lovable editor are in `prompts/screenshots/`.

### Audio

Audio uses the browser's built-in `speechSynthesis` API, with a Dutch voice for Dutch and an Arabic voice for Arabic. Every line has a speaker button, and Dutch lines also have a 🐢 button that repeats the same thing at 0.6x speed. There are no sound files and no external service, so the app is free to run and works offline after the first load.

### Running it

Open [[URL]] in a browser. Nothing to install. Audio needs a device with a Dutch text-to-speech voice, which is standard on Android, iOS, Windows and macOS.

---

## 4. Why this fits the problem

The problem is that this group cannot manage on their own in a few specific situations, so we built the vocabulary for those situations in a format they can actually use.

A printed word list would be simpler, but it cannot say anything out loud, and Dutch spelling gives an Arabic reader no route to the sound. It also cannot test recall, which is the part that fails at the counter.

Duolingo already exists, but it assumes you read Latin script, it moves fast, and it pushes you with streaks and timers. For this user those are obstacles rather than motivation. It also teaches general vocabulary instead of the words you need at a Dutch pharmacy.

A chatbot would need the user to type in a script they cannot write, would give answers of unpredictable length, and could state something wrong with complete confidence. That is a bad trade when someone is acting on medical or official information.

---

## 5. Working prototype

The app runs end to end with no manual steps: pick a topic, pick a direction, answer ten questions, get a score, redo the ones you missed. This is shown in `demo/demo.mp4`.

Limitations:

- It trains recognition and recall, not speaking or writing. That is the main boundary of this format and the first thing we would add next.
- If a device has no Dutch voice installed, the app shows a notice and carries on without audio instead of breaking.
- The Arabic transliterations are our own approximations of Dutch sounds that do not exist in Arabic. An NT2 teacher has not checked them.

---

## 6. Ethics

See `ETHICS.md`.

---

## Repository

```
README.md
ETHICS.md
slides/hackathon1.pdf
demo/demo.mp4
prompts/
prompts/screenshots/
src/
```
