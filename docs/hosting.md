# Hosting

Where the questions live, how the site is built and published, and how visits are counted.

## Where the questions live

**The questions need no Supabase, Firebase or database.** They are read-only content that changes when you publish, so they live as JSON in this repository, with change history and review by pull request, and the site serves them as static files.

- **Size, measured with the current 103 questions:** about 3.5 KB per question as minified JSON with both languages, and 1.2 KB compressed with gzip. 2,000 questions come to about 7 MB, or 2.5 MB compressed: about 150 KB compressed per area. With one file per area, the browser downloads only the chosen areas.
- **Offline use:** on the first visit, the service worker stores every question so the site works offline. With 2,000 questions that would be about 2.5 MB compressed. If that is too heavy for phones, `build_site.py` can write one file per language, which halves the size, or the service worker can store each area only when it is requested.
- **Hosting:** Cloudflare (Workers with static assets, or Pages) or GitHub Pages. On Cloudflare, requests for static assets are free and unlimited.
- **Accepted trade-off:** the answers travel to the browser, so anyone who opens the developer tools can see them. On a practice site without rankings this does not matter: cheating only hurts the cheater.

## When a backend is needed

| Need | Why | Option |
|---|---|---|
| Calibrating difficulty with real data | Right and wrong answers must be stored per question | Cloudflare Worker + D1, in use since October 2026 ([Statistics](statistics.md)) |
| Reporting mistakes from the site | A form that stores the report | Worker + D1, or no backend: a link that opens a GitHub issue (the current solution) |
| Rankings or certificates | Answers must be graded on the server so nobody can cheat | Worker + D1 |
| Accounts and progress across devices | Authentication is needed | Supabase (Postgres and Auth) |

**Recommendation: Cloudflare D1**, because it lives next to the hosting. Its free plan gives 5 million rows read and 100,000 rows written per day, with 5 GB of storage; since September 1, 2026, once the daily limit is reached, queries fail until midnight UTC, which is acceptable for statistics. Supabase's free plan gives 500 MB per project and pauses projects after a week without activity, which complicates a site with sporadic traffic. Firebase offers nothing this project needs.

The statistics store, for each answer, the question and its version, the chosen option, whether it was correct, the date, the language, the mode, a random id per quiz and whether it was a first attempt, with no IP addresses or user identifiers ([Statistics](statistics.md#what-is-recorded)).

## Building and testing

```bash
pip install jsonschema
python scripts/validate.py                    # checks the bank and prints a summary
python scripts/build_site.py                  # reviewed questions only
python scripts/build_site.py --include-drafts # drafts too
python -m http.server 8000 --directory site   # open http://localhost:8000
python scripts/make_assets.py                 # icons and og-image.png (pip install playwright)
```

The service worker only works on `localhost` or over HTTPS. `http.server` serves only files, so each answer the site sends ends in a 501 error in the browser console, which does no harm. To try the Worker as well, `npx wrangler dev` serves the site and the Worker together with a local database ([Statistics](statistics.md#seeing-the-data)).

Before each push that changes questions or the site, regenerate `site/data` and the service worker version. While the questions are still drafts (`llm_draft`), the site is published with `python scripts/build_site.py --include-drafts`; once they are reviewed, without that option.

## Publishing on Cloudflare

The site is published as a Cloudflare Worker called `ai-ml-questions`, connected to the repository through Workers Builds. [`wrangler.jsonc`](../wrangler.jsonc) tells it to publish the `site/` folder as is, as static files, with no build step, because `site/data` is already generated in the repository. Cloudflare serves those files without running any code; only the requests that match no file reach [`worker/index.js`](../worker/index.js), which stores the answers in the D1 database `ai-ml-questions` (the `DB` binding).

- Every push to `main` republishes the site on its own; the status of each deployment is in the Cloudflare dashboard, under the Worker, in the **Deployments** or **Builds** tab.
- The `name` in `wrangler.jsonc` must match the Worker's name in the dashboard.
- The public address is https://ai-ml-questions.strangemachines.workers.dev/. If it changes, or if a custom domain is added under **Domains & Routes**, update `CONFIG.siteUrl` in `site/app.js` and the `og:url` and `og:image` tags in `site/index.html`, because LinkedIn needs absolute URLs.

`CONFIG` in `site/app.js` also holds the Ko-fi page (`kofiUrl`), the repository linked from the footer (`repoUrl`) and the link for reporting mistakes (`reportUrl`), which opens an issue in the repository. The repository's "Sponsor" button comes from [`.github/FUNDING.yml`](../.github/FUNDING.yml) and appears once Sponsorships is enabled in the repository's Settings → General → Features.

## Visits

The site counts visits with Cloudflare Web Analytics: the `beacon.min.js` script at the end of `site/index.html`, with the site's token. It uses no cookies and does not identify visitors, so no cookie banner is needed. The numbers (visits, page views, countries, where people come from and load speed) are in the Cloudflare dashboard under **Analytics & Logs → Web Analytics**. Ad blockers often block the script, so the numbers come out somewhat below the real ones. The service worker does not intercept those requests because they go to another domain.
