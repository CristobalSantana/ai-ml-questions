"use strict";

/* Fill these in before publishing the site. */
const CONFIG = {
  siteUrl: "https://ai-ml-questions.strangemachines.workers.dev/", // site domain, with a trailing slash
  kofiUrl: "https://ko-fi.com/strangemachines", // your Ko-fi page
  // Template for reporting mistakes; {title} and {body} are replaced. Empty hides the link.
  reportUrl: "https://github.com/CristobalSantana/ai-ml-questions/issues/new?title={title}&body={body}",
  repoUrl: "https://github.com/CristobalSantana/ai-ml-questions", // linked from the footer; empty hides the link
  ogTitle: "How much do you know about AI and machine learning?", // same as og:title in index.html
  // Where each answer is sent, anonymously, for the statistics of each question; worker/index.js
  // stores it (docs/statistics.md). Empty stops sending.
  answersUrl: "api/answers",
  // The waitlist of the Interview mode (docs/waitlist.md): where the emails go, where the count of
  // opened Interview cards goes, and the prices shown, in US$. Empty waitlistUrl hides the card and
  // the invitation; earlyPrice null shows only the full price.
  waitlistUrl: "api/waitlist",
  interestUrl: "api/interest",
  interviewPrice: 15,
  earlyPrice: 10,
  privacyUrl: "privacy", // site/privacy.html; Cloudflare serves pages without .html
  languages: ["en", "es"],
  defaultLanguage: "en",
  counts: [10, 25, 50, 100, 200],
};

const LEVELS = ["easy", "medium", "hard"];
const LETTERS = "ABCDE";
const EMOJI = { easy: "🟢", medium: "🟡", hard: "🔴" };
const KEY = {
  lang: "aiml:lang",
  prefs: "aiml:prefs",
  quiz: "aiml:quiz",
  seen: "aiml:seen",
  waitlist: "aiml:waitlist", // this browser signed up: the date, nothing else
  interest: "aiml:interest", // this browser was already counted as opening the Interview card
};
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // the same check as the Worker
const SEEN_LIMIT = 3000;
const UPDATES_SHOWN = 3; // updates on the home screen, in whole days (at least this many); older ones are folded

