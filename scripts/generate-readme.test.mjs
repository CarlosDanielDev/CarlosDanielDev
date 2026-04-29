import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { mkdtempSync, readFileSync, cpSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const SCRIPT = resolve(here, 'generate-readme.mjs');
const TEMPLATE_SRC = resolve(here, '..', 'README.template.md');

function startFixtureServer(handler) {
  return new Promise((res) => {
    const server = createServer(handler);
    server.listen(0, '127.0.0.1', () => res(server));
  });
}

function closeServer(server) {
  return new Promise((resolve) => {
    server.closeAllConnections?.();
    server.close(() => resolve());
  });
}

function runScript({ env = {}, cwd }) {
  return new Promise((resolve) => {
    const cleanEnv = { ...process.env, README_ROOT: cwd, ...env };
    if (env.PORTFOLIO_APPS_URL === '') delete cleanEnv.PORTFOLIO_APPS_URL;
    if (env.PORTFOLIO_TOKEN === '') delete cleanEnv.PORTFOLIO_TOKEN;
    const child = spawn(process.execPath, [SCRIPT], {
      cwd,
      env: cleanEnv,
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString('utf-8');
    });
    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString('utf-8');
    });
    child.on('close', (status) => {
      resolve({ status, stdout, stderr });
    });
  });
}

function makeWorkdir() {
  const dir = mkdtempSync(join(tmpdir(), 'readme-'));
  cpSync(TEMPLATE_SRC, join(dir, 'README.template.md'));
  return dir;
}

test('fails when PORTFOLIO_TOKEN is missing', async () => {
  const dir = makeWorkdir();
  const result = await runScript({ env: { PORTFOLIO_TOKEN: '' }, cwd: dir });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /PORTFOLIO_TOKEN/);
});

test('uses PORTFOLIO_APPS_URL when provided', async () => {
  const dir = makeWorkdir();
  let receivedUrl = '';
  const server = await startFixtureServer((req, res) => {
    receivedUrl = req.url;
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ apps: [], generatedAt: '2025-01-01' }));
  });
  const port = server.address().port;
  const result = await runScript({
    env: {
      PORTFOLIO_TOKEN: 'fake',
      PORTFOLIO_APPS_URL: `http://127.0.0.1:${port}/custom/apps.json`,
    },
    cwd: dir,
  });
  await closeServer(server);
  assert.equal(result.status, 0, `stderr: ${result.stderr}`);
  assert.equal(receivedUrl, '/custom/apps.json');
});

test('throws clear error when apps.json shape is wrong', async () => {
  const dir = makeWorkdir();
  const server = await startFixtureServer((req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ message: 'Not Found' }));
  });
  const port = server.address().port;
  const result = await runScript({
    env: {
      PORTFOLIO_TOKEN: 'fake',
      PORTFOLIO_APPS_URL: `http://127.0.0.1:${port}/`,
    },
    cwd: dir,
  });
  await closeServer(server);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Unexpected apps\.json shape/);
});

test('renders apps section with valid input', async () => {
  const dir = makeWorkdir();
  const server = await startFixtureServer((req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(
      JSON.stringify({
        apps: [
          {
            name: 'Foo',
            tagline: 'desc',
            status: 'published',
            appStoreUrl: 'https://example.com/foo',
          },
        ],
        generatedAt: '2025-01-01',
      })
    );
  });
  const port = server.address().port;
  const result = await runScript({
    env: {
      PORTFOLIO_TOKEN: 'fake',
      PORTFOLIO_APPS_URL: `http://127.0.0.1:${port}/`,
    },
    cwd: dir,
  });
  await closeServer(server);
  assert.equal(result.status, 0, `stderr: ${result.stderr}`);
  const out = readFileSync(join(dir, 'README.md'), 'utf-8');
  assert.match(out, /Foo/);
});

test('falls back to default URL when PORTFOLIO_APPS_URL is empty', async () => {
  const dir = makeWorkdir();
  const result = await runScript({
    env: { PORTFOLIO_TOKEN: 'definitely-bad', PORTFOLIO_APPS_URL: '' },
    cwd: dir,
  });
  assert.notEqual(result.status, 0);
  assert.match(
    result.stderr,
    /api\.github\.com\/repos\/CarlosDanielDev\/portfolio|Failed to fetch apps\.json|fetch failed/i
  );
});
