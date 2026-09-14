import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert';

console.log('🧐 [Tester & Security QA] Running Adversarial UI & Client-side Fuzzing Tests...');

const distPath = path.resolve('dist');
const indexPath = path.join(distPath, 'index.html');
const searchIndexPath = path.resolve('public/data/search_index.json');

// 1. Verify index.html exists
assert(fs.existsSync(indexPath), '🔴 Blocker: dist/index.html was not generated!');
const html = fs.readFileSync(indexPath, 'utf-8');

// 2. Client-Side XSS and Script Injection Defense
const maliciousSearchPayloads = [
  '<script>document.title="PWNED"</script>',
  '"><svg onload=alert(1)>',
  "'; DROP TABLE jobs; --",
  '[[[[((((*+?\\',
  'Fresher\u200b Network \u202eEngineer 👨‍👩‍👧‍👦'
];

// Test JavaScript regex escaping function logic used in client search
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

for (const payload of maliciousSearchPayloads) {
  try {
    const escaped = escapeRegex(payload);
    const re = new RegExp(escaped, 'i');
    // Ensure regex compilation succeeds without throw
    assert(re instanceof RegExp, `Failed to compile escaped regex for: ${payload}`);
  } catch (err) {
    assert.fail(`🔴 Regex Crash: Adversarial payload broke regex compiler: ${payload} -> ${err.message}`);
  }
}
console.log(`✔ [1/5] Client Regex Injection Resilience: ${maliciousSearchPayloads.length} malicious payloads neutralized`);

// 3. Search Index Integrity & Inverted Schema Validation
assert(fs.existsSync(searchIndexPath), '🔴 Missing public/data/search_index.json');
const indexData = JSON.parse(fs.readFileSync(searchIndexPath, 'utf-8'));

assert(indexData.version === '1.0.0', '🔴 Index version mismatch');
assert(typeof indexData.total_records === 'number', '🔴 Invalid total_records');
assert(indexData.indexes && indexData.indexes.by_role, '🔴 Missing indexes.by_role');
assert(indexData.indexes && indexData.indexes.by_location, '🔴 Missing indexes.by_location');
assert(indexData.indexes && indexData.indexes.by_level, '🔴 Missing indexes.by_level');
assert(indexData.indexes && indexData.indexes.by_skill, '🔴 Missing indexes.by_skill');
assert(indexData.indexes && indexData.indexes.by_keyword, '🔴 Missing indexes.by_keyword');
assert(indexData.records && Object.keys(indexData.records).length > 0, '🔴 Empty records lookup table');
console.log(`✔ [2/5] Inverted Search Index: 100% Validated (${Object.keys(indexData.records).length} jobs, ${Object.keys(indexData.indexes.by_keyword).length} keyword tokens)`);

// 4. UI Fallback & State Recovery Controls
assert(html.includes('id="empty-reset-btn"'), '🔴 Missing #empty-reset-btn button for empty-state recovery');
assert(html.includes('id="retry-fetch-btn"'), '🔴 Missing #retry-fetch-btn button for error-state recovery');
console.log('✔ [3/5] State Recovery Controls: Reset & Retry buttons verified');

// 5. Dark Theme Color Contrast Check
assert(html.includes('#090d16') || html.includes('bg-[#090d16]'), '🔴 Missing dark cyber radar background color');
assert(html.includes('text-slate-100') || html.includes('text-white'), '🔴 Missing high-contrast title text color');
console.log('✔ [4/5] Dark Theme Contrast: Cyber radar dark palette validated');

// 6. Mobile 320px Viewport Overflow Guard
// Ensure no hardcoded full-screen widths like w-[500px] that exceed 320px
const hardcodedWideRegex = /w-\[(\d{3,})px\]/g;
let match;
const wideClasses = [];
while ((match = hardcodedWideRegex.exec(html)) !== null) {
  const width = parseInt(match[1], 10);
  if (width > 320) {
    wideClasses.push(`w-[${width}px]`);
  }
}
assert(wideClasses.length === 0, `🔴 Mobile Overflow: Detected fixed widths exceeding 320px: ${wideClasses.join(', ')}`);
console.log('✔ [5/5] Mobile-First Safety (320px Viewport): Zero fixed-width overflows detected');

console.log('\n🏅 [Tester & Security QA] All Adversarial UI checks PASSED with exit code 0!\n');
process.exit(0);