/* Interface text. Each language has the same keys; translating the site means editing this object. */
const STRINGS = {
  en: {
    siteName: "AI/ML Questions",
    home: "Home",
    alpha: "alpha",
    language: "Language",
    loading: "Loading questions…",
    loadError: "The questions could not be loaded. Check your connection and reload the page.",
    headline: "How much do you know about AI and machine learning?",
    purpose:
      "The main goal is to learn AI and ML concepts, from the basics to niche topics. Every option explains why it is right or wrong. Free, no sign-up.",
    difficulty: "Difficulty",
    topics: "Topics",
    all: "All",
    none: "None",
    count: "Questions",
    mode: "Mode",
    study: "Study",
    studyHint: "See the explanation after each question.",
    exam: "Exam",
    examHint: "See your score and the explanations at the end.",
    start: "Start",
    continue: "Continue",
    discard: "Discard",
    quit: "Quit",
    keys: "Shortcuts: 1–4 to choose, Enter to continue",
    next: "Next",
    finish: "See results",
    kofiFoot: "☕ Support on Ko-fi",
    githubFoot: "Open source on GitHub",
    updates: "Updates",
    olderUpdates: (n) => `Earlier updates (${n})`,
    day: (y, m, d) => `${m}/${d}/${y}`,
    privacy: "Privacy",
    interview: "Interview",
    soon: "coming soon",
    interviewHint: "Practice for machine learning job interviews.",
    interviewWhat:
      "Questions like those in an ML interview: debugging models, reading code, production and databases. Every option explains why it is right or wrong.",
    interviewPrice: (full, early) => `US$${full}, one-time payment.${early ? ` US$${early} if you sign up now.` : ""}`,
    resultsInterview: "Preparing for an ML interview? Interview mode is coming soon.",
    emailLabel: "Your email",
    emailPlaceholder: "you@example.com",
    notifyMe: "Notify me",
    waitlistPrivacy: "I will only use your email to tell you when it opens. You can ask me to delete it at any time.",
    waitlistSending: "Sending…",
    waitlistDone: "Done. I will write to you once, when it opens.",
    waitlistJoined: "You are on the list. I will write to you once, when it opens.",
    waitlistInvalid: "Check the email: it looks incomplete.",
    waitlistError: "It could not be sent. Check your connection and try again.",
    level: { easy: "Easy", medium: "Medium", hard: "Hard" },
    // The type of reasoning (Bloom's revised taxonomy), shown apart from the difficulty.
    bloom: { remember: "Remember", understand: "Understand", apply: "Apply", analyze: "Analyze", evaluate: "Evaluate" },
    bloomLabel: "Reasoning",
    bloomTitle: "Type of reasoning the question asks for, from Bloom's taxonomy",
    kind: { paper: "Paper", book: "Book", docs: "Docs", post: "Post", experiment: "Experiment", article: "Article" },
    bankSize: (n, t) => `${n} ${n === 1 ? "question" : "questions"} · ${t} ${t === 1 ? "topic" : "topics"}`,
    available: (n) => (n ? `${n} available with these filters` : "No questions match these filters"),
    allCount: (n) => `All (${n})`,
    notEnough: (n) => `Only ${n} match these filters`,
    resume: (i, n) => `You have a quiz in progress: question ${i} of ${n}.`,
    progress: (i, n) => `${i} of ${n}`,
    levelTitle: "Estimated difficulty",
    correct: "Correct.",
    wrong: (letter) => `Incorrect. The correct answer is ${letter}.`,
    explanation: "Explanation",
    sources: "Sources",
    reviewed: (date) => `Reviewed in ${date}`,
    report: "Report a mistake",
    reportTitle: (id) => `Mistake in ${id}`,
    reportBody: (prompt) => `Question: ${prompt}\n\nWhat is wrong:\n`,
    srCorrect: " (correct answer)",
    srChosen: " (your answer)",
    srRight: "Correct. ",
    srWrong: "Incorrect. ",
    yourAnswer: "Your answer",
    rightAnswer: "Correct answer",
    resultsTitle: "Result",
    pct: (p) => `${p}% correct`,
    byLevel: "By difficulty",
    byTopic: (n) => `By topic, from lowest to highest score (${n})`,
    share: "Share",
    shareLabel: "Text to share",
    shareLinkedIn: "Share on LinkedIn",
    copy: "Copy text",
    nativeShare: "Share…",
    shareHint: "LinkedIn only accepts the link, so the button copies the text for you to paste into your post.",
    copied: "Text copied. Paste it into your post.",
    copyFailed: "Couldn't copy. Select the text and copy it by hand.",
    shareScore: (n, k, pct) =>
      `I answered ${n} AI and machine learning ${n === 1 ? "question" : "questions"} and got ${k} right (${pct}%).`,
    shareTopics: (best, worst) => `Best topic: ${best}. Hardest for me: ${worst}.`,
    shareCta: (url) => `How many can you get? ${url}`,
    supportText: "Did it help? The site is free and runs on voluntary support.",
    supportCta: "☕ Buy me a coffee on Ko-fi",
    reviewWrong: (n) => `Review mistakes (${n})`,
    reviewAll: "Review answers",
    noErrors: "No mistakes. Try a harder level.",
    again: "New quiz",
    retryWrong: "Retry the mistakes",
  },
  es: {
    siteName: "Preguntas IA/ML",
    home: "Inicio",
    alpha: "alfa",
    language: "Idioma",
    loading: "Cargando preguntas…",
    loadError: "No se pudieron cargar las preguntas. Revisa la conexión y recarga la página.",
    headline: "¿Cuánto sabes sobre inteligencia artificial y machine learning?",
    purpose:
      "El objetivo principal es aprender conceptos de IA y ML, de lo básico a lo de nicho. Cada alternativa explica por qué es correcta o no. Gratis y sin registro.",
    difficulty: "Dificultad",
    topics: "Contenidos",
    all: "Todos",
    none: "Ninguno",
    count: "Preguntas",
    mode: "Modo",
    study: "Estudio",
    studyHint: "Ves la explicación después de cada pregunta.",
    exam: "Examen",
    examHint: "Ves el resultado y las explicaciones al final.",
    start: "Empezar",
    continue: "Continuar",
    discard: "Descartar",
    quit: "Salir",
    keys: "Atajos: 1–4 para elegir, Enter para seguir",
    next: "Siguiente",
    finish: "Ver resultado",
    kofiFoot: "☕ Apoyar en Ko-fi",
    githubFoot: "Código abierto en GitHub",
    updates: "Actualizaciones",
    olderUpdates: (n) => `Actualizaciones anteriores (${n})`,
    day: (y, m, d) => `${d}/${m}/${y}`,
    privacy: "Privacidad",
    interview: "Entrevista",
    soon: "próximamente",
    interviewHint: "Práctica para entrevistas de trabajo en machine learning.",
    interviewWhat:
      "Preguntas como las de una entrevista de ML: depurar modelos, leer código, producción y bases de datos. Cada alternativa explica por qué es correcta o incorrecta.",
    interviewPrice: (full, early) => `US$${full}, pago único.${early ? ` Si te anotas ahora, US$${early}.` : ""}`,
    resultsInterview: "¿Te preparas para una entrevista de ML? El modo Entrevista viene pronto.",
    emailLabel: "Tu correo",
    emailPlaceholder: "tu@correo.com",
    notifyMe: "Avísame",
    waitlistPrivacy: "Solo usaré tu correo para avisarte cuando abra. Puedes pedir que lo borre cuando quieras.",
    waitlistSending: "Enviando…",
    waitlistDone: "Listo. Te escribiré una vez, cuando abra.",
    waitlistJoined: "Ya estás en la lista. Te escribiré una vez, cuando abra.",
    waitlistInvalid: "Revisa el correo: parece incompleto.",
    waitlistError: "No se pudo enviar. Revisa la conexión e inténtalo de nuevo.",
    level: { easy: "Fácil", medium: "Medio", hard: "Difícil" },
    bloom: { remember: "Recordar", understand: "Comprender", apply: "Aplicar", analyze: "Analizar", evaluate: "Evaluar" },
    bloomLabel: "Razonamiento",
    bloomTitle: "Tipo de razonamiento que pide la pregunta, según la taxonomía de Bloom",
    kind: { paper: "Paper", book: "Libro", docs: "Docs", post: "Post", experiment: "Experimento", article: "Artículo" },
    bankSize: (n, t) => `${n} ${n === 1 ? "pregunta" : "preguntas"} · ${t} ${t === 1 ? "contenido" : "contenidos"}`,
    available: (n) =>
      n ? `${n} ${n === 1 ? "disponible" : "disponibles"} con estos filtros` : "No hay preguntas con estos filtros",
    allCount: (n) => `Todas (${n})`,
    notEnough: (n) => `Solo hay ${n} con estos filtros`,
    resume: (i, n) => `Tienes un quiz a medias: vas por la pregunta ${i} de ${n}.`,
    progress: (i, n) => `${i} de ${n}`,
    levelTitle: "Dificultad estimada",
    correct: "Correcto.",
    wrong: (letter) => `Incorrecto. La respuesta correcta es la ${letter}.`,
    explanation: "Explicación",
    sources: "Fuentes",
    reviewed: (date) => `Revisada en ${date}`,
    report: "Reportar un error",
    reportTitle: (id) => `Error en ${id}`,
    reportBody: (prompt) => `Pregunta: ${prompt}\n\nQué está mal:\n`,
    srCorrect: " (respuesta correcta)",
    srChosen: " (tu respuesta)",
    srRight: "Correcta. ",
    srWrong: "Incorrecta. ",
    yourAnswer: "Tu respuesta",
    rightAnswer: "Respuesta correcta",
    resultsTitle: "Resultado",
    pct: (p) => `${p}% de aciertos`,
    byLevel: "Por dificultad",
    byTopic: (n) => `Por contenido, de menor a mayor acierto (${n})`,
    share: "Compartir",
    shareLabel: "Texto para compartir",
    shareLinkedIn: "Compartir en LinkedIn",
    copy: "Copiar texto",
    nativeShare: "Compartir…",
    shareHint: "LinkedIn solo recibe el enlace, así que el botón copia el texto para que lo pegues en tu publicación.",
    copied: "Texto copiado. Pégalo en tu publicación.",
    copyFailed: "No se pudo copiar. Selecciona el texto y cópialo a mano.",
    shareScore: (n, k, pct) =>
      `${n === 1 ? "Respondí 1 pregunta" : `Respondí ${n} preguntas`} de IA y machine learning y acerté ${k} (${pct}%).`,
    shareTopics: (best, worst) => `En lo que mejor me fue: ${best}. Lo que más me costó: ${worst}.`,
    shareCta: (url) => `¿Cuánto sacas tú? ${url}`,
    supportText: "¿Te sirvió? El sitio es gratis y se mantiene con aportes voluntarios.",
    supportCta: "☕ Invítame un café en Ko-fi",
    reviewWrong: (n) => `Repasar errores (${n})`,
    reviewAll: "Revisar respuestas",
    noErrors: "Sin errores. Prueba con un nivel más difícil.",
    again: "Otro quiz",
    retryWrong: "Reintentar las que fallaste",
  },
};

