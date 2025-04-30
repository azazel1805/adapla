const CACHE_NAME = 'personalized-learning-v1'; // Change version if you update assets
const urlsToCache = [
  '/', // Cache the root page
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  '/manifest.json'
  // Add other essential static assets if needed
];

// Install event: Cache static assets
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        // Force the waiting service worker to become the active service worker.
        return self.skipWaiting();
      })
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Tell the active service worker to take control of the page immediately.
      return self.clients.claim();
    })
  );
});

// Fetch event: Serve cached assets first, fallback to network
self.addEventListener('fetch', event => {
    // We only want to cache GET requests for our static assets
    if (event.request.method !== 'GET') {
        return;
    }

    // Strategy: Cache first for static assets defined in urlsToCache
    // For other requests (like API calls /explain), go network first.
    const requestUrl = new URL(event.request.url);

    // Check if the request is for one of the assets we explicitly cache
    const isCachableAsset = urlsToCache.includes(requestUrl.pathname) || requestUrl.pathname === '/';

    if (isCachableAsset) {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    // Cache hit - return response
                    if (response) {
                        // console.log(`Service Worker: Serving from cache: ${event.request.url}`);
                        return response;
                    }

                    // Not in cache - fetch from network, cache it, then return
                    // console.log(`Service Worker: Fetching from network: ${event.request.url}`);
                    return fetch(event.request).then(
                        networkResponse => {
                            // Check if we received a valid response
                            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
                                return networkResponse;
                            }

                            // IMPORTANT: Clone the response. A response is a stream
                            // and because we want the browser to consume the response
                            // as well as the cache consuming the response, we need
                            // to clone it so we have two streams.
                            const responseToCache = networkResponse.clone();

                            caches.open(CACHE_NAME)
                                .then(cache => {
                                    cache.put(event.request, responseToCache);
                                });

                            return networkResponse;
                        }
                    );
                }).catch(error => {
                    // Handle fetch errors, maybe serve an offline page?
                    console.error('Service Worker: Fetch error:', error);
                    // Optional: return caches.match('/offline.html');
                })
        );
    } else {
        // For non-static assets (like API calls), just fetch from network.
        // You could implement more complex strategies like Network First or Stale While Revalidate here.
        // console.log(`Service Worker: Network request (not cached): ${event.request.url}`);
        event.respondWith(fetch(event.request));
    }
});