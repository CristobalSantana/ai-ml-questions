-- Several products on the waitlist: Interview, Enterprise and the online book (CONFIG.products in
-- site/app.js). The same person can ask to hear about more than one, so a sign-up is an email and a
-- product, and the count of opened cards is kept per product. The rows of 0001's tables are copied
-- as Interview, the only product they could be about; 0003 copies whatever arrived while the
-- Worker was being updated, and drops the old tables.

-- One row per email and product, lowercased and trimmed by the Worker. An email already on that
-- product's list is not written again, and the reply is the same either way.
CREATE TABLE IF NOT EXISTS signups (
  email   TEXT NOT NULL,
  product TEXT NOT NULL, -- interview, enterprise or book
  at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')), -- when it arrived, in UTC
  lang    TEXT NOT NULL, -- en or es, the language of the site at the time
  place   TEXT NOT NULL, -- home (a product's card) or results (after a quiz, Interview only)
  PRIMARY KEY (email, product)
) WITHOUT ROWID;

-- How many browsers opened each product's card each day, per language: a count, with no email or
-- identifier. Each browser counts once per product (the site remembers it).
CREATE TABLE IF NOT EXISTS opens (
  day     TEXT    NOT NULL, -- YYYY-MM-DD, in UTC
  lang    TEXT    NOT NULL, -- en or es
  product TEXT    NOT NULL, -- interview, enterprise or book
  opens   INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, lang, product)
) WITHOUT ROWID;

INSERT OR IGNORE INTO signups (email, product, at, lang, place)
  SELECT email, 'interview', at, lang, place FROM waitlist;
INSERT OR IGNORE INTO opens (day, lang, product, opens)
  SELECT day, lang, 'interview', opens FROM interest;
-- Emptied once copied, so 0003 can add exactly what the old Worker counted after this point.
DELETE FROM interest;
