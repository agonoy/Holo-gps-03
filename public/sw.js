const APP_CACHE = 'holo-gps-03-app-v1';
const TILE_CACHE_PREFIX = 'holo-gps-03-oahu-tiles';
const TILE_CACHE_VERSION = 'v2';

const OAHU_BOUNDS = {
  north: 21.78,
  south: 21.22,
  west: -158.33,
  east: -157.58,
};

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(APP_CACHE);
    await cache.addAll(['./', './index.html']);
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    await self.clients.claim();
  })());
});

function latLonToTile(lat, lon, zoom) {
  const latRad = (lat * Math.PI) / 180;
  const n = Math.pow(2, zoom);
  const x = Math.floor(((lon + 180) / 360) * n);
  const y = Math.floor(((1 - Math.log(Math.tan(latRad) + 1 / Math.cos(latRad)) / Math.PI) / 2) * n);
  return { x, y };
}

function buildOahuTileUrls(minZoom, maxZoom) {
  const urls = [];

  for (let z = minZoom; z <= maxZoom; z += 1) {
    const topLeft = latLonToTile(OAHU_BOUNDS.north, OAHU_BOUNDS.west, z);
    const bottomRight = latLonToTile(OAHU_BOUNDS.south, OAHU_BOUNDS.east, z);

    for (let x = topLeft.x; x <= bottomRight.x; x += 1) {
      for (let y = topLeft.y; y <= bottomRight.y; y += 1) {
        urls.push(`https://tile.openstreetmap.org/${z}/${x}/${y}.png`);
      }
    }
  }

  return urls;
}

async function broadcast(payload) {
  const clients = await self.clients.matchAll({ includeUncontrolled: true, type: 'window' });
  for (const client of clients) {
    client.postMessage(payload);
  }
}

function buildCacheName(minZoom, maxZoom) {
  return `${TILE_CACHE_PREFIX}-z${minZoom}-z${maxZoom}-${TILE_CACHE_VERSION}`;
}

async function getAllTileCacheNames() {
  const keys = await caches.keys();
  return keys.filter((key) => key.startsWith(`${TILE_CACHE_PREFIX}-`));
}

async function downloadOahuPack(minZoom, maxZoom) {
  try {
    const cacheName = buildCacheName(minZoom, maxZoom);
    const cache = await caches.open(cacheName);
    const urls = buildOahuTileUrls(minZoom, maxZoom);
    const total = urls.length;
    let done = 0;

    await broadcast({ type: 'OFFLINE_PACK_STARTED', total, minZoom, maxZoom, cacheName });

    for (const url of urls) {
      const cached = await cache.match(url);
      if (!cached) {
        const response = await fetch(url, { mode: 'no-cors', cache: 'no-store' });
        await cache.put(url, response);
      }

      done += 1;
      if (done % 20 === 0 || done === total) {
        await broadcast({ type: 'OFFLINE_PACK_PROGRESS', done, total, minZoom, maxZoom, cacheName });
      }
    }

    await broadcast({ type: 'OFFLINE_PACK_READY', done, total, minZoom, maxZoom, cacheName });
  } catch (error) {
    await broadcast({ type: 'OFFLINE_PACK_ERROR', message: String(error), minZoom, maxZoom });
  }
}

async function clearOahuPack() {
  const tileCaches = await getAllTileCacheNames();
  await Promise.all(tileCaches.map((name) => caches.delete(name)));
  await broadcast({ type: 'OFFLINE_PACK_CLEARED', clearedCaches: tileCaches.length });
}

self.addEventListener('message', (event) => {
  const data = event.data || {};

  if (data.type === 'DOWNLOAD_OAHU_PACK') {
    const minZoom = Number.isInteger(data.minZoom) ? data.minZoom : 11;
    const maxZoom = Number.isInteger(data.maxZoom) ? data.maxZoom : 14;
    event.waitUntil(downloadOahuPack(minZoom, maxZoom));
  }

  if (data.type === 'CLEAR_OAHU_PACK') {
    event.waitUntil(clearOahuPack());
  }
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  const isOsmTile = url.hostname === 'tile.openstreetmap.org' && request.destination === 'image';

  if (isOsmTile) {
    event.respondWith((async () => {
      const tileCaches = await getAllTileCacheNames();
      for (const cacheName of tileCaches) {
        const cache = await caches.open(cacheName);
        const cachedInPack = await cache.match(request);
        if (cachedInPack) {
          return cachedInPack;
        }
      }

      const writeThroughCacheName = buildCacheName(11, 14);
      const writeThroughCache = await caches.open(writeThroughCacheName);

      try {
        const response = await fetch(request);
        await writeThroughCache.put(request, response.clone());
        return response;
      } catch (_error) {
        return new Response('', { status: 504, statusText: 'Offline tile unavailable' });
      }
    })());
    return;
  }

  const isAppRequest = request.mode === 'navigate';
  if (isAppRequest) {
    event.respondWith((async () => {
      const cache = await caches.open(APP_CACHE);
      try {
        const response = await fetch(request);
        await cache.put(request, response.clone());
        return response;
      } catch (_error) {
        const cached = await cache.match(request);
        if (cached) {
          return cached;
        }
        const fallback = await cache.match('./index.html');
        return fallback || new Response('Offline', { status: 503 });
      }
    })());
  }
});