let lang = CONFIG.defaultLanguage;
let T = STRINGS[lang];

/* Helpers */
const $ = (selector) => document.querySelector(selector);
const tx = (obj) => (obj ? obj[lang] ?? obj.en ?? Object.values(obj)[0] ?? "" : "");
const esc = (value) =>
  String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const rich = (value) => esc(value).replace(/`([^`]+)`/g, "<code>$1</code>");
const areaOf = (id) => id.replace(/-\d{4}$/, "");
const randomId = () => Array.from(crypto.getRandomValues(new Uint8Array(8)), (b) => b.toString(16).padStart(2, "0")).join("");

function shuffle(list) {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function formatMonth(isoDate) {
  const [year, month] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString(lang, { month: "long", year: "numeric" });
}

const optionOrder = (q) => (q.keep_order ? q.options.map((o) => o.id) : shuffle(q.options.map((o) => o.id)));
const shareUrl = () => CONFIG.siteUrl + (lang === CONFIG.defaultLanguage ? "" : `#${lang}`);

/* Local storage can be missing (private window, preview), so every access fails quietly. */
const store = {
  get(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* without storage, the quiz lives in memory */
    }
  },
  remove(key) {
    try {
      localStorage.removeItem(key);
    } catch {
      /* nothing to remove */
    }
  },
};

/* Data */
const bank = {
  groups: [], // topics with questions, in taxonomy order
  groupById: new Map(),
  groupOf: new Map(), // area -> topic id
  subtopicName: new Map(),
  counts: {},
  total: 0,
  updates: [], // updates.json, newest first
  questions: new Map(),
  loaded: new Set(),
};

async function getJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

async function loadMeta() {
  const [taxonomy, index] = await Promise.all([getJSON("data/taxonomy.json"), getJSON("data/index.json")]);
  bank.counts = index.counts;
  bank.total = index.total;
  bank.updates = Array.isArray(index.updates) ? index.updates : [];
  for (const area of taxonomy.areas) {
    for (const sub of area.subtopics) bank.subtopicName.set(`${area.id}/${sub.id}`, sub.name);
  }
  for (const group of taxonomy.groups) {
    const areas = group.areas.filter((a) => bank.counts[a]);
    for (const area of group.areas) bank.groupOf.set(area, group.id);
    if (!areas.length) continue;
    const topic = { ...group, areas };
    bank.groups.push(topic);
    bank.groupById.set(group.id, topic);
  }
}

async function loadAreas(ids) {
  const missing = ids.filter((id) => !bank.loaded.has(id) && bank.counts[id]);
  const lists = await Promise.all(missing.map((id) => getJSON(`data/questions/${id}.json`)));
  lists.forEach((list, i) => {
    for (const q of list) bank.questions.set(q.id, q);
    bank.loaded.add(missing[i]);
  });
}

/* Start-screen preferences */
const prefs = { levels: [...LEVELS], groups: null, count: CONFIG.counts[0], mode: "study" };

function loadPrefs() {
  const saved = store.get(KEY.prefs, {});
  if (Array.isArray(saved.levels)) prefs.levels = LEVELS.filter((l) => saved.levels.includes(l));
  if (Array.isArray(saved.groups)) {
    const ids = saved.groups.filter((id) => bank.groupById.has(id));
    prefs.groups = ids.length === bank.groups.length ? null : ids;
  }
  if (CONFIG.counts.includes(saved.count)) prefs.count = saved.count;
  if (saved.mode === "study" || saved.mode === "exam") prefs.mode = saved.mode;
}

const savePrefs = () => store.set(KEY.prefs, prefs);
const selectedGroups = () => prefs.groups ?? bank.groups.map((g) => g.id);
const areasOf = (groupIds) => groupIds.flatMap((id) => bank.groupById.get(id)?.areas ?? []);

function countFor(groupIds, levels) {
  let n = 0;
  for (const area of areasOf(groupIds)) for (const level of levels) n += bank.counts[area]?.[level] ?? 0;
  return n;
}

function countOptions(available) {
  const options = CONFIG.counts.map((n) => ({ n, value: String(n), label: String(n), disabled: n > available }));
  const max = CONFIG.counts.at(-1);
  if (available > 0 && available < max && !CONFIG.counts.includes(available)) {
    options.push({ n: available, value: "max", label: T.allCount(available), disabled: false });
  }
  return options.sort((a, b) => a.n - b.n);
}

function renderSetup() {
  const groups = selectedGroups();
  $("#levels").innerHTML = LEVELS.map((level) => {
    const on = prefs.levels.includes(level);
    return `<button type="button" class="chip" data-level="${level}" aria-pressed="${on}">
      <span class="dot ${level}" aria-hidden="true"></span>${T.level[level]}
      <span class="count">${countFor(groups, [level])}</span></button>`;
  }).join("");

  $("#topics").innerHTML = bank.groups
    .map((group) => {
      const on = groups.includes(group.id);
      return `<button type="button" class="chip" data-group="${group.id}" aria-pressed="${on}">
      <span class="tick" aria-hidden="true"></span>${esc(tx(group.name))}<span class="count">${countFor([group.id], prefs.levels)}</span></button>`;
    })
    .join("");

  const available = countFor(groups, prefs.levels);
  const effective = Math.min(prefs.count, available);
  $("#counts").innerHTML = countOptions(available)
    .map((o) => {
      const pressed = !o.disabled && o.n === effective;
      const extra = o.disabled ? ` disabled title="${esc(T.notEnough(available))}"` : "";
      return `<button type="button" class="count-opt" data-count="${o.value}" aria-pressed="${pressed}"${extra}>${o.label}</button>`;
    })
    .join("");

  $("#available").textContent = T.available(available);
  $("#start").disabled = available === 0;
  $(`#mode-${prefs.mode}`).checked = true;
  renderResume();
}

