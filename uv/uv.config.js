const localHost = location.hostname === '127.0.0.1' || location.hostname === 'localhost' || location.hostname === '::1';

self.__uv$config = {
    prefix: '/uv/service/',
    bare: localHost ? '/bare/' : 'https://tomp.app/',
    encodeUrl: Ultraviolet.codec.xor.encode,
    decodeUrl: Ultraviolet.codec.xor.decode,
    handler: '/uv/uv.handler.js',
    bundle: '/uv/uv.bundle.js',
    config: '/uv/uv.config.js',
    sw: '/uv/sw.js',
};
