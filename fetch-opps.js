const https = require('https');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const HG_KEY = '1a262cdcd25f40fba31836526d6e12b1';
const SEARCHES = [
  // Rex's searches
  { id: 'm6_juXBrDh441f0I-mD5s', label: 'User Experience', ericAlso: false },
  // Eric's existing HigherGov saved searches (marked ericAlso: true)
  { id: 'c-DVvbqbEWlzb-MHZ3JNR',    label: 'CDC 8(a)',                  ericAlso: true },
  { id: '9O8IE4AuzgLjT6aQtZjHy',    label: 'Census Opps (BLN NAICS)',  ericAlso: true },
  { id: 'FRacCgvvUr69AzRneQauN',    label: 'NOAA General',              ericAlso: true },
  { id: 'E2rJZOxslwGCLQi3m7VlY',    label: 'Commerce Opportunities',   ericAlso: true },
  { id: 'bfIczPCqwFX0CqfQBdqwV',    label: 'IRS & Treasury',            ericAlso: true },
  { id: '0V6NAggtyNTUw6GGsmk9e',    label: 'IRS Opportunities',         ericAlso: true },
  { id: 'QZWyCUILaOqccWDMKmW-z',    label: 'All Agencies',              ericAlso: true },
];
const DASHBOARD_DIR = '/Users/t24/Desktop/T24/dashboard';
const OUT_FILE = path.join(DASHBOARD_DIR, 'opps.json');

// Federal agency keywords - positive signals
const FEDERAL_POSITIVE = [
  'department of', 'dept of', 'office of', 'bureau of', 'administration',
  'agency', 'commission', 'authority', 'institute', 'center for', 'corps',
  'command', 'navy', 'army', 'air force', 'marine corps', 'coast guard',
  'nih', 'irs', 'faa', 'fbi', 'dod', 'hhs', 'dhs', 'gsa', 'epa',
  'usace', 'visn', 'nasa', 'nsf', 'noaa', 'usda', 'census', 'fema',
  'millennium challenge', 'defense ', 'intelligence', 'treasury',
  'customs and border', 'immigration', 'federal ', 'national ',
  'u.s. ', 'united states ', 'american battle', 'broadcasting board',
  'peace corps', 'trade and development', 'export-import',
];

// SLED keywords - disqualifiers
const SLED_DISQUALIFIERS = [
  'county', 'city of', 'town of', 'village of', 'borough',
  'school district', 'school board', 'boces', 'university', 'college',
  'judicial branch', 'judicial council', 'septa', 'mta', 'transit authority',
  'water district', 'fire district', 'municipal', 'parks & wildlife',
  'parks and wildlife', 'department of natural resources',
  'real estate commission', 'gaming commission',
];

// BLN24 past performance agencies
const BLN24_AGENCIES = [
  'census', 'internal revenue', ' irs', 'noaa', 'fema', 'cdc', 'cms ',
  'centers for medicare', 'hhs', 'health resources', 'hrsa',
  'administration for community', 'acl', 'commerce', 'usda',
  'agriculture', 'gsa', 'uspto', 'patent', 'department of education',
  'housing', 'hud', 'defense health', 'dha', 'epa', 'treasury',
  'homeland', 'dhs', 'labor', 'interior', 'nih', 'fda',
  'national telecommunications', 'ntia', 'minority business', 'mbda',
  'federal trade', 'ftc', 'department of state', 'state department',
  'transportation', 'navy', 'army', 'air force', 'booz allen',
  'oversight.gov', 'inspector general',
];

// Official BLN24 NAICS codes from Capability Statement (updated Apr 2026)
const BLN24_NAICS = new Set(['541511','541513','541611','541612','541690','541613','541990','518210','512110','541519','541618','541430']);

const CX_KW = ['user experience','ux ','human-centered','human centered','service design','accessibility','section 508','508 compliance','human factors','usability'];
const COMMS_KW = ['communications','outreach','marketing','campaign','branding','content strategy','public affairs','media','advertising','stakeholder','storytelling'];
const DATA_KW = ['data analytics','data management','business intelligence','dashboard','analytics platform','ai ','machine learning','artificial intelligence','data engineering','data architecture'];
const TECH_KW = ['modernization','cloud ','devops','devsecops','cybersecurity','legacy','digital services','web development','software development','it support','application'];

