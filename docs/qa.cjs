const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const rootDir = 'C:\\Users\\ASUS\\Downloads';

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent((req.url || '/index1.html').split('?')[0]);
  const filePath = path.join(rootDir, urlPath === '/' ? 'index1.html' : urlPath);
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const type = {
      '.html': 'text/html; charset=utf-8',
      '.js': 'text/javascript',
      '.css': 'text/css',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.mp4': 'video/mp4',
      '.pdf': 'application/pdf',
    }[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': type });
    res.end(data);
  });
});

(async () => {
  await new Promise((resolve) => server.listen(4174, '127.0.0.1', resolve));
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const logs = [];

  page.on('console', (msg) => logs.push(`${msg.type()}: ${msg.text()}`));
  page.on('pageerror', (err) => logs.push(`pageerror: ${err.message}`));

  await page.goto('http://127.0.0.1:4174/index1.html', {
    waitUntil: 'domcontentloaded',
    timeout: 30000,
  });
  await page.waitForTimeout(7000);

  const desktop = await page.evaluate(() => ({
    rootText: document.querySelector('#root')?.innerText?.slice(0, 120) || '',
    navLinks: [...document.querySelectorAll('nav a')].map((a) => a.textContent.trim()),
    icons: document.querySelectorAll('.hero-icon-orbit').length,
    socialCards: document.querySelectorAll('.social-card').length,
    filmFrames: document.querySelectorAll('.film-frame').length,
    bodyW: document.documentElement.scrollWidth,
    innerW: innerWidth,
    bodyH: document.documentElement.scrollHeight,
  }));

  await page.getByRole('button', { name: /Toggle language/i }).click();
  await page.waitForTimeout(300);
  const arabic = await page.evaluate(() => ({
    dir: document.querySelector('.interactive-shell')?.getAttribute('dir'),
    text: document.querySelector('#root')?.innerText?.slice(0, 180) || '',
    font: getComputedStyle(document.querySelector('.interactive-shell')).fontFamily,
  }));

  await page.getByRole('button', { name: /Toggle theme/i }).click();
  await page.waitForTimeout(300);
  const light = await page.evaluate(() => ({
    hasLight: document.querySelector('.interactive-shell')?.classList.contains('theme-light'),
    navBg: getComputedStyle(document.querySelector('nav')).backgroundColor,
  }));

  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(1200);

  const mobile = await page.evaluate(() => {
    const nav = document.querySelector('nav');
    const heroIcons = [...document.querySelectorAll('.hero-icon-orbit')].map((el) => el.getBoundingClientRect());
    const social = [...document.querySelectorAll('.social-card')].slice(0, 2).map((el) => el.getBoundingClientRect());
    const timeline = document.querySelector('.timeline-panel')?.getBoundingClientRect();

    return {
      navHeight: Math.round(nav?.getBoundingClientRect().height || 0),
      navLinksVisible: [...document.querySelectorAll('nav a')].filter((a) => getComputedStyle(a).display !== 'none').length,
      icons: heroIcons.length,
      firstIcon: heroIcons[0] ? {
        w: Math.round(heroIcons[0].width),
        h: Math.round(heroIcons[0].height),
        top: Math.round(heroIcons[0].top),
      } : null,
      social: social.map((r) => ({ w: Math.round(r.width), h: Math.round(r.height) })),
      timeline: timeline ? { w: Math.round(timeline.width), h: Math.round(timeline.height) } : null,
      bodyW: document.documentElement.scrollWidth,
      innerW: innerWidth,
      bodyH: document.documentElement.scrollHeight,
    };
  });

  await browser.close();
  server.close();
  console.log(JSON.stringify({ desktop, arabic, light, mobile, logs: logs.slice(0, 16) }, null, 2));
})().catch((err) => {
  server.close();
  console.error(err);
  process.exit(1);
});
