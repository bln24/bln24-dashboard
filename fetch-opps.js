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

// BLN24 direct past performance agencies
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

// Clarity24 JV (BLN24 + Accenture Federal Services) — 8(a) MP JV, UEI Q9VENYSZDXD3
// Confirmed wins: NOAA $7.06M, USDA FNS $2.2M, IRS $1.4M, CBP $1.37M (total $12.03M)
// Note: NOAA, USDA, IRS already in BLN24_AGENCIES — CBP/FNS added here
const CLARITY24_AGENCIES = [
  'customs and border protection', 'cbp',
  'food and nutrition service', 'fns',
];

// BLN Fors Marsh JV LLC — 8(a) JV, Asian-Pacific American Owned, UEI P4D4UVLLQQC3
// Confirmed wins: HHS Program Support Center $10.28M, USPTO $822K, FTC $581K (total $12M)
// Note: IRS already in BLN24_AGENCIES
const FORS_MARSH_AGENCIES = [
  'program support center',
  'federal trade commission', 'ftc',
  'patent and trademark', 'uspto',
  'bureau of the fiscal service', 'fiscal service',
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

  // Past performance match — direct BLN24
  if (BLN24_AGENCIES.some(a => agency.includes(a))) {
    score += 25;
    reasons.push('BLN24 direct past performance with this agency');
  }
  // Clarity24 JV past performance (BLN24 + Accenture) — CBP $1.4M, USDA FNS $2.2M
  else if (CLARITY24_AGENCIES.some(a => agency.includes(a))) {
    score += 20;
    reasons.push('Clarity24 JV past performance (BLN24 + Accenture) — $12M in cloud/digital wins');
  }
  // BLN Fors Marsh JV past performance — HHS $10.3M, USPTO, FTC
  else if (FORS_MARSH_AGENCIES.some(a => agency.includes(a))) {
    score += 20;
    reasons.push('BLN Fors Marsh JV past performance — $12M in comms/behavioral science wins');
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

  // Tier classification — context only, not a scoring modifier
  // BLN24 has proven wins at T2 and T3; T1 harder cold but not deprioritized
  const midVal = (o.val_low && o.val_high) ? (o.val_low + o.val_high) / 2 : (o.val_low || o.val_high || null);
  let tier = null;
  if (midVal !== null) {
    if (midVal >= 20000000) { tier = 1; }
    else if (midVal >= 5000000) { tier = 2; }
    else if (midVal >= 500000) { tier = 3; }
    // below $500K: no tier assigned
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
  // Type sets matched to actual HigherGov values
  // Note: opp_cat='Federal Forecast Opportunity' uses type 'New' or 'Recompete' — distinguished by opp_cat, not opp_type
  const RFI_TYPES = new Set(['Sources Sought','Request for Information']);
  const RFP_TYPES = new Set(['Solicitation','Synopsis Solicitation','Combined Synopsis/Solicitation','Request for Proposal','Request for Quotation']);
  const FORECAST_OPP_CAT = 'Federal Forecast Opportunity';
  const CONTRACT_OPP_CAT = 'Federal Contract Opportunity';
  // Accept all opp_cats we care about; filter Award Notices etc by checking opp_cat
  const SKIP_TYPES = new Set(['Award Notice','Justification','Special Notice']);
  let allOpps = [];
  const seen = new Set();

  for (const search of SEARCHES) {
    try {
      const data = await hgFetch(search.id);
      const results = data.results || [];
      let added = 0, skipped_sled = 0, skipped_expired = 0, skipped_type = 0;

      for (const r of results) {
        const otype = (r.opp_type || {}).description || '';
        const ocat = r.opp_cat || '';
        // Skip award notices, justifications, and other noise
        if (SKIP_TYPES.has(otype)) { skipped_type++; continue; }
        // Skip if neither a known contract opp nor a forecast
        if (ocat && ocat !== CONTRACT_OPP_CAT && ocat !== FORECAST_OPP_CAT) { skipped_type++; continue; }
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
        // Categorize notice type — forecasts identified by opp_cat, not opp_type
        let noticeCategory = 'other';
        if (ocat === FORECAST_OPP_CAT) noticeCategory = 'forecast';
        else if (RFI_TYPES.has(otype)) noticeCategory = 'rfi';
        else if (RFP_TYPES.has(otype)) noticeCategory = 'rfp';
        else noticeCategory = 'rfp'; // default active solicitations to rfp bucket

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
