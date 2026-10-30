-- Applied once the Worker writes to signups and opens (0002): adds what reached the old tables in
-- the meantime, then drops them, so no email stays in a table nobody reads.
INSERT OR IGNORE INTO signups (email, product, at, lang, place)
  SELECT email, 'interview', at, lang, place FROM waitlist;
INSERT INTO opens (day, lang, product, opens)
  SELECT day, lang, 'interview', opens FROM interest WHERE true
  ON CONFLICT (day, lang, product) DO UPDATE SET opens = opens + excluded.opens;
DROP TABLE waitlist;
DROP TABLE interest;