function isFederal(agencyName) {
  const a = agencyName.toLowerCase();
  if (SLED_DISQUALIFIERS.some(k => a.includes(k))) return false;
  if (FEDERAL_POSITIVE.some(k => a.includes(k))) return true;
  // Default to false for ambiguous names
  return false;
}

function scoreOpp(o) {
  const agency = (o.agency || '').toLowerCase();
  const naics = o.naics || '';
  const sa = (o.set_aside || '').toLowerCase();
  const title = (o.title || '').toLowerCase();
  const summary = (o.summary || '').toLowerCase();
  const combined = title + ' ' + summary;
  let score = 0;
  const reasons = [];

  // Past performance match
  if (BLN24_AGENCIES.some(a => agency.includes(a))) {
    score += 25;
    reasons.push('Past performance with this agency');
  }
  // NAICS match
  if (BLN24_NAICS.has(naics)) {
    score += 20;
    reasons.push('NAICS aligns with BLN24 capabilities');
  }
  // Set-aside
  if (sa.includes('8a') || sa.includes('8(a)')) {
    score += 20;
    reasons.push('8(a) set-aside — direct vehicle match');
  } else if (sa.includes('sba') || sa.includes('small business') || sa.includes('wosb') || sa.includes('sdvosb')) {
    score += 10;
    reasons.push('Small business set-aside');
  } else if (!sa || sa.toLowerCase().includes('full and open') || sa.toLowerCase().includes('unrestricted')) {
    score -= 10;
    reasons.push('Full & Open — lower win probability (competing against all firms)');
  }
  // Capability keywords
  if (CX_KW.some(k => combined.includes(k))) { score += 15; reasons.push('CX/UX capability match'); }
  if (COMMS_KW.some(k => combined.includes(k))) { score += 12; reasons.push('Strategic Comms match'); }
  if (DATA_KW.some(k => combined.includes(k))) { score += 10; reasons.push('Data/Analytics match'); }
  if (TECH_KW.some(k => combined.includes(k))) { score += 8; reasons.push('Tech Modernization match'); }

  // Out of scope penalty
  const oos = ['medical device','construction','hvac','logistics','warehousing','janitorial','food','vehicle','aircraft','weapon','ammunition'];
  if (oos.some(k => combined.includes(k))) { score -= 30; reasons.push('OUT OF SCOPE signals'); }

  // Tier classification — BLN24 has proven wins at T2 and T3, highest probability there
  // Tier 3: $500K–5M — proven wins, highest probability
  // Tier 2: $5M–20M — proven wins, strong target
  // Tier 1: $20M+ — can win but needs existing relationship, harder cold
  const midVal = (o.val_low && o.val_high) ? (o.val_low + o.val_high) / 2 : (o.val_low || o.val_high || null);
  let tier = null;
  if (midVal !== null) {
    if (midVal >= 20000000) { tier = 1; score -= 10; reasons.push('Tier 1 ($20M+) — needs existing relationship to win; harder cold'); }
    else if (midVal >= 5000000) { tier = 2; score += 15; reasons.push('Tier 2 ($5M–20M) — BLN24 proven wins at this range'); }
    else if (midVal >= 500000) { tier = 3; score += 20; reasons.push('Tier 3 ($500K–5M) — BLN24 proven wins, highest probability tier'); }
    else { tier = null; reasons.push('Value below $500K — bid cost likely exceeds return'); }
  }

  let winProb;
  if (score >= 50) winProb = 'High (40-60%)';
  else if (score >= 30) winProb = 'Medium (20-40%)';
  else if (score >= 15) winProb = 'Low (10-20%)';
  else winProb = 'Very Low (<10%)';

  return { score, reasons, winProb, tier };
}

