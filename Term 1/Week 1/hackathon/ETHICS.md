# Ethical reflection

## Who is excluded

**People who cannot read any script.**
This is the biggest problem with our project. The people most damaged by the language barrier are often the ones who are illiterate in their first language as well, and our app is built entirely on reading Arabic. We exclude the people at the centre of the problem we set out to solve.

What that means for them: a tool like this widens the gap between literate and illiterate newcomers instead of closing it. The literate get better at Dutch and the illiterate stay where they are.

What we did: every line in the app has audio, so someone who reads slowly can work from sound instead. What we would do next: navigation by icon only, and a spoken instruction mode that needs no reading at all.

**People who do not read Arabic.**
The whole app is scaffolded in Arabic script. A Ukrainian, Eritrean or Polish newcomer with the same problem gets nothing from it.

What that means: we built something for one community and could easily describe it as a solution for newcomers in general, which would be wrong.

What we did: we named the user group precisely in the README instead of overclaiming. The data structure keeps the language layer separate, so adding another language pair is a content job rather than a rebuild.

**People without a smartphone, data, or usable eyesight.**
Delivering only through an app assumes a device and vision.

What we did: no login, no data collected, works offline after the first load, 22px text and 64px buttons. What we would do next: a printable version of each topic.

## What the app assumes about its learner

That they own a phone with a Dutch text-to-speech voice. That they read Arabic. That they can tap accurately. That they will practise on their own.

The last one is probably the weakest assumption. For older people, language learning is usually social, and an app is a poor replacement for a taalcafé or a class with other people in it.

## How it could be used for the wrong reasons

**As a cheap substitute for teaching.**
A municipality or welfare organisation could point at a free app instead of funding NT2 classes for older residents. Our app teaches 100 words. A course teaches a language.

What that means: the people who need a teacher get an app instead, and the budget quietly disappears.

What we did: the README states that this does not prepare anyone for an inburgering or NT2 exam. We would rather be described accurately than adopted widely.

**As a test.**
Nothing stops an organisation from treating the score as a measure of someone's Dutch. It is not one. It measures recognition of 100 words that we chose.

What we did: no score is stored, sent anywhere, or exportable. Progress stays in the device's localStorage and nowhere else.

**Teaching a wrong pronunciation with confidence.**
Our Arabic transliterations approximate Dutch sounds that do not exist in Arabic, and machine text-to-speech is not a native speaker.

What that means: someone could learn a pronunciation that a Dutch listener does not recognise, and then be misunderstood at exactly the moment it matters, like at a pharmacy counter.

What we did: audio sits next to every transliteration so the sound is the main source and the script is only a support. What we would do next: have an Arabic-speaking NT2 teacher check the transliterations, and replace machine audio with recordings by native speakers.

## Data and dignity

The app asks for no name, no account, no email, no age and no country of origin. It collects no analytics. Nothing leaves the device.

That is deliberate and not only about privacy. Our users have usually just been through months of registration, interviews and forms. An app that opens by demanding personal details repeats the experience we are trying to make easier. The welcome screen says in Dutch and Arabic that nothing is stored about them.

The same thinking shaped the interface. There are no streaks, no points, no timers and no failure sounds. A wrong answer is marked *bijna*, meaning almost, and never *fout*. These are adults with careers and families behind them, learning something difficult in a hard situation. Software that scolds them would be worse than no software.

The language facts come from the same idea. Most of them show Arabic words that Dutch borrowed: *koffie*, *alcohol*, *admiraal*, *cijfer*, *algebra*. The learner is not only receiving a language. Some of their language is already inside this one.
