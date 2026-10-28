// SmartVision service worker: the app opens even with a weak connection.
const CACHE = 'smartvision-v2';
const SHELL = ['./', 'index.html', 'manifest.json', 'icon-192.png', 'icon-512.png'];
const LIVE = ['nominatim.openstreetmap.org', 'routing.openstreetmap.de', 'overpass-api.de', 'tile.openstreetmap.org'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.allSettled(SHELL.map(u => c.add(u)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (LIVE.includes(url.hostname)) return;                 // maps and routes always come live
  if (req.mode === 'navigate') {                           // page: newest first, cached copy if offline
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); return r; })
      .catch(() => caches.match(req).then(r => r || caches.match('index.html'))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => {            // libraries and model files: cache first
    const net = fetch(req).then(r => { if (r && (r.ok || r.type === 'opaque')) { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); } return r; })
      .catch(() => hit);
    return hit || net;
  }));
});
