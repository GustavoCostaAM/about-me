import { createServer } from 'node:http';
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const root = path.resolve(import.meta.dirname, '..');
const config = JSON.parse(await readFile(path.join(root, 'site.config.json'), 'utf8'));
const manifest = JSON.parse(await readFile(path.join(root, 'reports', 'public-files.json'), 'utf8'));
const files = new Set(manifest.files);
const pages = manifest.files.filter(file => file.toLowerCase().endsWith('.html')).sort();
if (!pages.length) throw new Error('No HTML pages discovered');
const tags = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'];
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.js': 'text/javascript' };
const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://localhost');
    const decoded = decodeURIComponent(url.pathname);
    if (!decoded.startsWith(config.basePath)) throw new Error('Outside base path');
    let file = decoded.slice(config.basePath.length);
    if (!file || file.endsWith('/')) file += 'index.html';
    if (!files.has(file)) throw new Error('File not in public manifest');
    const target = path.join(root, 'dist', file);
    if (!(await stat(target)).isFile()) throw new Error('Not a file');
    response.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' });
    response.end(await readFile(target));
  } catch {
    response.writeHead(404);
    response.end('Not found');
  }
});

let browser;
const report = { viewport: config.viewport, tags, pages: [], errors: [], warnings: [] };
try {
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const origin = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch();
  for (const file of pages) {
    console.log(`A11Y PAGE ${file}`);
    const page = await browser.newPage({ viewport: config.viewport });
    const localFailures = [];
    page.on('requestfailed', request => {
      const message = `${file}: ${request.url()}: ${request.failure()?.errorText}`;
      if (request.url().startsWith(origin + '/')) localFailures.push(message);
      else report.warnings.push({ type: 'external-request', message });
    });
    page.on('response', response => {
      if (response.status() < 400) return;
      const message = `${file}: HTTP ${response.status()} ${response.url()}`;
      if (response.url().startsWith(origin + '/')) localFailures.push(message);
      else report.warnings.push({ type: 'external-response', message });
    });
    page.on('pageerror', error => localFailures.push(`${file}: script: ${error.message}`));
    try {
      const url = origin + config.basePath + file.split('/').map(encodeURIComponent).join('/');
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      if (!response?.ok() || page.url() !== url) throw new Error(`Page did not load at expected URL: ${page.url()}`);
      // Wait for local images, without making third-party frames a prerequisite.
      await page.waitForFunction(localOrigin => [...document.images]
        .filter(image => new URL(image.currentSrc || image.src, document.baseURI).origin === localOrigin)
        .every(image => image.complete), origin, { timeout: 15000 });
      const brokenImages = await page.evaluate(localOrigin => [...document.images]
        .filter(image => new URL(image.currentSrc || image.src, document.baseURI).origin === localOrigin && !image.naturalWidth)
        .map(image => image.src), origin);
      if (brokenImages.length) throw new Error(`Local images did not decode: ${brokenImages.join(', ')}`);
      const result = await new AxeBuilder({ page }).withTags(tags)
        .options({ rules: { 'target-size': { enabled: true } } }).analyze();
      report.pages.push({ file, url, axeVersion: result.testEngine.version,
        violations: result.violations, incomplete: result.incomplete,
        passes: result.passes.map(rule => rule.id), inapplicable: result.inapplicable.map(rule => rule.id) });
      // Every violation blocks, including best practices and minor impact. No severity downgrade.
      for (const rule of result.violations) report.errors.push({ file, rule: rule.id, impact: rule.impact,
        nodes: rule.nodes.map(node => ({ target: node.target, summary: node.failureSummary })) });
      for (const rule of result.incomplete) report.warnings.push({ file, type: 'incomplete', rule: rule.id, nodes: rule.nodes });
      report.errors.push(...localFailures.map(message => ({ file, message })));
      console.log(`${file}: ${result.violations.length} errors; ${result.incomplete.length} incomplete rules`);
    } catch (error) {
      report.errors.push({ file, message: error.stack || String(error) });
    } finally {
      await page.close();
    }
  }
} catch (error) {
  report.errors.push({ message: error.stack || String(error) });
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await mkdir(path.join(root, 'reports'), { recursive: true });
  await writeFile(path.join(root, 'reports', 'accessibility.json'), JSON.stringify(report, null, 2) + '\n');
}
for (const error of report.errors) console.error('ERROR', JSON.stringify(error));
for (const warning of report.warnings) console.warn('WARNING', JSON.stringify(warning));
if (report.errors.length || report.pages.length !== pages.length) process.exitCode = 1;

