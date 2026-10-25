/* Service worker: stores the site and the questions so it works offline.
   scripts/build_site.py rewrites VERSION whenever any file changes. */
const VERSION = "5d891644cb7d";
const CACHE = `ai-ml-questions-${VERSION}`;

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);
      const list = await (await fetch("precache.json", { cache: "no-store" })).json();
      await cache.addAll(list);
      await self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      for (const key of await caches.keys()) {
        if (key !== CACHE) await caches.delete(key);
      }
      await self.clients.claim();
    })(),
  );
});

/* Answers from the cache and refreshes it in the background; offline, the page keeps working. */
self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) return;

  const network = fetch(request).then(async (response) => {
    if (response.ok) {
      const copy = response.clone();
      const cache = await caches.open(CACHE);
      await cache.put(request, copy);
    }
    return response;
  });
  event.waitUntil(network.then(() => undefined, () => undefined));

  event.respondWith(
    (async () => {
      const cached = await caches.match(request, { ignoreSearch: true });
      if (cached) return cached;
      try {
        return await network;
      } catch {
        if (request.mode === "navigate") {
          const shell = await caches.match("./");
          if (shell) return shell;
        }
        return Response.error();
      }
    })(),
  );
});
