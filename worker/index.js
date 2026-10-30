/* Cloudflare Worker for AI/ML Questions.

   Cloudflare serves the files in site/ before this code runs, so it only receives requests that
   match no file. It handles three, all POST:

   - /api/answers: each answer, stored anonymously in D1 (migrations/0001_answers.sql) for the
     statistics of each question (docs/statistics.md).
   - /api/waitlist: an email for the waitlist of a product coming soon (Interview, Enterprise or
     the online book), stored in a database of its own (migrations-waitlist/), apart from the
     answers (docs/waitlist.md).
   - /api/interest: one more browser that opened a product's card today, as a bare count.

   It stores no IP address and sets no cookie. */

const MAX_LENGTH = 1024;
const QUESTION_ID = /^[a-z0-9]+(?:-[a-z0-9]+)*-\d{4}$/;
const QUIZ_ID = /^[0-9a-f]{16}$/;
const LANGUAGES = new Set(["en", "es"]);
const MODES = new Set(["study", "exam"]);
const PLACES = new Set(["home", "results"]);
const PRODUCTS = new Set(["interview", "enterprise", "book"]); // CONFIG.products in site/app.js
// Something, an @ and a domain with a dot. Whether the address works shows when the product opens.
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MAX_EMAIL = 254;

const reply = (status, headers) => new Response(null, { status, headers });

/* What every request must be: from this site, small and JSON. Returns the body, or the Response to
   send back instead. */
async function readBody(request) {
  const { origin } = new URL(request.url);
  const from = request.headers.get("Origin");
  if (from && from !== origin) return reply(403);
  if (Number(request.headers.get("Content-Length") ?? 0) > MAX_LENGTH) return reply(413);
  const text = await request.text();
  if (text.length > MAX_LENGTH) return reply(413);
  try {
    const body = JSON.parse(text);
    return body && typeof body === "object" ? body : reply(400);
  } catch {
    return reply(400);
  }
}

/* The published questions of each area, read once per isolate from the site's own files. The
   Worker checks every answer against them and works out whether it is correct itself. */
const areas = new Map();

async function findQuestion(id, env, origin) {
  const area = id.replace(/-\d{4}$/, "");
  let questions = areas.get(area);
  if (!questions) {
    const res = await env.ASSETS.fetch(`${origin}/data/questions/${area}.json`);
    if (!res.ok) return null;
    questions = new Map((await res.json()).map((q) => [q.id, q]));
    areas.set(area, questions);
  }
  return questions.get(id) ?? null;
}

async function saveAnswer(request, env) {
  const answer = await readBody(request);
  if (answer instanceof Response) return answer;
  const { quiz, question, version, choice, lang, mode, first } = answer;
  const wellFormed =
    typeof quiz === "string" && QUIZ_ID.test(quiz) &&
    typeof question === "string" && QUESTION_ID.test(question) &&
    Number.isInteger(version) &&
    typeof choice === "string" &&
    LANGUAGES.has(lang) &&
    MODES.has(mode) &&
    typeof first === "boolean";
  if (!wellFormed) return reply(400);

  // Only questions with one correct option: the site has no other kind yet.
  const q = await findQuestion(question, env, new URL(request.url).origin);
  if (!q || q.format !== "single" || !q.options.some((o) => o.id === choice)) return reply(422);
  // A page opened before the question changed: its answer belongs to a version that is gone.
  if (version !== q.version) return reply(409);

  await env.DB.prepare(
    "INSERT INTO answers (quiz, question, version, choice, correct, lang, mode, first) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
  )
    .bind(quiz, question, version, choice, q.answer.includes(choice) ? 1 : 0, lang, mode, first ? 1 : 0)
    .run();
  return reply(204);
}

async function joinWaitlist(request, env) {
  const body = await readBody(request);
  if (body instanceof Response) return body;
  // A page cached from before there were several products sends no product: it meant Interview.
  const { email, lang, place, website, product = "interview" } = body;
  // A field people do not see, which only bots fill in. They get the same reply as everyone.
  if (website) return reply(204);
  const address = typeof email === "string" ? email.trim().toLowerCase() : "";
  if (address.length > MAX_EMAIL || !EMAIL.test(address) || !LANGUAGES.has(lang) || !PLACES.has(place) || !PRODUCTS.has(product)) return reply(400);
  // An email already on that product's list stays as it was, and the reply does not change, so the
  // form cannot be used to find out whether someone signed up.
  await env.WAITLIST.prepare(
    "INSERT INTO signups (email, product, lang, place) VALUES (?, ?, ?, ?) ON CONFLICT (email, product) DO NOTHING",
  )
    .bind(address, product, lang, place)
    .run();
  return reply(204);
}

async function countInterest(request, env) {
  const body = await readBody(request);
  if (body instanceof Response) return body;
  const product = body.product ?? "interview";
  if (!LANGUAGES.has(body.lang) || !PRODUCTS.has(product)) return reply(400);
  await env.WAITLIST.prepare(
    "INSERT INTO opens (day, lang, product, opens) VALUES (strftime('%Y-%m-%d', 'now'), ?, ?, 1) ON CONFLICT (day, lang, product) DO UPDATE SET opens = opens + 1",
  )
    .bind(body.lang, product)
    .run();
  return reply(204);
}

const ROUTES = new Map([
  ["/api/answers", saveAnswer],
  ["/api/waitlist", joinWaitlist],
  ["/api/interest", countInterest],
]);

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    const handle = ROUTES.get(path);
    if (!handle) return env.ASSETS.fetch(request);
    if (request.method !== "POST") return reply(405, { Allow: "POST" });
    try {
      return await handle(request, env);
    } catch (err) {
      // For example, the free plan's daily D1 limit: the site keeps working, this request is lost.
      // The message never includes what was sent, so no email ends up in the logs.
      console.error(`${path} not saved: ${err?.message ?? err}`);
      return reply(503);
    }
  },
};