/* Updates, under the start button: one line per change, grouped by day, newest first. The most
   recent days are shown until there are UPDATES_SHOWN lines; the rest are folded, with their count. */
function renderUpdates() {
  const days = [];
  for (const update of bank.updates) {
    const text = tx(update.text);
    if (!text) continue;
    if (days.at(-1)?.date === update.date) days.at(-1).items.push(text);
    else days.push({ date: update.date, items: [text] });
  }
  let shown = 0;
  let lines = 0;
  while (shown < days.length && lines < UPDATES_SHOWN) lines += days[shown++].items.length;
  const older = days.slice(shown);
  const day = ({ date, items }) => {
    const [y, m, d] = date.split("-");
    return `<li><time datetime="${esc(date)}">${esc(T.day(y, m, d))}</time>
      <ul>${items.map((text) => `<li>${rich(text)}</li>`).join("")}</ul></li>`;
  };
  $("#updates").hidden = days.length === 0;
  $("#updates-list").innerHTML = days.slice(0, shown).map(day).join("");
  $("#updates-older").hidden = older.length === 0;
  $("#updates-older-label").textContent = T.olderUpdates(older.reduce((n, d) => n + d.items.length, 0));
  $("#updates-older-list").innerHTML = older.map(day).join("");
}

function refocus(selector) {
  const el = $(selector);
  if (el && !el.disabled) el.focus();
}

/* Quiz */
let quiz = null; // { v, mode, index, sid, items: [{ id, order, choice, first, sent }] }
let lastResult = null;

const saveQuiz = () => quiz && store.set(KEY.quiz, quiz);

function markSeen(id) {
  const seen = store.get(KEY.seen, {});
  seen[id] = Date.now();
  let entries = Object.entries(seen);
  if (entries.length > SEEN_LIMIT) entries = entries.sort((a, b) => b[1] - a[1]).slice(0, SEEN_LIMIT);
  store.set(KEY.seen, Object.fromEntries(entries));
}

/* Sends a final answer once. Only the quiz's random id, the question, the option chosen, the
   language, the mode and whether this browser had answered it before travel; the Worker stores
   no IP address. */
function sendAnswer(item) {
  // Offline it waits: in study mode it is tried again on moving on; after that the answer is lost.
  if (!CONFIG.answersUrl || item.sent || item.choice === null || navigator.onLine === false) return;
  item.sent = true;
  const q = bank.questions.get(item.id);
  const body = JSON.stringify({
    quiz: quiz.sid,
    question: q.id,
    version: q.version,
    choice: item.choice,
    lang,
    mode: quiz.mode,
    first: item.first === true,
  });
  try {
    if (!navigator.sendBeacon(CONFIG.answersUrl, body)) throw new Error("beacon refused");
  } catch {
    fetch(CONFIG.answersUrl, { method: "POST", body, keepalive: true }).catch(() => {});
  }
}

/* Easiest first: by level, then by the rubric score (0 to 8, docs/difficulty.md). A quiz that opens
   with a hard question loses most people at the first mistake. Ties keep a random order. */
const LEVEL_RANK = { easy: 0, medium: 1, hard: 2 };
const BLOOM_SCORE = { remember: 0, understand: 0, apply: 1, analyze: 2, evaluate: 2 };
const rubricScore = (q) => (BLOOM_SCORE[q.bloom] ?? 0) + Object.values(q.difficulty ?? {}).reduce((sum, x) => sum + x, 0);
const easiestFirst = (list) =>
  shuffle(list).sort((a, b) => LEVEL_RANK[a.level] - LEVEL_RANK[b.level] || rubricScore(a) - rubricScore(b));

