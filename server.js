'use strict';

const http = require('node:http');
const path = require('node:path');
const express = require('express');
const { createBareServer } = require('@tomphttp/bare-server-node');

const app = express();
const server = http.createServer();
const bareServer = createBareServer('/bare/');

const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || '127.0.0.1';
const ROOT = __dirname;

// Serve the existing GRASSUBG frontend, including /uv/* assets.
app.use(express.static(ROOT, {
  index: 'index.html',
  fallthrough: true
}));

app.get('/health', (_req, res) => {
  res.type('text/plain').send('GRASSUBG local server OK');
});

app.use((_req, res) => {
  res.status(404).type('text/plain').send('Not found');
});

// Bare must receive matching requests before Express handles normal files.
server.on('request', (req, res) => {
  if (bareServer.shouldRoute(req)) {
    return bareServer.routeRequest(req, res);
  }
  return app(req, res);
});

// Bare also uses HTTP upgrade for WebSocket traffic.
server.on('upgrade', (req, socket, head) => {
  if (bareServer.shouldRoute(req)) {
    return bareServer.routeUpgrade(req, socket, head);
  }
  socket.end();
});

server.listen(PORT, HOST, () => {
  console.log(`GRASSUBG running at http://${HOST}:${PORT}`);
  console.log(`Bare server mounted at http://${HOST}:${PORT}/bare/`);
});

function shutdown(signal) {
  console.log(`\n${signal} received. Shutting down...`);
  server.close(() => process.exit(0));
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
