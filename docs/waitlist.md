# Waitlist

Three paid products are planned and not built yet: **Interview**, questions like those of an ML/AI Engineer job interview; **Enterprise**, sets of AI/ML questions for recruiters; and an **online book** of 200 multiple-choice questions for ML/AI roles. Before building them and their payments, the site measures interest in each one with a waitlist: people see what the product is and what it will cost, and leave their email if they want to hear when it opens.

## What people see

- **On the home screen**, under the modes, a "Coming soon" row with one card per product, with a gold border that shines softly: its name, a (?) and what those who sign up now will pay, with the launch price after it (Interview: US$10, then US$15; Enterprise: US$100, then US$120), or, for the book, which has no price yet, "−40% if you sign up now".
- **The (?)** shows what the product is, on hover, on keyboard focus or on a tap: "A set of interview questions for ML/AI Engineers", "A set of AI/ML questions for recruiters" and "An online book of 200 multiple-choice questions for ML/AI roles".
- **Tapping a card** does not start a quiz: below the row it opens what the product is, its price, the email field and the "Notify me" button. Tapping it again, or another card, closes it.
- **On the results screen**, under the score by topic, a one-line invitation to Interview with the same field. It does not appear in a browser that has already signed up for Interview.
- **Under the field**, what the email is for and a link to the privacy page, [`site/privacy.html`](../site/privacy.html), in English and Spanish.
- **After sending**, "Done. I will write to you once, when it opens." The browser remembers which products it signed up for, and on later visits that product's card says so instead of asking again.

The products and their prices are `CONFIG.products` in `site/app.js`, in US$: `price` is the launch price, `early` what those who sign up now will pay, and `discount` the percentage off for a product without a price. Their names, the text of each (?) and what each one is are in `STRINGS`. An empty `CONFIG.waitlistUrl` hides the cards and the invitation. A new product also needs its id in `PRODUCTS` in [`worker/index.js`](../worker/index.js) and in [`scripts/waitlist.py`](../scripts/waitlist.py).

## What is stored

The Worker stores the waitlists in their own D1 database, `ai-ml-questions-waitlist` (the `WAITLIST` binding in [`wrangler.jsonc`](../wrangler.jsonc)), apart from the anonymous answers, so that database never holds personal data. [`migrations-waitlist/`](../migrations-waitlist/) creates two tables; 0002 and 0003 replaced those of 0001, which had a single waitlist, Interview's:

| Table | Column | What it holds |
|---|---|---|
| `signups` | `email` | The email, lowercased and trimmed |
| | `product` | `interview`, `enterprise` or `book`. One row per email and product, so a person can ask to hear about more than one |
| | `at` | When it arrived, in UTC |
| | `lang` | `en` or `es`, the language of the site at the time, so the announcement goes in that language |
| | `place` | `home` (a product's card) or `results` (after a quiz, Interview only) |
| `opens` | `day`, `lang`, `product` | A day in UTC, a language and a product |
| | `opens` | How many browsers opened that product's card for the first time that day |

**What is not stored:** IP addresses, cookies, names, or anything that links an email to the answers of a quiz.

**The reply does not reveal who signed up.** An email already on a product's list is not written again, and the Worker answers the same way either way, so the form cannot be used to check whether someone is on the list, which could reveal that they are looking for a job.

**Bots.** The form has a field people do not see, `website`. If it arrives filled in, the Worker answers as usual and stores nothing. If spam gets through anyway, [Turnstile](https://developers.cloudflare.com/turnstile/) can be added; it was left out because it loads a script from another domain on the page.

**The count of opened cards.** Each browser counts once per product, the first time it opens that card; the site remembers that in the browser. So `opens` approximates the people who saw the price and the form, and it can be compared with the sign-ups from the home screen.

## Seeing the data

**In the Cloudflare dashboard:** on the **D1 SQL database** page, select `ai-ml-questions-waitlist` and then **Console**:

```sql
-- Sign-ups by product, language and place
SELECT product, lang, place, COUNT(*) FROM signups GROUP BY product, lang, place;

-- Sign-ups per product and week
SELECT product, strftime('%Y-%W', at) AS week, COUNT(*) FROM signups GROUP BY product, week ORDER BY week;

-- Browsers that opened each card, per day
SELECT day, product, lang, opens FROM opens ORDER BY day DESC, product;
```

**With the script:** export the database and run [`scripts/waitlist.py`](../scripts/waitlist.py) on it.

```bash
npx wrangler login                                  # once, with the Cloudflare account
npx wrangler d1 export ai-ml-questions-waitlist --remote --output waitlist.sql
python scripts/waitlist.py waitlist.sql                                       # each product, by week
python scripts/waitlist.py waitlist.sql --product interview --emails emails.csv   # one product's emails
```

`waitlist.sql` and `emails.csv` hold personal data: they are in `.gitignore` so they are not committed by mistake, and they are best deleted once used.

**Reading the numbers.** For each product, sign-ups from the home screen are compared with the browsers that opened its card; for Interview, sign-ups from the results screen are compared with the quizzes that reached the end, which come from the answers database (quizzes with 10 or more answers). The number of sign-ups that justifies building a product is best decided before looking, so it is not reinterpreted afterwards. With the traffic of October 2026, about 130 quizzes started and 27 reached 10 answers per week, so sign-ups will be few.

## Keeping the promise

The privacy page and the form promise one email when the product someone signed up for opens, with the launch price or discount, nothing else, and deleting the email six months after that product opens, or when its list closes if it never opens. Chile's data protection law, Ley 21.719, in force from December 1, 2026, asks for this kind of information and for these rights to be honored. So:

- **When a product opens:** export its emails with `--product`, write once to each person in their language, honoring the early price or discount, and six months later delete that product's rows:
  `npx wrangler d1 execute ai-ml-questions-waitlist --remote --command "DELETE FROM signups WHERE product = 'interview'"`
- **When someone asks to see or delete their email:** requests arrive at interviewquestions.iaml@gmail.com. Look it up or delete it, on every product, in the dashboard console, or with
  `npx wrangler d1 execute ai-ml-questions-waitlist --remote --command "DELETE FROM signups WHERE email = 'name@example.com'"`,
  and reply to confirm.
- **If the promise changes:** update `site/privacy.html` (both languages and their dates) and the texts of the form in `STRINGS`, in `site/app.js`.
- **Before the first sale of a product:** the privacy page covers only the free site and the waitlists, and it says so. It promises to describe what each paid product stores (the payment platform, any account or purchase records) before it opens, so that section has to be written first.

## Locally

`npx wrangler d1 migrations apply ai-ml-questions-waitlist --local` creates the tables in a local copy, and `npx wrangler dev` serves the site and the Worker with both databases. In the remote database they already exist; in a new one they are created with `--remote`.