function hgFetch(searchId) {
  return new Promise((resolve, reject) => {
    const url = new URL(`https://www.highergov.com/api-external/opportunity/?api_key=${HG_KEY}&search_id=${encodeURIComponent(searchId)}&page_size=100`);
    const req = https.request({
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: 'GET',
      minVersion: 'TLSv1.2',
      maxVersion: 'TLSv1.2',
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { reject(new Error('JSON parse failed: ' + data.substring(0,200))); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  const today = new Date().toISOString().split('T')[0];
  // Priority types — RFI/Sources Sought, RFP/Solicitation, Forecast
  const RFI_TYPES = new Set(['Sources Sought','Request for Information']);
  const RFP_TYPES = new Set(['Solicitation','Combined Synopsis/Solicitation','Request for Proposal','Request for Quotation']);
  const FORECAST_TYPES = new Set(['Presolicitation','Special Notice','Planning Notice']);
  const GOOD_TYPES = new Set([...RFI_TYPES, ...RFP_TYPES, ...FORECAST_TYPES]);
  let allOpps = [];
  const seen = new Set();

  for (const search of SEARCHES) {
    try {
      const data = await hgFetch(search.id);
      const results = data.results || [];
      let added = 0, skipped_sled = 0, skipped_expired = 0, skipped_type = 0;

      for (const r of results) {
        const otype = (r.opp_type || {}).description || '';
        if (!GOOD_TYPES.has(otype)) { skipped_type++; continue; }
        const due = r.due_date || '';
        if (due && due < today) { skipped_expired++; continue; }
        const key = r.source_id || r.title || '';
        if (seen.has(key)) continue;
        seen.add(key);

        const agencyName = (r.agency || {}).agency_name || '';
        if (!isFederal(agencyName)) { skipped_sled++; continue; }

        const sa = r.set_aside || '';
        let vl = r.val_est_low, vh = r.val_est_high;
        try { vl = vl ? parseFloat(vl) : null; } catch(e) { vl = null; }
        try { vh = vh ? parseFloat(vh) : null; } catch(e) { vh = null; }

        const naics = (r.naics_code || {}).naics_code || '';
        // Categorize notice type
        let noticeCategory = 'other';
        if (RFI_TYPES.has(otype)) noticeCategory = 'rfi';
        else if (RFP_TYPES.has(otype)) noticeCategory = 'rfp';
        else if (FORECAST_TYPES.has(otype)) noticeCategory = 'forecast';

        const isFullOpen = !sa || sa.toLowerCase().includes('full and open') || sa.toLowerCase().includes('unrestricted');

        const opp = {
          naics, title: r.title || '', agency: agencyName,
          type: otype, noticeCategory, set_aside: sa, searchLabel: search.label,
          posted: r.posted_date || '', due,
          val_low: vl, val_high: vh,
          summary: (r.ai_summary || '').substring(0, 400),
          path: r.path || '',
          is8a: sa.toLowerCase().includes('8a') || sa.toLowerCase().includes('8(a)'),
          isFullOpen,
          ericAlso: search.ericAlso || false,
        };

        const { score, reasons, winProb, tier } = scoreOpp(opp);
        opp.capture_score = score;
        opp.win_reasons = reasons;
        opp.win_prob = winProb;
        opp.tier = tier;

        allOpps.push(opp);
        added++;
      }
      console.log(`"${search.label}": ${results.length} raw | ${added} federal active | skipped: ${skipped_sled} SLED, ${skipped_expired} expired, ${skipped_type} wrong type`);
    } catch(e) {
      console.error(`Error for ${search.label}:`, e.message);
    }
  }

  // Sort by capture score
  allOpps.sort((a, b) => b.capture_score - a.capture_score || (a.due || '9').localeCompare(b.due || '9'));

  const output = { updated: new Date().toISOString(), count: allOpps.length, opps: allOpps };
  fs.writeFileSync(OUT_FILE, JSON.stringify(output, null, 2));
  console.log(`Written ${allOpps.length} federal opps to ${OUT_FILE}`);

  try {
    execSync(`cd ${DASHBOARD_DIR} && git add opps.json && git diff --cached --quiet || (git commit -m "Update opps ${today}" && git push)`, { stdio: 'inherit' });
  } catch(e) {
    console.log('Git note:', e.message);
  }
}

main().catch(console.error);