/* Spreads the quiz across topic and level, preferring questions not seen recently. */
function stratifiedSample(pool, n, seen) {
  const groups = new Map();
  for (const q of shuffle(pool)) {
    // By area, not by topic: regrouping the topics does not change which questions come up.
    const key = `${q.area}|${q.level}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(q);
  }
  for (const list of groups.values()) list.sort((a, b) => (seen[a.id] ?? 0) - (seen[b.id] ?? 0));
  const queues = shuffle([...groups.values()]);
  const out = [];
  while (out.length < n && queues.length) {
    for (let i = 0; i < queues.length && out.length < n; ) {
      out.push(queues[i].shift());
      if (queues[i].length) i++;
      else queues.splice(i, 1);
    }
  }
  return easiestFirst(out);
}

async function startQuiz({ ids = null, mode = prefs.mode } = {}) {
  const areas = ids ? [...new Set(ids.map(areaOf))] : areasOf(selectedGroups());
  await loadAreas(areas);
  const seen = store.get(KEY.seen, {});
  let picked;
  if (ids) {
    picked = easiestFirst(ids.map((id) => bank.questions.get(id)).filter(Boolean));
  } else {
    const pool = [...bank.questions.values()].filter((q) => areas.includes(q.area) && prefs.levels.includes(q.level));
    picked = stratifiedSample(pool, Math.min(prefs.count, pool.length), seen);
  }
  if (!picked.length) return;
  quiz = {
    v: 2,
    mode,
    index: 0,
    sid: randomId(),
    items: picked.map((q) => ({ id: q.id, order: optionOrder(q), choice: null, first: !seen[q.id] })),
  };
  saveQuiz();
  showScreen("quiz");
  renderQuestion(true);
  window.scrollTo(0, 0);
}

function sourceHTML(source) {
  let label = esc(source.title);
  if (source.authors) label += ` · ${esc(source.authors)}`;
  if (source.year) label += `, ${source.year}`;
  const body = source.url ? `<a href="${esc(source.url)}" target="_blank" rel="noopener">${label}</a>` : label;
  return `<li><span class="kind">${esc(T.kind[source.kind] ?? source.kind)}</span>${body}</li>`;
}

function reportLink(q) {
  if (!CONFIG.reportUrl) return "";
  const url = CONFIG.reportUrl
    .replace("{title}", encodeURIComponent(T.reportTitle(q.id)))
    .replace("{body}", encodeURIComponent(T.reportBody(tx(q.prompt))));
  return `<a href="${esc(url)}" target="_blank" rel="noopener">${T.report}</a>`;
}

/* Difficulty and type of reasoning are shown apart: Bloom says what kind of thinking a question
   asks for, the level how many people get it right (docs/difficulty.md). */
const levelTag = (q, withTitle = false) =>
  `<span class="level-tag"${withTitle ? ` title="${T.levelTitle}"` : ""}><span class="dot ${q.level}" aria-hidden="true"></span><span class="visually-hidden">${T.difficulty}: </span>${T.level[q.level]}</span>`;
const bloomTag = (q, withTitle = false) =>
  T.bloom[q.bloom]
    ? `<span class="bloom-tag"${withTitle ? ` title="${T.bloomTitle}"` : ""}><span class="visually-hidden">${T.bloomLabel}: </span>${T.bloom[q.bloom]}</span>`
    : "";

function verdictText(q, item) {
  if (q.answer.includes(item.choice)) return T.correct;
  return T.wrong(LETTERS[item.order.indexOf(q.answer[0])]);
}

function feedbackHTML(q, item) {
  const ok = q.answer.includes(item.choice);
  const foot = [`<span>${q.id}</span>`];
  if (q.stability === "volatile") foot.push(`<span>${T.reviewed(formatMonth(q.reviewed_at))}</span>`);
  const report = reportLink(q);
  if (report) foot.push(report);
  return `<section class="feedback">
      <p class="verdict ${ok ? "ok" : "bad"}">${verdictText(q, item)}</p>
      <div class="block"><h3 class="label">${T.explanation}</h3><p>${rich(tx(q.explanation))}</p></div>
      <div class="block"><h3 class="label">${T.sources}</h3><ul class="sources">${q.sources.map(sourceHTML).join("")}</ul></div>
      <div class="q-foot">${foot.join("")}</div>
    </section>`;
}

function renderQuestion(focusPrompt) {
  const item = quiz.items[quiz.index];
  const q = bank.questions.get(item.id);
  const total = quiz.items.length;
  const answered = item.choice !== null;
  const reveal = answered && quiz.mode === "study";

  $("#progress-label").textContent = T.progress(quiz.index + 1, total);
  $("#progress-bar").style.width = `${((quiz.index + (answered ? 1 : 0)) / total) * 100}%`;

  const options = item.order
    .map((oid, i) => {
      const option = q.options.find((o) => o.id === oid);
      const chosen = item.choice === oid;
      const right = q.answer.includes(oid);
      const classes = ["option"];
      if (reveal && right) classes.push("is-correct");
      if (reveal && chosen && !right) classes.push("is-wrong");
      const mark = reveal && right ? "✓" : reveal && chosen ? "✗" : LETTERS[i];
      const sr = reveal ? (right ? T.srCorrect : chosen ? T.srChosen : "") : "";
      return `<li>
        <button type="button" class="${classes.join(" ")}" data-oid="${oid}" aria-pressed="${chosen}"${reveal ? " disabled" : ""}>
          <span class="bubble" aria-hidden="true">${mark}</span>
          <span class="option-text"><span class="visually-hidden">${LETTERS[i]}. </span>${rich(tx(option.text))}<span class="visually-hidden">${sr}</span></span>
        </button>
        ${reveal ? `<p class="rationale">${rich(tx(option.rationale))}</p>` : ""}
      </li>`;
    })
    .join("");

  const topic = bank.groupById.get(bank.groupOf.get(q.area));
  const subtopic = bank.subtopicName.get(`${q.area}/${q.subtopic}`);
  $("#question").innerHTML = `
    <div class="q-meta">
      ${levelTag(q, true)} ${bloomTag(q, true)}
      <span class="q-topic">${esc(tx(topic?.name))} · ${esc(tx(subtopic))}</span>
    </div>
    <h2 class="q-prompt" id="q-prompt" tabindex="-1">${rich(tx(q.prompt))}</h2>
    ${q.code ? `<pre class="q-code"><code>${esc(q.code.source)}</code></pre>` : ""}
    <ol class="options" aria-labelledby="q-prompt">${options}</ol>
    ${reveal ? feedbackHTML(q, item) : ""}`;

  const next = $("#next");
  next.disabled = !answered;
  next.textContent = quiz.index === total - 1 ? T.finish : T.next;
  if (focusPrompt) $("#q-prompt").focus({ preventScroll: true });
}

function choose(oid) {
  const item = quiz.items[quiz.index];
  if (quiz.mode === "study" && item.choice !== null) return;
  item.choice = oid;
  markSeen(item.id);
  if (quiz.mode === "study") sendAnswer(item); // in study mode the first choice is final
  saveQuiz();
  renderQuestion(false);
  if (quiz.mode === "study") announce(verdictText(bank.questions.get(item.id), item));
  $("#next").focus({ preventScroll: true });
}

function goNext() {
  const item = quiz.items[quiz.index];
  if (item.choice === null) return;
  sendAnswer(item); // in exam mode the choice is final on moving on
  if (quiz.index < quiz.items.length - 1) {
    quiz.index++;
    saveQuiz();
    renderQuestion(true);
    window.scrollTo(0, 0);
  } else {
    finish();
  }
}

function resumable() {
  const saved = quiz ?? store.get(KEY.quiz, null);
  const ok = saved && saved.v === 2 && Array.isArray(saved.items) && saved.items.length > 0 && saved.index < saved.items.length;
  return ok ? saved : null;
}

function renderResume() {
  const saved = resumable();
  $("#resume").hidden = !saved;
  if (saved) $("#resume-text").textContent = T.resume(saved.index + 1, saved.items.length);
}

async function resume() {
  const saved = resumable();
  if (!saved) return;
  await loadAreas([...new Set(saved.items.map((i) => areaOf(i.id)))]);
  saved.items = saved.items.filter((i) => bank.questions.has(i.id));
  saved.sid ??= randomId(); // a quiz saved before answers were sent
  for (const item of saved.items) {
    item.first ??= false;
    // If the question changed since the quiz was saved, its options are laid out again.
    const q = bank.questions.get(item.id);
    const ids = q.options.map((o) => o.id);
    if (item.order.length !== ids.length || !item.order.every((id) => ids.includes(id))) {
      item.order = optionOrder(q);
      item.choice = null;
      item.sent = false;
    }
  }
  if (!saved.items.length) {
    discardQuiz();
    return;
  }
  saved.index = Math.min(saved.index, saved.items.length - 1);
  quiz = saved;
  showScreen("quiz");
  renderQuestion(true);
  window.scrollTo(0, 0);
}

function discardQuiz() {
  quiz = null;
  store.remove(KEY.quiz);
  renderSetup();
}

/* Results */
function computeResult(qz) {
  const byLevel = Object.fromEntries(LEVELS.map((l) => [l, { n: 0, k: 0 }]));
  const topics = new Map();
  const rows = [];
  let correct = 0;
  for (const item of qz.items) {
    const q = bank.questions.get(item.id);
    const ok = q.answer.includes(item.choice);
    correct += ok ? 1 : 0;
    byLevel[q.level].n++;
    byLevel[q.level].k += ok ? 1 : 0;
    const gid = bank.groupOf.get(q.area);
    const row = topics.get(gid) ?? { id: gid, n: 0, k: 0 };
    row.n++;
    row.k += ok ? 1 : 0;
    topics.set(gid, row);
    rows.push({ item, q, ok });
  }
  const total = qz.items.length;
  return { mode: qz.mode, total, correct, pct: Math.round((100 * correct) / total), byLevel, byTopic: [...topics.values()], rows };
}

const topicName = (id) => tx(bank.groupById.get(id)?.name);

function sortedTopics(res) {
  return [...res.byTopic].sort(
    (a, b) => a.k / a.n - b.k / b.n || b.n - a.n || topicName(a.id).localeCompare(topicName(b.id), lang),
  );
}

function buildShareText(res) {
  const lines = [T.shareScore(res.total, res.correct, res.pct)];
  const levels = LEVELS.filter((l) => res.byLevel[l].n).map(
    (l) => `${EMOJI[l]} ${T.level[l]} ${res.byLevel[l].k}/${res.byLevel[l].n}`,
  );
  if (levels.length) lines.push(levels.join(" · "));
  const ranked = res.byTopic.filter((t) => t.n >= 2);
  if (ranked.length >= 2) {
    const rate = (t) => t.k / t.n;
    const best = ranked.reduce((b, t) => (rate(t) > rate(b) || (rate(t) === rate(b) && t.n > b.n) ? t : b));
    const worst = ranked.reduce((w, t) => (rate(t) < rate(w) || (rate(t) === rate(w) && t.n > w.n) ? t : w));
    if (rate(best) > rate(worst)) lines.push(T.shareTopics(topicName(best.id), topicName(worst.id)));
  }
  lines.push(T.shareCta(shareUrl()));
  return lines.join("\n");
}

function barRow(name, k, n, cls) {
  const pct = n ? Math.round((100 * k) / n) : 0;
  return `<div class="bar-row">
      <span class="name">${name}</span>
      <span class="bar ${cls}" aria-hidden="true"><span style="width:${pct}%"></span></span>
      <span class="val">${k}/${n}</span>
    </div>`;
}

function reviewItem({ item, q, ok }) {
  const letter = (oid) => LETTERS[item.order.indexOf(oid)];
  const option = (oid) => q.options.find((o) => o.id === oid);
  const chosen = option(item.choice);
  const right = option(q.answer[0]);
  return `<details>
      <summary>
        <span class="mini ${ok ? "ok" : "bad"}" aria-hidden="true">${ok ? "✓" : "✗"}</span>
        <span><span class="visually-hidden">${ok ? T.srRight : T.srWrong}</span>${rich(tx(q.prompt))}</span>
      </summary>
      <div class="body">
        ${ok ? "" : `<p><b>${T.yourAnswer}:</b> ${letter(chosen.id)}. ${rich(tx(chosen.text))}</p>`}
        <p><b>${T.rightAnswer}:</b> ${letter(right.id)}. ${rich(tx(right.text))}</p>
        <p>${rich(tx(q.explanation))}</p>
        <div class="q-foot">
          ${levelTag(q)} ${bloomTag(q)}
          <span>${q.id}</span>
        </div>
      </div>
    </details>`;
}

function renderResults(res) {
  const wrong = res.rows.filter((r) => !r.ok);
  const review = res.mode === "exam" ? [...wrong, ...res.rows.filter((r) => r.ok)] : wrong;
  const levelRows = LEVELS.filter((l) => res.byLevel[l].n)
    .map((l) => barRow(`<span class="dot ${l}" aria-hidden="true"></span>${T.level[l]}`, res.byLevel[l].k, res.byLevel[l].n, l))
    .join("");
  const topics = sortedTopics(res);
  const topicRows = topics.map((t) => barRow(esc(topicName(t.id)), t.k, t.n, "topic")).join("");
  const linkedin = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl())}`;

  $("#results").innerHTML = `
    <div>
      <h1 class="label" id="results-title" tabindex="-1">${T.resultsTitle}</h1>
      <p class="score">${res.correct}<small>/ ${res.total}</small></p>
      <p class="score-sub">${T.pct(res.pct)}</p>
    </div>

    <section class="panel" aria-labelledby="r-levels">
      <h2 class="label" id="r-levels">${T.byLevel}</h2>
      <div class="bars">${levelRows}</div>
    </section>

    <details class="topics"${topics.length <= 4 ? " open" : ""}>
      <summary><h2 class="label" id="r-topics">${T.byTopic(topics.length)}</h2></summary>
      <div class="bars">${topicRows}</div>
    </details>

    ${interviewInvite()}

    <section class="panel share" aria-labelledby="r-share">
      <h2 class="label" id="r-share">${T.share}</h2>
      <label class="visually-hidden" for="share-text">${T.shareLabel}</label>
      <textarea id="share-text" rows="5" spellcheck="false">${esc(buildShareText(res))}</textarea>
      <div class="card-preview" aria-hidden="true">
        <img src="og-image.png" alt="" width="1200" height="627" loading="lazy">
        <div><span class="domain">${esc(new URL(CONFIG.siteUrl).host)}</span><span class="title">${esc(CONFIG.ogTitle)}</span></div>
      </div>
      <div class="actions">
        <a class="btn primary" id="share-linkedin" href="${esc(linkedin)}" target="_blank" rel="noopener">${T.shareLinkedIn}</a>
        <button type="button" class="btn" id="share-copy">${T.copy}</button>
        <button type="button" class="btn" id="share-native" hidden>${T.nativeShare}</button>
      </div>
      <p class="hint">${T.shareHint}</p>
    </section>

    <section class="support" aria-label="Ko-fi">
      <p>${T.supportText}</p>
      <a class="btn" href="${esc(CONFIG.kofiUrl)}" target="_blank" rel="noopener">${T.supportCta}</a>
    </section>

    <section class="panel review" aria-labelledby="r-review">
      <h2 class="label" id="r-review">${res.mode === "exam" ? T.reviewAll : T.reviewWrong(wrong.length)}</h2>
      ${review.length ? review.map(reviewItem).join("") : `<p class="hint">${T.noErrors}</p>`}
    </section>

    <div class="actions">
      <button type="button" class="btn primary" id="again">${T.again}</button>
      ${wrong.length ? `<button type="button" class="btn" id="retry-wrong">${T.retryWrong}</button>` : ""}
    </div>`;

  if (typeof navigator.share === "function") $("#share-native").hidden = false;
}

function finish() {
  lastResult = computeResult(quiz);
  quiz = null;
  store.remove(KEY.quiz);
  renderResults(lastResult);
  showScreen("results");
  window.scrollTo(0, 0);
  $("#results-title").focus({ preventScroll: true });
}

/* Waitlist of the Interview mode (docs/waitlist.md). The email goes to the Worker and the browser
   only remembers that it signed up; the reply is the same whether or not the email was already
   on the list. */
const joined = () => Boolean(store.get(KEY.waitlist, null));
const privacyHref = () => `${CONFIG.privacyUrl}#${lang}`;

/* The fields belong to an empty form outside (#waitlist-home, #waitlist-results) through their
   form attribute, because the home card sits inside the setup form and forms cannot nest. */
function waitlistFields(place) {
  const form = `waitlist-${place}`;
  return `<div class="waitlist-row">
      <label class="visually-hidden" for="${form}-email">${T.emailLabel}</label>
      <input type="email" id="${form}-email" name="email" form="${form}" autocomplete="email" inputmode="email" maxlength="254" placeholder="${esc(T.emailPlaceholder)}" required>
      <button type="submit" class="btn primary" form="${form}">${T.notifyMe}</button>
    </div>
    <div class="hp" aria-hidden="true"><label>Website <input type="text" name="website" form="${form}" tabindex="-1" autocomplete="off"></label></div>
    <p class="hint">${T.waitlistPrivacy} <a href="${esc(privacyHref())}">${T.privacy}</a></p>
    <p class="waitlist-status" id="${form}-status" role="status"></p>`;
}

const priceLine = () => T.interviewPrice(CONFIG.interviewPrice, CONFIG.earlyPrice);

function renderInterview() {
  $("#interview").hidden = !CONFIG.waitlistUrl;
  const typed = $("#waitlist-home-email")?.value ?? "";
  $("#interview-panel").innerHTML = joined()
    ? `<p class="waitlist-done">${T.waitlistJoined}</p>`
    : `<p>${T.interviewWhat}</p><p class="price">${priceLine()}</p>${waitlistFields("home")}`;
  const input = $("#waitlist-home-email");
  if (input) input.value = typed; // switching the language keeps what was typed
}

/* On the results screen, under the score, unless this browser already signed up. */
function interviewInvite() {
  if (!CONFIG.waitlistUrl || joined()) return "";
  return `<section class="panel invite" id="r-interview" aria-labelledby="r-interview-title">
      <h2 class="label" id="r-interview-title">${T.interview} · ${T.soon}</h2>
      <p>${T.resultsInterview} ${priceLine()}</p>
      <form id="waitlist-results" data-waitlist="results" novalidate></form>
      ${waitlistFields("results")}
    </section>`;
}

function toggleInterview() {
  const button = $("#interview-toggle");
  const open = button.getAttribute("aria-expanded") !== "true";
  button.setAttribute("aria-expanded", String(open));
  $("#interview-panel").hidden = !open;
  if (open) countInterest();
}

/* One count per browser, the first time it opens the Interview card: the language and nothing else. */
function countInterest() {
  if (!CONFIG.interestUrl || store.get(KEY.interest, null) || navigator.onLine === false) return;
  store.set(KEY.interest, new Date().toISOString().slice(0, 10));
  const body = JSON.stringify({ lang });
  try {
    if (!navigator.sendBeacon(CONFIG.interestUrl, body)) throw new Error("beacon refused");
  } catch {
    fetch(CONFIG.interestUrl, { method: "POST", body, keepalive: true }).catch(() => {});
  }
}

async function joinWaitlist(form) {
  const place = form.dataset.waitlist;
  const fields = [...form.elements];
  const input = fields.find((el) => el.name === "email");
  const button = fields.find((el) => el.type === "submit");
  const status = $(`#waitlist-${place}-status`);
  const email = input.value.trim();
  if (!EMAIL.test(email) || email.length > 254) {
    input.setAttribute("aria-invalid", "true");
    status.textContent = T.waitlistInvalid;
    input.focus();
    return;
  }
  input.removeAttribute("aria-invalid");
  button.disabled = true;
  status.textContent = T.waitlistSending;
  try {
    const website = fields.find((el) => el.name === "website")?.value ?? "";
    const res = await fetch(CONFIG.waitlistUrl, { method: "POST", body: JSON.stringify({ email, lang, place, website }) });
    if (res.status === 400) {
      input.setAttribute("aria-invalid", "true");
      status.textContent = T.waitlistInvalid;
      button.disabled = false;
      return;
    }
    if (!res.ok) throw new Error(String(res.status));
  } catch {
    status.textContent = T.waitlistError;
    button.disabled = false;
    return;
  }
  store.set(KEY.waitlist, new Date().toISOString().slice(0, 10));
  const done = `<p class="waitlist-done">${T.waitlistDone}</p>`;
  if (place === "results") {
    $("#r-interview").innerHTML = done;
    renderInterview(); // the home card no longer asks
  } else {
    $("#interview-panel").innerHTML = done;
  }
  announce(T.waitlistDone);
}

/* Sharing and notices */
function announce(message) {
  // Cleared first so a screen reader repeats a message identical to the previous one.
  const el = $("#announcer");
  el.textContent = "";
  requestAnimationFrame(() => {
    el.textContent = message;
  });
}

let toastTimer = 0;
function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.hidden = true;
  }, 3500);
}

