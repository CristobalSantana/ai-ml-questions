-- One row per answered question. The site sends it (site/app.js) and the Worker stores it
-- (worker/index.js). No IP address, cookie or user identifier is stored; docs/statistics.md
-- explains each column and how the statistics are computed.
--
-- There are no indexes on purpose: each one would add a row written per answer, and the
-- statistics read the whole table anyway.
CREATE TABLE IF NOT EXISTS answers (
  id       INTEGER PRIMARY KEY,
  at       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')), -- when it arrived, in UTC
  quiz     TEXT    NOT NULL, -- random id the browser makes for one quiz; the next quiz gets another
  question TEXT    NOT NULL, -- question id, such as retrieval-0005
  version  INTEGER NOT NULL, -- version of the question that was shown
  choice   TEXT    NOT NULL, -- id of the chosen option in the bank, not its position on screen
  correct  INTEGER NOT NULL, -- 1 if the choice is the key; the Worker works it out, not the browser
  lang     TEXT    NOT NULL, -- en or es
  mode     TEXT    NOT NULL, -- study or exam
  first    INTEGER NOT NULL  -- 1 if this browser had never answered the question before
);
