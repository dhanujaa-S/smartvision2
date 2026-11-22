// SmartVision service worker: after one visit with internet, detection works offline.
const CACHE = 'smartvision-v6';
const SHELL = ['./', 'index.html', 'manifest.json', 'icon-192.png', 'icon-512.png',
  'leaflet.js', 'leaflet.css',
  'ort.wasm.min.js', 'ort-wasm-simd-threaded.mjs', 'ort-wasm-simd-threaded.wasm', 'sv_model.onnx', 'sv_coco.onnx'];
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
  if (req.mode === 'navigate') {                           // page: cached copy first, so it opens with no internet
    e.respondWith(caches.match('index.html').then(hit => {
      const net = fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put('index.html', c)); return r; });
      return hit ? (net.catch(() => {}), hit) : net;
    }));
    return;
  }
  // libraries and model files: cache only, no re-download (saves data and battery)
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    if (r && r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); }
    return r;
  })));
});
