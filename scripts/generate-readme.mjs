import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

const APPS_JSON_URL =
  'https://api.github.com/repos/CarlosDanielDev/portfolio/contents/public/apps.json?ref=main';

const STATUS_BADGE = {
  published: (name, url) =>
    `<a href="${url}"><img src="https://img.shields.io/badge/App_Store-Published-000000?style=for-the-badge&logo=app-store&logoColor=white" alt="App Store"/></a>`,
  'in-review': () =>
    `<img src="https://img.shields.io/badge/Status-In_Review-orange?style=for-the-badge" alt="In Review"/>`,
  'coming-soon': () =>
    `<img src="https://img.shields.io/badge/Status-Coming_Soon-yellow?style=for-the-badge" alt="Coming Soon"/>`,
};

function buildAppCell(app) {
  const badgeFn = STATUS_BADGE[app.status];
  const badge = badgeFn ? badgeFn(app.name, app.appStoreUrl) : '';

  return [
    `    <td align="center" width="25%">`,
    `      <strong>${app.name}</strong><br/>`,
    `      <sub>${app.tagline}</sub><br/><br/>`,
    `      ${badge}`,
    `    </td>`,
  ].join('\n');
}

function buildAppsSection(apps) {
  const rows = [];
  for (let i = 0; i < apps.length; i += 4) {
    const chunk = apps.slice(i, i + 4);
    const cells = chunk.map(buildAppCell).join('\n');
    rows.push(`  <tr>\n${cells}\n  </tr>`);
  }
  return `<table>\n${rows.join('\n')}\n</table>`;
}

async function main() {
  const token = process.env.PORTFOLIO_TOKEN;
  if (!token) {
    throw new Error('PORTFOLIO_TOKEN environment variable is required');
  }

  console.log(`Fetching apps data from GitHub API...`);
  const response = await fetch(APPS_JSON_URL, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github.v3.raw',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch apps.json: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  const apps = data.apps;
  console.log(`Fetched ${apps.length} apps (generated ${data.generatedAt})`);

  const publishedCount = apps.filter((a) => a.status === 'published').length;
  const appsSection = buildAppsSection(apps);

  const templatePath = resolve(ROOT, 'README.template.md');
  const template = readFileSync(templatePath, 'utf-8');

  const readme = template
    .replace('{{publishedCount}}', String(publishedCount))
    .replace('{{appsSection}}', appsSection);

  const readmePath = resolve(ROOT, 'README.md');
  writeFileSync(readmePath, readme);
  console.log(`Generated README.md with ${apps.length} apps (${publishedCount} published)`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
