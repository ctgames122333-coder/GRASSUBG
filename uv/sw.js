// Proxy backend temporarily disabled.
// This service worker intentionally does not intercept requests.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));
