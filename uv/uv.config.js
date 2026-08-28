self.__uv$config = {
    prefix: '/uv/service/',
    bare: 'https://tomp.app/', // Public Bare server, can be changed if it goes down
    encodeUrl: Ultraviolet.codec.xor.encode,
    decodeUrl: Ultraviolet.codec.xor.decode,
    handler: '/uv/uv.handler.js',
    bundle: '/uv/uv.bundle.js',
    config: '/uv/uv.config.js',
    sw: '/uv/sw.js',
};
