importScripts(
    '/uv/uv.bundle.js',
    '/uv/uv.client.js',
    '/uv/uv.config.js',
    '/uv/uv.handler.js',
    '/uv/sw.js'
);

const uv = new self.UVServiceWorker();

self.addEventListener('fetch', (event) => {
    if (uv.route(event)) {
        event.respondWith(uv.fetch(event));
    }
});
