self.__uv$config = {
    prefix: '/uv/service/',
    bare: 'https://tomp.app/',
    encodeUrl: Ultraviolet.codec.xor.encode,
    decodeUrl: Ultraviolet.codec.xor.decode,
    handler: '/uv/uv.handler.js',
    bundle: '/uv/uv.bundle.js',
    config: '/uv/uv.config.js',
    sw: '/uv/sw.js',
};

// Games use their original URL directly. The Proxy tab remains separate.
if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    window.addEventListener('DOMContentLoaded', function () {
        window.openGame = function (title, url, cover = '') {
            window.currentGameData = { title, url, cover };

            const titleEl = document.getElementById('game-viewer-title');
            if (titleEl) {
                titleEl.innerHTML = `<span class="gv-game-brand">${cover ? `<img src="${cover}" alt="">` : ''}</span><span class="gv-game-title-text"><i class="fa-solid fa-gamepad"></i> ${String(title).replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span>`;
            }

            const iframe = document.getElementById('game-iframe');
            const loading = document.getElementById('game-load-status');
            const overlay = document.getElementById('game-viewer-overlay');
            if (!iframe || !overlay) return;

            if (loading) {
                loading.classList.add('show');
                const loadingTitle = loading.querySelector('.gv-loading-title');
                const loadingSub = loading.querySelector('.gv-loading-sub');
                if (loadingTitle) loadingTitle.textContent = 'Loading ' + title;
                if (loadingSub) loadingSub.textContent = 'Opening the game directly…';
            }

            overlay.style.display = 'flex';
            iframe.src = 'about:blank';
            iframe.dataset.source = url;
            iframe.src = url;

            if (loading) loading.classList.remove('show');
        };
    }, { once: true });
}