async function copyShareText() {
  const area = $("#share-text");
  try {
    await navigator.clipboard.writeText(area.value);
    toast(T.copied);
  } catch {
    area.focus();
    area.select();
    toast(T.copyFailed);
  }
}

async function nativeShare() {
  try {
    await navigator.share({ title: T.siteName, text: $("#share-text").value });
  } catch (err) {
    if (err?.name !== "AbortError") copyShareText();
  }
}

/* Language */
function applyStaticText() {
  document.documentElement.lang = lang;
  document.title = T.siteName;
  for (const el of document.querySelectorAll("[data-i18n]")) el.textContent = T[el.dataset.i18n];
  for (const el of document.querySelectorAll("[data-i18n-aria]")) el.setAttribute("aria-label", T[el.dataset.i18nAria]);
  for (const button of document.querySelectorAll("[data-lang]")) button.setAttribute("aria-pressed", String(button.dataset.lang === lang));
  $("#brand").title = T.home;
  $("#kofi-foot").href = CONFIG.kofiUrl;
  $("#github-foot").href = CONFIG.repoUrl;
  $("#github-foot").hidden = !CONFIG.repoUrl;
  $("#privacy-foot").href = privacyHref();
  renderInterview();
  // Before the data arrives, the counts written into index.html by build_site.py keep the header from changing size.
  const size = $("#bank-size");
  const total = bank.total || Number(size.dataset.total);
  if (total) size.textContent = T.bankSize(total, bank.groups.length || Number(size.dataset.topics));
  renderUpdates();
}

