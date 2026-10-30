# Website

`site/` is a static site: HTML, CSS and JavaScript with no frameworks, with the fonts bundled. Its only external script is Cloudflare Web Analytics ([Hosting](hosting.md#visits)). Each answer is sent anonymously to the site's Worker for the statistics of each question ([Statistics](statistics.md)).

## Quiz rules

- **Count:** 10, 25, 50, 100 or 200 questions. If fewer questions match the chosen filters, an "All (N)" option appears.
- **Filters:** levels and topics. Collection and stability are left for later.
- **Sampling:** stratified by area and level, so a mixed quiz is not dominated by the area with the most questions. It uses the 17 areas, not the 8 topics, so regrouping topics does not change which questions come up. It never repeats a question within a quiz and avoids recently seen ones (history stored in the browser).
- **Order:** from easiest to hardest, by level and then by the rubric score, so a quiz warms up instead of opening with a hard question. In the first answers recorded, half of the people who missed their first question left right there. Retrying the mistakes follows the same order.
- **Shuffled options** in each quiz, except with `keep_order`; that is why the answer is stored by id and not by position. In 500,000 test shuffles, the correct option landed in each position between 24.9% and 25.1% of the time.
- **Visible difficulty:** each question shows a green, yellow or red dot with the level written next to it, so it does not rely on color alone.
- **Type of reasoning:** next to the difficulty, an outlined tag shows what kind of thinking the question asks for, from Bloom's taxonomy: Remember, Understand, Apply, Analyze or Evaluate. It is kept apart from the difficulty on purpose ([Difficulty](difficulty.md#difficulty-is-not-the-bloom-level)).
- **Modes:** study (explanation after each answer) and exam (score and explanations at the end).
- **Long quizzes:** 200 questions take about 2 to 3 hours, so progress is saved in the browser.
- **At the end:** score by topic and level, review of mistakes, a result to share and a Ko-fi button.
- **Footer:** links to Ko-fi, to the repository on GitHub and to the privacy page (`CONFIG.kofiUrl`, `CONFIG.repoUrl` and `CONFIG.privacyUrl`).
- **On each question:** a link to report a mistake and, for `volatile` questions, the date of the last review.
- **Answers:** each final answer is sent once, anonymously: in study mode on choosing, in exam mode on moving on. `CONFIG.answersUrl` in `site/app.js` says where; empty stops sending ([Statistics](statistics.md#what-is-recorded)).
- **Only questions** with `origin` `human` or `llm_reviewed` are published. While the bank is in alpha, drafts are published too ([Hosting](hosting.md#building-and-testing)).

## Name

**AI/ML Questions** in English and **Preguntas IA/ML** in Spanish, with an "alpha" badge («alfa» in Spanish) for as long as the site is in alpha. The name is descriptive on purpose: it says what the site is with the same words someone would type into a search engine. To change it:

- `site/app.js`: `siteName` in `STRINGS.en` and in `STRINGS.es`.
- `site/index.html`: the `<title>`, `og:site_name` and the initial header text.
- `site/manifest.webmanifest`: `name` and `short_name`.
- `scripts/make_assets.py`: `NAME`. Then run the script to regenerate `og-image.png`.

To end the alpha, delete the `<span class="badge">` from `site/index.html`.

## Screens

1. **Home:** the name, the language switch (EN/ES) and the site's goal. Then difficulty (the three dots), topics, number of questions and mode, with how many questions are available for those filters. Under the two modes, a "Coming soon" row with a card for each planned product, Interview, Enterprise and the online book, each with a (?) and its price tag; a card opens its [waitlist](waitlist.md). If there is an unfinished quiz, it offers to resume it. Under the start button, the latest [updates](#updates).
2. **Question:** the dot with the level written next to it, the type of reasoning, the topic and subtopic, the stem, and the options as answer-sheet bubbles. In study mode, answering marks the correct option and shows each option's rationale, the explanation and the sources. On a computer, keys 1 to 4 (or A to D) choose and Enter moves on. The language can be switched mid-quiz without losing progress.
3. **Results:** score, correct answers by difficulty and by topic, the invitation to the Interview waitlist, the message to share, Ko-fi and the review of mistakes, with the option to retry only the missed questions.

## Updates

The home screen lists the latest changes under the start button: one short sentence per change, grouped by day, newest first. The date is written 10/25/2026 in English and 25/10/2026 in Spanish. The most recent days are shown until there are at least three changes (`UPDATES_SHOWN` in `site/app.js`), so the home screen stays short however many updates pile up; older ones are folded under "Earlier updates (N)" («Actualizaciones anteriores (N)»), which opens the whole list.

The list lives in `updates.json`, at the root of the repository:

```json
{ "date": "2026-10-25", "text": { "en": "One sentence.", "es": "Una oración." } }
```

Each update needs a date as YYYY-MM-DD and one sentence in each language, of up to 140 characters in English and 160 in Spanish. Updates of the same day keep the order of the file. `scripts/build_site.py` checks them and copies them into `site/data/index.json`, so after editing `updates.json` the site has to be built again; `tests/test_updates.py` fails if the two differ.

## Sharing on LinkedIn

LinkedIn's share URL (`https://www.linkedin.com/sharing/share-offsite/?url=...`) accepts only the link; the post text cannot be prefilled. So the button copies the message to the clipboard and opens LinkedIn with the link, and the person pastes the text. On phones, the "Share…" button («Compartir…» in Spanish) opens the system's share menu.

The message is built from the result, in the chosen language, and the person can edit it before copying:

```
I answered 25 AI and machine learning questions and got 19 right (76%).
🟢 Easy 8/8 · 🟡 Medium 8/12 · 🔴 Hard 3/5
Best topic: Neural networks. Hardest for me: Retrieval & RAG.
How many can you get? https://ai-ml-questions.strangemachines.workers.dev/
```

```
Respondí 25 preguntas de IA y machine learning y acerté 19 (76%).
🟢 Fácil 8/8 · 🟡 Medio 8/12 · 🔴 Difícil 3/5
En lo que mejor me fue: Redes neuronales. Lo que más me costó: Retrieval y RAG.
¿Cuánto sacas tú? https://ai-ml-questions.strangemachines.workers.dev/#es
```

- The topics line appears only if the quiz had at least two topics with two or more questions each, and with different results.
- The Spanish link ends in `#es`, so whoever opens it sees the site in Spanish.

LinkedIn builds the link card from the Open Graph tags in `index.html`: the title "How much do you know about AI and machine learning?", the description and `og-image.png` (1200 × 627). The card is in English and the same for both languages, because LinkedIn ignores what comes after the `#`; a Spanish card would need its own path, such as `/es/`, with its own tags. Since the site is static, the card is the same for everyone; an image with each person's score needs a Worker to generate it (phase 2). LinkedIn caches the card, so after changing it you have to refresh it with LinkedIn's Post Inspector.

## Offline and installable

**The page does not move while it loads.** `index.html` preloads the fonts of the first screen, and `fonts.css` uses `font-display: optional`, so text never switches fonts after it appears; on a slow first visit the system font stays until the next visit. `build_site.py` writes the number of questions and topics into the header, and the loading line fills the screen, so neither the header nor the footer jumps when the data arrives. Cloudflare Web Analytics shows the result under Core Web Vitals, as CLS.

With `manifest.webmanifest` and `sw.js`, the site can be installed on a phone and works offline. On the first visit, the service worker stores what `precache.json` lists (the pages, the fonts, the icons and every question); after that it answers from what it stored and updates it in the background. `scripts/build_site.py` changes the service worker version whenever a file changes, so browsers download the new files.

## Languages

- **English by default.** The site opens in English and can be switched to Spanish with the EN/ES button; the choice is saved in the browser.
- **Links per language.** `#es` or `#en` at the end of the link opens the site in that language. The order of precedence is: the link's language, the saved choice and, if there is neither, English. The site ignores the browser's language, so the default is always English.
- **Questions.** English is required and Spanish optional; if a question has no Spanish, it is shown in English. The validator summary counts how many questions each language has.
- **Interface.** The texts are in `STRINGS`, in `site/app.js`, one set per language. Adding another language means adding it to `CONFIG.languages`, to `STRINGS`, to the schema and to the questions.

Strange Machines and ml-toy-experiments are in English, which favors English for reach; Spanish has less competition and serves readers in Chile and Latin America.
