-- The waitlist of the Interview mode, in a database of its own (ai-ml-questions-waitlist), so the
-- anonymous answers (migrations/0001_answers.sql) never sit next to personal data. The Worker
-- (worker/index.js) writes here; docs/waitlist.md explains the columns, how to see the data and
-- how long it is kept, and site/privacy.html tells the people who sign up.

-- One row per email, lowercased and trimmed by the Worker. An email already on the list is not
-- written again, and the reply is the same either way, so the form does not reveal who signed up.
CREATE TABLE IF NOT EXISTS waitlist (
  email TEXT PRIMARY KEY,
  at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')), -- when it arrived, in UTC
  lang  TEXT NOT NULL, -- en or es, the language of the site at the time
  place TEXT NOT NULL  -- home (the Interview card) or results (after a quiz)
) WITHOUT ROWID;

-- How many browsers opened the Interview card each day, per language: a count, with no email or
-- identifier. Each browser counts once (the site remembers it), so this approximates people.
CREATE TABLE IF NOT EXISTS interest (
  day   TEXT    NOT NULL, -- YYYY-MM-DD, in UTC
  lang  TEXT    NOT NULL, -- en or es
  opens INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, lang)
) WITHOUT ROWID;