function setLanguage(next, { save = true } = {}) {
  if (!CONFIG.languages.includes(next)) return;
  lang = next;
  T = STRINGS[lang];
  if (save) store.set(KEY.lang, lang);
  try {
    if (/^#(en|es)$/.test(location.hash)) history.replaceState(null, "", `#${lang}`);
  } catch {
    /* the frame does not allow changing the address */
  }
  applyStaticText();
  if (!$("#screen-setup").hidden) renderSetup();
  if (!$("#screen-quiz").hidden && quiz) renderQuestion(false);
  if (!$("#screen-results").hidden && lastResult) renderResults(lastResult);
}

function initialLanguage() {
  const fromHash = location.hash.replace("#", "");
  if (CONFIG.languages.includes(fromHash)) return fromHash;
  const saved = store.get(KEY.lang, null);
  return CONFIG.languages.includes(saved) ? saved : CONFIG.defaultLanguage;
}

/* Screens and events */
function showScreen(name) {
  for (const screen of ["setup", "quiz", "results"]) $(`#screen-${screen}`).hidden = screen !== name;
  $("#status").hidden = true;
}

function goHome() {
  saveQuiz();
  renderSetup();
  showScreen("setup");
  window.scrollTo(0, 0);
}

function wireEvents() {
  $("#brand").addEventListener("click", (e) => {
    e.preventDefault();
    goHome();
  });

  for (const button of document.querySelectorAll("[data-lang]")) {
    button.addEventListener("click", () => setLanguage(button.dataset.lang));
  }

  $("#levels").addEventListener("click", (e) => {
    const chip = e.target.closest("[data-level]");
    if (!chip) return;
    const level = chip.dataset.level;
    const on = prefs.levels.includes(level);
    prefs.levels = LEVELS.filter((l) => (l === level ? !on : prefs.levels.includes(l)));
    savePrefs();
    renderSetup();
    refocus(`[data-level="${level}"]`);
  });

  $("#topics").addEventListener("click", (e) => {
    const chip = e.target.closest("[data-group]");
    if (!chip) return;
    const id = chip.dataset.group;
    const current = selectedGroups();
    const next = current.includes(id) ? current.filter((g) => g !== id) : [...current, id];
    prefs.groups = next.length === bank.groups.length ? null : bank.groups.map((g) => g.id).filter((g) => next.includes(g));
    savePrefs();
    renderSetup();
    refocus(`[data-group="${id}"]`);
  });

  $("#topics-all").addEventListener("click", () => {
    prefs.groups = null;
    savePrefs();
    renderSetup();
  });

  $("#topics-none").addEventListener("click", () => {
    prefs.groups = [];
    savePrefs();
    renderSetup();
  });

  $("#counts").addEventListener("click", (e) => {
    const option = e.target.closest("[data-count]");
    if (!option || option.disabled) return;
    const value = option.dataset.count;
    prefs.count = value === "max" ? CONFIG.counts.at(-1) : Number(value);
    savePrefs();
    renderSetup();
    refocus(`[data-count="${value}"]`);
  });

  for (const input of document.querySelectorAll('input[name="mode"]')) {
    input.addEventListener("change", () => {
      prefs.mode = input.value;
      savePrefs();
    });
  }

  $("#setup").addEventListener("submit", (e) => {
    e.preventDefault();
    startQuiz();
  });

  $("#resume-go").addEventListener("click", resume);
  $("#resume-drop").addEventListener("click", discardQuiz);

  $("#interview-toggle").addEventListener("click", toggleInterview);
  // The waitlist forms on the home screen and on the results screen.
  document.addEventListener("submit", (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement) || !form.dataset.waitlist) return;
    e.preventDefault();
    joinWaitlist(form);
  });

  $("#question").addEventListener("click", (e) => {
    const option = e.target.closest(".option");
    if (option && !option.disabled) choose(option.dataset.oid);
  });

  $("#next").addEventListener("click", goNext);
  $("#quit").addEventListener("click", goHome);

  document.addEventListener("keydown", (e) => {
    if ($("#screen-quiz").hidden || !quiz || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
    const item = quiz.items[quiz.index];
    const key = e.key.toLowerCase();
    let i = "12345".indexOf(key);
    if (i < 0) i = "abcde".indexOf(key);
    if (key.length === 1 && i >= 0 && i < item.order.length) {
      e.preventDefault();
      choose(item.order[i]);
    } else if (e.key === "Enter" && !(e.target instanceof HTMLButtonElement) && !$("#next").disabled) {
      e.preventDefault();
      goNext();
    }
  });

  $("#results").addEventListener("click", (e) => {
    const target = e.target.closest("a, button");
    if (!target) return;
    if (target.id === "share-linkedin") copyShareText(); // the link still opens
    else if (target.id === "share-copy") copyShareText();
    else if (target.id === "share-native") nativeShare();
    else if (target.id === "again") goHome();
    else if (target.id === "retry-wrong" && lastResult) {
      startQuiz({ ids: lastResult.rows.filter((r) => !r.ok).map((r) => r.q.id), mode: lastResult.mode });
    }
  });
}

function registerServiceWorker() {
  try {
    if (!window.isSecureContext || !("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("sw.js").catch(() => {});
  } catch {
    /* this environment does not allow service workers */
  }
}

async function boot() {
  setLanguage(initialLanguage(), { save: false });
  try {
    await loadMeta();
  } catch {
    $("#status").textContent = T.loadError;
    return;
  }
  loadPrefs();
  applyStaticText();
  wireEvents();
  renderSetup();
  showScreen("setup");
  registerServiceWorker();
}

boot();
