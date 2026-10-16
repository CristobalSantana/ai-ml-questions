# Website

`site/` is a static site: HTML, CSS and JavaScript with no frameworks, with the fonts bundled. Its only external script is Cloudflare Web Analytics ([Hosting](hosting.md#visits)).

## Quiz rules

- **Count:** 10, 25, 50, 100 or 200 questions. If fewer questions match the chosen filters, an "All (N)" option appears.
- **Filters:** levels and topics. Collection and stability are left for later.
- **Sampling:** stratified by area and level, so a mixed quiz is not dominated by the area with the most questions. It uses the 17 areas, not the 8 topics, so regrouping topics does not change which questions come up. It never repeats a question within a quiz and avoids recently seen ones (history stored in the browser).
- **Shuffled options** in each quiz, except with `keep_order`; that is why the answer is stored by id and not by position. In 500,000 test shuffles, the correct option landed in each position between 24.9% and 25.1% of the time.
- **Visible difficulty:** each question shows a green, yellow or red dot with the level written next to it, so it does not rely on color alone.
- **Modes:** study (explanation after each answer) and exam (score and explanations at the end).
- **Long quizzes:** 200 questions take about 2 to 3 hours, so progress is saved in the browser.
- **At the end:** score by topic and level, review of mistakes, a result to share and a Ko-fi button.
- **On each question:** a link to report a mistake and, for `volatile` questions, the date of the last review.
- **Only questions** with `origin` `human` or `llm_reviewed` are published. While the bank is in alpha, drafts are published too ([Hosting](hosting.md#building-and-testing)).

## Name

**AI/ML Questions** in English and **Preguntas IA/ML** in Spanish, with an "alpha" badge («alfa» in Spanish) for as long as the site is in alpha. The name is descriptive on purpose: it says what the site is with the same words someone would type into a search engine. To change it:

- `site/app.js`: `siteName` in `STRINGS.en` and in `STRINGS.es`.
- `site/index.html`: the `<title>`, `og:site_name` and the initial header text.
- `site/manifest.webmanifest`: `name` and `short_name`.
- `scripts/make_assets.py`: `NAME`. Then run the script to regenerate `og-image.png`.

To end the alpha, delete the `<span class="badge">` from `site/index.html`.

## Screens

1. **Home:** the name, the language switch (EN/ES) and the site's goal. Then difficulty (the three dots), topics, number of questions and mode, with how many questions are available for those filters. If there is an unfinished quiz, it offers to resume it.
2. **Question:** the dot with the level written next to it, the topic and subtopic, the stem, and the options as answer-sheet bubbles. In study mode, answering marks the correct option and shows each option's rationale, the explanation and the sources. On a computer, keys 1 to 4 (or A to D) choose and Enter moves on. The language can be switched mid-quiz without losing progress.
3. **Results:** score, correct answers by difficulty and by topic, the message to share, Ko-fi and the review of mistakes, with the option to retry only the missed questions.

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
Lo que mejor me fue: Redes neuronales. Lo que más me costó: Retrieval y RAG.
¿Cuánto sacas tú? https://ai-ml-questions.strangemachines.workers.dev/#es
```

- The topics line appears only if the quiz had at least two topics with two or more questions each, and with different results.
- The Spanish link ends in `#es`, so whoever opens it sees the site in Spanish.

LinkedIn builds the link card from the Open Graph tags in `index.html`: the title "How much do you know about AI and machine learning?", the description and `og-image.png` (1200 × 627). The card is in English and the same for both languages, because LinkedIn ignores what comes after the `#`; a Spanish card would need its own path, such as `/es/`, with its own tags. Since the site is static, the card is the same for everyone; an image with each person's score needs a Worker to generate it (phase 2). LinkedIn caches the card, so after changing it you have to refresh it with LinkedIn's Post Inspector.

## Offline and installable

With `manifest.webmanifest` and `sw.js`, the site can be installed on a phone and works offline. On the first visit, the service worker stores what `precache.json` lists (the page, the fonts, the icons and every question); after that it answers from what it stored and updates it in the background. `scripts/build_site.py` changes the service worker version whenever a file changes, so browsers download the new files.

## Languages

- **English by default.** The site opens in English and can be switched to Spanish with the EN/ES button; the choice is saved in the browser.
- **Links per language.** `#es` or `#en` at the end of the link opens the site in that language. The order of precedence is: the link's language, the saved choice and, if there is neither, English. The site ignores the browser's language, so the default is always English.
- **Questions.** English is required and Spanish optional; if a question has no Spanish, it is shown in English. The validator summary counts how many questions each language has.
- **Interface.** The texts are in `STRINGS`, in `site/app.js`, one set per language. Adding another language means adding it to `CONFIG.languages`, to `STRINGS`, to the schema and to the questions.

Strange Machines and ml-toy-experiments are in English, which favors English for reach; Spanish has less competition and serves readers in Chile and Latin America.
