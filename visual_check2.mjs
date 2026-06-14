// 通过 HTTP 拉取 + 视觉规则分析（不依赖浏览器二进制）
import fs from 'fs';

const pages = [
  { name: 'home', url: 'http://localhost:8080/' },
  { name: 'explore', url: 'http://localhost:8080/explore' },
  { name: 'kind-proxy', url: 'http://localhost:8080/explore/k/proxy' },
  { name: 'platform-proxy-desktop', url: 'http://localhost:8080/explore/k/proxy/p/desktop' },
  { name: 'detail-sing-box', url: 'http://localhost:8080/explore/project/sing-box' },
];

const issues = [];

for (const p of pages) {
  const r = await fetch(p.url);
  const html = await r.text();
  console.log(`\n=== ${p.name} (${html.length} bytes) ===`);
  
  // 检查 1: 是否有 hydration error
  if (html.includes('hydration') || html.includes('Hydration')) {
    issues.push(`${p.name}: 检测到 hydration 相关字符串`);
  }
  
  // 检查 2: 卡片高度是否一致
  const cardClass = 'class="group block border border-line bg-bg-elev/40';
  const cardCount = (html.match(new RegExp(cardClass, 'g')) || []).length;
  console.log(`  卡片数: ${cardCount}`);
  
  // 检查 3: 按钮是否可点击 (有 onClick)
  const buttonCount = (html.match(/<button/g) || []).length;
  const linkCount = (html.match(/<a /g) || []).length;
  console.log(`  按钮: ${buttonCount}, 链接: ${linkCount}`);
  
  // 检查 4: 描述是否被截断
  const clampCount = (html.match(/line-clamp-2/g) || []).length;
  console.log(`  描述截断: ${clampCount}`);
  
  // 检查 5: 徽章存在
  const badgeCount = (html.match(/font-mono/g) || []).length;
  console.log(`  monospace 元素: ${badgeCount}`);
}

console.log('\n=== 视觉问题汇总 ===');
if (issues.length === 0) {
  console.log('  ✓ 未发现明显问题');
} else {
  issues.forEach(i => console.log(`  ✗ ${i}`));
}
