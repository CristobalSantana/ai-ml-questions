# Waitlist

The Interview mode is not built yet. Before building it and its payments, the site measures interest with a waitlist: people see what the mode is and what it will cost, and leave their email if they want to hear when it opens.

## What people see

- **On the home screen**, under Study and Exam, an "Interview · coming soon" card with a dashed outline. Tapping it does not start a quiz: it opens what the mode is, its price, the email field and the "Notify me" button.
- **On the results screen**, under the score by topic, a one-line invitation with the same field. It does not appear in a browser that has already signed up.
- **Under the field**, what the email is for and a link to the privacy page, [`site/privacy.html`](../site/privacy.html), in English and Spanish.
- **After sending**, "Done. I will write to you once, when it opens." The browser remembers that it signed up, and on later visits the card says so instead of asking again.

The prices are `CONFIG.interviewPrice` and `CONFIG.earlyPrice` in `site/app.js`, in US$: 15, and 10 for those who sign up now. With `earlyPrice: null`, only the full price is shown. An empty `CONFIG.waitlistUrl` hides the card and the invitation.

## What is stored

The Worker stores the waitlist in its own D1 database, `ai-ml-questions-waitlist` (the `WAITLIST` binding in [`wrangler.jsonc`](../wrangler.jsonc)), apart from the anonymous answers, so that database never holds personal data. [`migrations-waitlist/0001_waitlist.sql`](../migrations-waitlist/0001_waitlist.sql) creates two tables:

| Table | Column | What it holds |
|---|---|---|
| `waitlist` | `email` | The email, lowercased and trimmed. One row per email |
| | `at` | When it arrived, in UTC |
| | `lang` | `en` or `es`, the language of the site at the time, so the announcement goes in that language |
| | `place` | `home` (the Interview card) or `results` (after a quiz) |
| `interest` | `day`, `lang` | A day in UTC and a language |
| | `opens` | How many browsers opened the Interview card for the first time that day |

**What is not stored:** IP addresses, cookies, names, or anything that links an email to the answers of a quiz.

**The reply does not reveal who signed up.** An email already on the list is not written again, and the Worker answers the same way either way, so the form cannot be used to check whether someone is on the list, which could reveal that they are looking for a job.

**Bots.** The form has a field people do not see, `website`. If it arrives filled in, the Worker answers as usual and stores nothing. If spam gets through anyway, [Turnstile](https://developers.cloudflare.com/turnstile/) can be added; it was left out because it loads a script from another domain on the page.

**The count of opened cards.** Each browser counts once, the first time it opens the card; the site remembers that in the browser. So `opens` approximates the people who saw the price and the form, and it can be compared with the sign-ups from the home screen.

## Seeing the data

**In the Cloudflare dashboard:** on the **D1 SQL database** page, select `ai-ml-questions-waitlist` and then **Console**:

```sql
-- Sign-ups by language and by place
SELECT lang, place, COUNT(*) FROM waitlist GROUP BY lang, place;

-- Sign-ups per week
SELECT strftime('%Y-%W', at) AS week, COUNT(*) FROM waitlist GROUP BY week ORDER BY week;

-- Browsers that opened the Interview card, per day
SELECT day, lang, opens FROM interest ORDER BY day DESC;
```

**With the script:** export the database and run [`scripts/waitlist.py`](../scripts/waitlist.py) on it.

```bash
npx wrangler login                                  # once, with the Cloudflare account
npx wrangler d1 export ai-ml-questions-waitlist --remote --output waitlist.sql
python scripts/waitlist.py waitlist.sql                      # sign-ups and opened cards, by week
python scripts/waitlist.py waitlist.sql --emails emails.csv  # the emails, with their language
```

`waitlist.sql` and `emails.csv` hold personal data: they are in `.gitignore` so they are not committed by mistake, and they are best deleted once used.

**Reading the numbers.** Sign-ups from the home screen are compared with the browsers that opened the card, and sign-ups from the results screen with the quizzes that reached the end, which come from the answers database (quizzes with 10 or more answers). The number of sign-ups that justifies building Interview is best decided before looking, so it is not reinterpreted afterwards. With the traffic of October 2026, about 130 quizzes started and 27 reached 10 answers per week, so sign-ups will be few.

## Keeping the promise

The privacy page and the form promise one email when Interview opens, with the launch price, nothing else, and deleting the email six months after the opening, or when the list closes if Interview never opens. Chile's data protection law, Ley 21.719, in force from December 1, 2026, asks for this kind of information and for these rights to be honored. So:

- **When Interview opens:** export the emails, write once to each person in their language, and six months later delete the list:
  `npx wrangler d1 execute ai-ml-questions-waitlist --remote --command "DELETE FROM waitlist"`
- **When someone asks to see or delete their email:** requests arrive at interviewquestions.iaml@gmail.com. Look it up or delete it in the dashboard console, or with
  `npx wrangler d1 execute ai-ml-questions-waitlist --remote --command "DELETE FROM waitlist WHERE email = 'name@example.com'"`,
  and reply to confirm.
- **If the promise changes:** update `site/privacy.html` (both languages and their dates) and the texts of the form in `STRINGS`, in `site/app.js`.
- **Before the first sale of Interview:** the privacy page covers only the free site and the waitlist, and it says so. It promises to describe what the paid mode stores (the payment platform, any account or purchase records) before Interview opens, so that section has to be written first.

## Locally

`npx wrangler d1 migrations apply ai-ml-questions-waitlist --local` creates the tables in a local copy, and `npx wrangler dev` serves the site and the Worker with both databases. In the remote database the tables already exist; in a new one they are created with `--remote`.
