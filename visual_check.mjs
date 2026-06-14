import { chromium } from '@playwright/test';

const pages = [
  { name: 'home', url: 'http://localhost:8080/' },
  { name: 'explore', url: 'http://localhost:8080/explore' },
  { name: 'kind-proxy', url: 'http://localhost:8080/explore/k/proxy' },
  { name: 'platform-proxy-desktop', url: 'http://localhost:8080/explore/k/proxy/p/desktop' },
  { name: 'detail-sing-box', url: 'http://localhost:8080/explore/project/sing-box' },
];

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  
  const consoleErrors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(`[${msg.type()}] ${msg.text()}`);
  });
  page.on('pageerror', (err) => consoleErrors.push(`[pageerror] ${err.message}`));
  
  for (const p of pages) {
    console.log(`\n=== ${p.name} ===`);
    try {
      const resp = await page.goto(p.url, { waitUntil: 'networkidle', timeout: 15000 });
      console.log(`HTTP: ${resp?.status()}`);
      await page.screenshot({ path: `/tmp/screen-${p.name}.png`, fullPage: false });
      
      const cardCount = await page.locator('a[href*="/explore/project/"]').count();
      console.log(`项目链接数: ${cardCount}`);
      
      const themeBtn = await page.locator('button[aria-label*="切换"]').count();
      console.log(`主题按钮: ${themeBtn}`);
      
      const langBtn = await page.locator('button[aria-label*="Switch language"]').count();
      console.log(`语言按钮: ${langBtn}`);
      
      const sidebarLinks = await page.locator('a[href*="/explore/k/"]').count();
      console.log(`分类链接: ${sidebarLinks}`);
    } catch (e) {
      console.log(`错误: ${e.message}`);
    }
  }
  
  // 点击语言按钮测试
  console.log('\n=== 测试语言切换 ===');
  await page.goto('http://localhost:8080/explore', { waitUntil: 'networkidle' });
  const langBtn = page.locator('button[aria-label*="Switch language"]').first();
  await langBtn.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/screen-lang-open.png' });
  
  // 选择中文
  const zhOpt = page.locator('button[role="option"]').filter({ hasText: '中文' });
  console.log(`中文选项: ${await zhOpt.count()}`);
  if (await zhOpt.count() > 0) {
    await zhOpt.first().click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: '/tmp/screen-lang-zh.png' });
    const title = await page.locator('h1').first().textContent();
    console.log(`标题: ${title}`);
  }
  
  if (consoleErrors.length) {
    console.log(`\n=== 控制台错误 (${consoleErrors.length}) ===`);
    consoleErrors.slice(0, 10).forEach(e => console.log(e));
  } else {
    console.log('\n=== 无控制台错误 ===');
  }
  
  await browser.close();
})();
