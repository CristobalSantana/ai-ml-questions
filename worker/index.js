/* Cloudflare Worker for AI/ML Questions.

   Cloudflare serves the files in site/ before this code runs, so it only receives requests that
   match no file. The one it handles is POST /api/answers: the site sends each answer there and the
   Worker stores it in D1 (migrations/0001_answers.sql), anonymously, for the statistics of each
   question (docs/statistics.md). It stores no IP address and sets no cookie. */

const ANSWERS_PATH = "/api/answers";
const MAX_LENGTH = 1024;
const QUESTION_ID = /^[a-z0-9]+(?:-[a-z0-9]+)*-\d{4}$/;
const QUIZ_ID = /^[0-9a-f]{16}$/;
const LANGUAGES = new Set(["en", "es"]);
const MODES = new Set(["study", "exam"]);

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

const reply = (status, headers) => new Response(null, { status, headers });

async function saveAnswer(request, env) {
  const { origin } = new URL(request.url);
  const from = request.headers.get("Origin");
  if (from && from !== origin) return reply(403);
  if (Number(request.headers.get("Content-Length") ?? 0) > MAX_LENGTH) return reply(413);
  const text = await request.text();
  if (text.length > MAX_LENGTH) return reply(413);

  let answer;
  try {
    answer = JSON.parse(text);
  } catch {
    return reply(400);
  }
  const { quiz, question, version, choice, lang, mode, first } = answer ?? {};
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
  const q = await findQuestion(question, env, origin);
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

export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname !== ANSWERS_PATH) return env.ASSETS.fetch(request);
    if (request.method !== "POST") return reply(405, { Allow: "POST" });
    try {
      return await saveAnswer(request, env);
    } catch (err) {
      // For example, the free plan's daily D1 limit: the site keeps working, the answer is lost.
      console.error(`Answer not saved: ${err?.message ?? err}`);
      return reply(503);
    }
  },
};
