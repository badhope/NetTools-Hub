// Simple static file server for Next.js static export with trailing slash support
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = '/workspace/out';
const PORT = 8080;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.mjs':  'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.txt':  'text/plain; charset=utf-8',
  '.svg':  'image/svg+xml',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.webp': 'image/webp',
  '.ico':  'image/x-icon',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.map':  'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.xml':  'application/xml; charset=utf-8',
};

function send(res, code, body, headers = {}) {
  res.writeHead(code, { 'Cache-Control': 'no-store', ...headers });
  res.end(body);
}

function safeJoin(root, urlPath) {
  let p = decodeURIComponent(urlPath.split('?')[0].split('#')[0]);
  const resolved = path.normalize(path.join(root, p));
  if (!resolved.startsWith(root)) return null;
  return resolved;
}

// Resolve a URL to a concrete file path under ROOT, or null if not found.
// Returns { filePath, redirect } where redirect is a 308 target if we need to
// canonicalize the trailing slash.
function resolveFile(urlPath) {
  const target = safeJoin(ROOT, urlPath);
  if (target === null) return { error: 400 };

  // 1. Exact file
  if (isFile(target)) return { filePath: target };

  // 2. Directory -> index.html
  if (isDir(target)) {
    const idx = path.join(target, 'index.html');
    if (isFile(idx)) return { filePath: idx };
    return { error: 404 };
  }

  // 3. Missing path. If URL doesn't have trailing slash, try redirect to canonical.
  if (!urlPath.endsWith('/')) {
    const withSlash = urlPath + '/';
    const idx2 = path.join(ROOT, withSlash, 'index.html');
    if (isFile(idx2)) return { redirect: withSlash };
  }

  // 4. Try .html extension
  const withHtml = target + '.html';
  if (isFile(withHtml)) return { filePath: withHtml };

  return { error: 404 };
}

function isFile(p) {
  try {
    return fs.statSync(p).isFile();
  } catch {
    return false;
  }
}

function isDir(p) {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

const server = http.createServer((req, res) => {
  const url = req.url || '/';
  if (url === '/__health') return send(res, 200, 'ok', { 'Content-Type': 'text/plain' });

  const result = resolveFile(url);
  if (result.error === 400) return send(res, 400, 'Bad request');
  if (result.redirect) return send(res, 308, '', { Location: result.redirect });
  if (result.error === 404) {
    const nf = path.join(ROOT, '404.html');
    if (isFile(nf)) {
      return send(res, 404, fs.readFileSync(nf), { 'Content-Type': MIME['.html'] });
    }
    return send(res, 404, 'Not Found');
  }

  const filePath = result.filePath;
  const ext = path.extname(filePath).toLowerCase();
  const type = MIME[ext] || 'application/octet-stream';
  const size = fs.statSync(filePath).size;
  res.writeHead(200, {
    'Content-Type': type,
    'Content-Length': size,
    'Cache-Control': 'no-store',
  });
  fs.createReadStream(filePath).pipe(res);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[preview] serving ${ROOT} on http://0.0.0.0:${PORT}`);
});
