const https = require('https');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const HG_KEY = '1a262cdcd25f40fba31836526d6e12b1';
const SEARCHES = [
  // Brian's primary NAICS-based search
  { id: 'Iup74Uz07U7NNMzBgoOGC', label: "Brian's Search", ericAlso: false },
  // Agency-specific supplemental searches (Eric's)
  { id: '9O8IE4AuzgLjT6aQtZjHy',    label: 'Census Opps',              ericAlso: true },
  { id: 'E2rJZOxslwGCLQi3m7VlY',    label: 'Commerce Opportunities',   ericAlso: true },
  { id: 'bfIczPCqwFX0CqfQBdqwV',    label: 'IRS & Treasury',            ericAlso: true },
  { id: '0V6NAggtyNTUw6GGsmk9e',    label: 'IRS Opportunities',         ericAlso: true },
  // Removed: CDC 8(a) (0 results), NOAA General (too broad/noisy), All Agencies (too broad/noisy)
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

// BLN24 confirmed past performance agencies (from SharePoint Contract Award spreadsheet + Past Performance folder)
// Prime: Census $18.4M, CMS $16M, IRS $7M, MBDA $4.4M, CDC $3.9M, Education $2.9M, HUD $2M
// Sub: DHA, DHRA, USPTO, NIH NEI
// JV (Clarity24): NOAA $7M, CBP $1.4M, USDA FNS $2.2M, IRS $1.4M
// JV (Fors Marsh): HHS PSC $10.3M, USPTO $822K, FTC $581K
const BLN24_AGENCIES = [
  // CONFIRMED PRIME WINS
  'census', 'centers for medicare', 'cms ', 'marketplace notice',
  'internal revenue', ' irs ', 'irs ',
  'minority business', 'mbda',
  'centers for disease', 'cdc ',
  'department of education', ' education ',
  'housing and urban', 'hud',
  'postal service', 'usps',
  'usda', 'agriculture',
  'health resources', 'hrsa',
  // CONFIRMED SUB WINS
  'defense health', 'dha',
  'defense human resources', 'dhra',
  'patent and trademark', 'uspto',
  'national eye institute', 'nei',
  // CONFIRMED PAST PERFORMANCE FOLDER AGENCIES
  'department of commerce', 'commerce',
  'department of homeland', 'homeland', 'dhs',
  'department of interior', 'interior', 'national park',
  'department of treasury', 'treasury', 'fiscal service',
  'election assistance', 'eac',
  'federal trade commission', 'ftc',
  // BROADER HHS / RELATED
  'health and human services', 'hhs',
  'administration for community', 'acl',
  'food and drug', 'fda',
  'national institutes', 'nih',
  'noaa', 'national oceanic',
  'fema',
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

// =============================================================
// SCOPE TAXONOMY
// Tags that describe WHAT TYPE of work an opp is asking for
// Used to show Brian a plain-English scope breakdown
// =============================================================

const SCOPE_TAGS = [
  // Work Type
  { tag: 'UX Research & Testing',      kw: ['ux research','usability testing','user research','user testing','usability study','user interviews','user-centered research'] },
  { tag: 'Human-Centered Design',       kw: ['human centered design','human-centered design','hcd','design thinking','service design','experience design'] },
  { tag: 'Accessibility / 508',         kw: ['accessibility','section 508','508 compliance','ada compliance','wcag'] },
  { tag: 'Communications Strategy',     kw: ['communications strategy','communications plan','communications support','communications services','strategic communications'] },
  { tag: 'Health Communications',       kw: ['health communications','public health campaign','health messaging','health outreach','health education','disease prevention campaign'] },
  { tag: 'Outreach & Engagement',       kw: ['outreach','stakeholder engagement','community engagement','public engagement','employer outreach','education campaign'] },
  { tag: 'Content Development',         kw: ['content development','content creation','content strategy','plain language','web content','editorial'] },
  { tag: 'Digital Marketing',           kw: ['digital marketing','paid media','social media','digital campaign','advertising','marketing platform','lead generation'] },
  { tag: 'Branding & Visual Design',    kw: ['branding','brand strategy','graphic design','visual design','logo','identity','creative services'] },
  { tag: 'Video & Multimedia',          kw: ['video production','multimedia','photography','motion graphics','animation','visual communications','audiovisual'] },
  { tag: 'Web Development',             kw: ['web development','web design','website redesign','frontend','drupal','wordpress','portal','web application'] },
  { tag: 'Digital Platform',            kw: ['digital platform','digital services','digital transformation','digital experience','information architecture'] },
  { tag: 'App Modernization',           kw: ['application modernization','app modernization','legacy modernization','system modernization','software modernization'] },
  { tag: 'Cloud Migration',             kw: ['cloud migration','cloud transition','cloud modernization','aws','azure','cloud infrastructure','cloud platform'] },
  { tag: 'Data Analytics',              kw: ['data analytics','data analysis','business intelligence','reporting','dashboard','data visualization','analytics platform'] },
  { tag: 'Data Engineering',            kw: ['data engineering','data management','data architecture','data pipeline','data governance','etl','data quality'] },
  { tag: 'AI / Machine Learning',       kw: ['artificial intelligence','machine learning','ai/ml','generative ai','llm','predictive analytics','nlp'] },
  { tag: 'Survey & Research',           kw: ['survey','survey design','survey methodology','data collection','research support','evaluation','program evaluation'] },
  { tag: 'Behavioral Science',          kw: ['behavioral science','behavioral research','behavior change','social marketing','nudge','command climate'] },
  { tag: 'IT Program Management',       kw: ['it program management','it governance','enterprise architecture','it portfolio','it strategy','cio support'] },
  { tag: 'DevSecOps',                   kw: ['devsecops','devops','ci/cd','agile','scrum','sprint','iterative development'] },
  { tag: 'Cybersecurity',               kw: ['cybersecurity','fisma','zero trust','splunk','soc','security operations','vulnerability','ato'] },
  { tag: 'Training & eLearning',        kw: ['training','elearning','e-learning','instructional design','lms','curriculum development','learning management'] },
  { tag: 'CRM / Salesforce',            kw: ['crm','salesforce','microsoft dynamics','customer relationship management','servicenow'] },
  { tag: 'Scientific/Technical Support',kw: ['scientific support','technical support','laboratory','research program','fisheries','biological','environmental'] },
  { tag: 'Translation / Language',      kw: ['translation','spanish language','multilingual','language services','interpretation'] },
];

// Scope tags BLN24 can credibly claim based on confirmed contract wins
// Anything NOT in this set = gap flag (we see the need but can't prime it cleanly)
const BLN24_OWNED_TAGS = new Set([
  'Human-Centered Design',       // IRS $7M HCD BPA, Census, CBP
  'UX Research & Testing',       // IRS HCD, Census UX
  'Accessibility / 508',         // IRS HCD BPA scope included 508
  'Communications Strategy',     // CMS MNPS, HUD, CDC
  'Health Communications',       // CDC DDT, CDC NAC, CDC NCHS, HHS OIDP
  'Outreach & Engagement',       // HUD FHEO, USCIS (potential), HRSA
  'Content Development',         // CMS MNPS notice production, CDC
  'Digital Marketing',           // USDA social media, CDC
  'Branding & Visual Design',    // MBDA website, Census design services
  'Video & Multimedia',          // CDC NCHS $3.6M, USDA, DOI, VA
  'Web Development',             // MBDA $4.4M, Census DWS, Oversight.gov
  'Digital Platform',            // Census DWS, MBDA, CBP.gov (Clarity24)
  'App Modernization',           // NOAA (Clarity24), Census MAF/TIGER
  'Cloud Migration',             // NOAA NWS IDP (Clarity24), Census cloud
  'Data Analytics',              // Census SRQA, Dept of Education EDARMST
  'Data Engineering',            // Census SRQA, MAF/TIGER
  'Survey & Research',           // USPTO survey (Fors Marsh), Census data collection
  'Behavioral Science',          // DHRA command climate (Fors Marsh)
  'Translation / Language',      // CMS Spanish language media campaign
]);

// Tags that appear in opps but BLN24 cannot credibly prime without a partner
const BLN24_GAP_TAGS = new Set([
  'AI / Machine Learning',       // We have data analytics but not deep AI/ML prime
  'Cybersecurity',               // No cyber prime delivery on record
  'DevSecOps',                   // No DevSecOps prime on record
  'IT Program Management',       // No CIO-shop IT mgmt prime on record
  'CRM / Salesforce',            // No CRM implementation prime on record
  'Scientific/Technical Support',// Not a BLN24 lane
  'Training & eLearning',        // Not a confirmed prime lane
]);

function extractScopeTags(text) {
  const t = text.toLowerCase();
  return SCOPE_TAGS.filter(s => s.kw.some(k => t.includes(k))).map(s => s.tag);
}

function classifyScopeTags(tags) {
  const owned = tags.filter(t => BLN24_OWNED_TAGS.has(t));
  const gaps  = tags.filter(t => BLN24_GAP_TAGS.has(t));
  const neutral = tags.filter(t => !BLN24_OWNED_TAGS.has(t) && !BLN24_GAP_TAGS.has(t));
  return { owned, gaps, neutral };
}

// =============================================================
// BLN24 PROVEN CAPABILITY LANES
// Derived from actual contract wins — NOT just NAICS codes
// Each lane: keywords that match real scopes BLN24 has delivered
// =============================================================

// LANE 1: Human-Centered Design & CX
// Proven: IRS HCD BPA $7M, Census UX work, CBP CX (Clarity24)
// Evidence: "Human Centered Design and Research", "Digital Transformation", CX on federal web platforms
const LANE_HCD = [
  'human centered design', 'human-centered design', 'hcd',
  'user experience', 'ux research', 'ux design',
  'service design', 'usability', 'usability testing',
  'human factors', 'user research', 'design research',
  'accessibility', 'section 508', '508 compliance',
  'customer experience', 'cx strategy',
  'user-centered', 'design thinking',
];

// LANE 2: Strategic Communications & Outreach
// Proven: CMS MNPS $16M, CDC comms $3.9M, HUD comms $2M, NTIA, HRSA, HHS OIDP $10M
// Evidence: notice production, health comms, multicultural outreach, digital campaigns
const LANE_COMMS = [
  'communications support', 'communications services', 'outreach',
  'public affairs', 'stakeholder engagement', 'stakeholder communications',
  'health communications', 'health messaging',
  'media campaign', 'marketing campaign', 'digital campaign',
  'content strategy', 'content development', 'content creation',
  'notice production', 'plain language',
  'branding', 'brand strategy',
  'social media', 'digital media',
  'multicultural', 'spanish language', 'multilingual',
  'public health campaign', 'awareness campaign',
  'paid media', 'advertising',
];

// LANE 3: Data Analytics, BI & Digital Platforms
// Proven: Census SRQA $4.1M (AI/ML/data), EDL $4.5M, EDARMST $2.9M (data analytics), GA4
// Evidence: data archiving, quality assurance, analytics platforms, risk management
const LANE_DATA = [
  'data analytics', 'data analysis', 'data management',
  'business intelligence', 'bi dashboard', 'dashboard development',
  'data engineering', 'data architecture', 'data governance',
  'machine learning', 'artificial intelligence', 'ai/ml',
  'statistical analysis', 'quantitative analysis',
  'risk management', 'data quality', 'data archiving',
  'analytics platform', 'reporting platform',
  'survey methodology', 'survey support', 'survey design',
  'research support', 'research services',
];

// LANE 4: Web Modernization & Digital Services
// Proven: MBDA website $4.4M, Census Digital Web Services, CNMP UX/digital, Oversight.gov $387K
// Evidence: website redesign, digital platforms, web development, CMS implementations
const LANE_WEB = [
  'website redesign', 'website design', 'web design',
  'web development', 'web modernization', 'digital modernization',
  'digital services', 'digital platform',
  'content management system', 'cms implementation',
  'web application', 'portal development',
  'digital transformation', 'digital experience',
  'drupal', 'wordpress', 'sharepoint',
  'front-end', 'frontend', 'ui development',
  'information architecture',
];

// LANE 5: Cloud & Application Modernization
// Proven: NOAA NWS IDP Cloud $4.3M (Clarity24), MAF/TIGER Cloud $4.5M, NOAA AI mod $2.8M
// Evidence: cloud migration, app modernization, devops, AWS/Azure work
const LANE_CLOUD = [
  'cloud migration', 'cloud transition', 'cloud modernization',
  'application modernization', 'app modernization', 'legacy modernization',
  'devops', 'devsecops', 'ci/cd',
  'aws', 'azure', 'google cloud', 'cloud infrastructure',
  'microservices', 'containerization', 'kubernetes',
  'software modernization', 'system modernization',
  'it modernization', 'platform modernization',
];

// LANE 6: Multimedia, Video & Visual Communications
// Proven: CDC NCHS Visual Comms $3.6M, multiple video/photo contracts, USDA social media
// Evidence: video production, photography, visual design, multimedia
const LANE_MULTIMEDIA = [
  'video production', 'video development', 'multimedia',
  'photography', 'photo services',
  'visual communications', 'visual design', 'graphic design',
  'motion graphics', 'animation',
  'social media content', 'digital content',
  'creative services', 'creative production',
  'infographics', 'data visualization',
];

// LANE 7: Behavioral Science & Research (BLN Fors Marsh)
// Proven: DHRA Command Climate $1M, USPTO survey support, FTC targeted campaigns
// Evidence: behavioral research, survey methodology, command climate
const LANE_BEHAVIORAL = [
  'behavioral science', 'behavioral research',
  'survey methodology', 'survey design', 'survey administration',
  'command climate', 'organizational climate',
  'focus group', 'qualitative research', 'ethnographic',
  'behavior change', 'social marketing',
  'evaluation', 'program evaluation',
  'research and analytics',
];

function isFederal(agencyName) {
  const a = agencyName.toLowerCase();
  if (SLED_DISQUALIFIERS.some(k => a.includes(k))) return false;
  if (FEDERAL_POSITIVE.some(k => a.includes(k))) return true;
  // Default to false for ambiguous names
  return false;
}

function scoreOpp(o) {
  const agency = (o.agency || '').toLowerCase();
  const sa = (o.set_aside || '').toLowerCase();
  const title = (o.title || '').toLowerCase();
  const summary = (o.summary || '').toLowerCase();
  const description = (o.description || '').toLowerCase();
  // Use full description for matching — much richer signal than title/summary alone
  const combined = title + ' ' + summary + ' ' + description;
  let score = 0;
  const reasons = [];
  const matchedLanes = [];

  // -------------------------------------------------------
  // 1. PAST PERFORMANCE AGENCY MATCH
  // Most important signal — BLN24 wins repeat clients
  // -------------------------------------------------------
  // Agency match alone is necessary but not sufficient
  // Weight kept moderate — capability lane match does the heavy lifting
  if (BLN24_AGENCIES.some(a => agency.includes(a))) {
    score += 15;
    reasons.push('Agency: BLN24 has past performance here (relationship + credibility advantage)');
  } else if (CLARITY24_AGENCIES.some(a => agency.includes(a))) {
    score += 12;
    reasons.push('Agency: Clarity24 JV (BLN24 + Accenture) has past performance here');
  } else if (FORS_MARSH_AGENCIES.some(a => agency.includes(a))) {
    score += 12;
    reasons.push('Agency: BLN Fors Marsh JV has past performance here');
  }

  // -------------------------------------------------------
  // 2. CAPABILITY LANE MATCHING
  // Score based on proven delivery lanes, not NAICS codes
  // Points awarded per lane match; multiple lanes = stronger case
  // -------------------------------------------------------

  const hcdMatches = LANE_HCD.filter(k => combined.includes(k));
  if (hcdMatches.length >= 2) {
    score += 25;
    matchedLanes.push('HCD/UX (IRS $7M, Census, CBP — proven prime)');
    reasons.push('Strong HCD/UX scope match — BLN24 proven prime (IRS $7M HCD BPA, Census UX, CBP digital transformation)');
  } else if (hcdMatches.length === 1) {
    score += 12;
    matchedLanes.push('HCD/UX (partial match)');
    reasons.push('Partial HCD/UX scope match — verify fit vs IRS/Census delivery experience');
  }

  const commsMatches = LANE_COMMS.filter(k => combined.includes(k));
  if (commsMatches.length >= 2) {
    score += 25;
    matchedLanes.push('Strategic Comms (CMS $16M, CDC $3.9M, HUD $2M — proven prime)');
    reasons.push('Strong comms/outreach scope match — BLN24 proven prime (CMS MNPS $16M, CDC health comms, HUD FHEO outreach)');
  } else if (commsMatches.length === 1) {
    score += 12;
    matchedLanes.push('Strategic Comms (partial)');
    reasons.push('Partial comms scope match — verify fit vs CMS/CDC/HUD delivery experience');
  }

  const dataMatches = LANE_DATA.filter(k => combined.includes(k));
  if (dataMatches.length >= 2) {
    score += 20;
    matchedLanes.push('Data/Analytics (Census $4.1M SRQA, Dept of Education $2.9M — proven prime)');
    reasons.push('Strong data/analytics scope match — BLN24 proven prime (Census SRQA AI/ML, Education EDARMST risk analytics)');
  } else if (dataMatches.length === 1) {
    score += 10;
    matchedLanes.push('Data/Analytics (partial)');
    reasons.push('Partial data/analytics scope match — verify fit vs Census/Education delivery experience');
  }

  const webMatches = LANE_WEB.filter(k => combined.includes(k));
  if (webMatches.length >= 2) {
    score += 20;
    matchedLanes.push('Web/Digital Platforms (MBDA $4.4M, Census DWS, Oversight.gov — proven prime)');
    reasons.push('Strong web modernization scope match — BLN24 proven prime (MBDA website $4.4M, Census DWS, Oversight.gov)');
  } else if (webMatches.length === 1) {
    score += 10;
    matchedLanes.push('Web/Digital (partial)');
    reasons.push('Partial web/digital scope match — verify fit vs MBDA/Census delivery experience');
  }

  const cloudMatches = LANE_CLOUD.filter(k => combined.includes(k));
  if (cloudMatches.length >= 2) {
    score += 20;
    matchedLanes.push('Cloud/App Mod (NOAA $7M via Clarity24 — JV prime)');
    reasons.push('Strong cloud/app modernization match — Clarity24 JV proven prime (NOAA cloud migration $7M, MAF/TIGER cloud)');
  } else if (cloudMatches.length === 1) {
    score += 10;
    matchedLanes.push('Cloud/App Mod (partial)');
    reasons.push('Partial cloud/modernization match — Clarity24 JV has NOAA cloud delivery experience');
  }

  const multimediaMatches = LANE_MULTIMEDIA.filter(k => combined.includes(k));
  if (multimediaMatches.length >= 2) {
    score += 15;
    matchedLanes.push('Multimedia/Visual Comms (CDC NCHS $3.6M, USDA, DOI — proven prime)');
    reasons.push('Strong multimedia/visual comms match — BLN24 proven prime (CDC NCHS $3.6M, USDA social media, DOI video)');
  } else if (multimediaMatches.length === 1) {
    score += 8;
    matchedLanes.push('Multimedia (partial)');
    reasons.push('Partial multimedia scope match — verify fit vs CDC/USDA visual delivery experience');
  }

  const behavioralMatches = LANE_BEHAVIORAL.filter(k => combined.includes(k));
  if (behavioralMatches.length >= 2) {
    score += 15;
    matchedLanes.push('Behavioral Science/Research (DHRA, USPTO via BLN Fors Marsh JV)');
    reasons.push('Strong behavioral/research scope match — BLN Fors Marsh JV proven (DHRA climate research, USPTO survey support)');
  } else if (behavioralMatches.length === 1) {
    score += 8;
    reasons.push('Partial behavioral/research match — BLN Fors Marsh JV has delivery experience');
  }

  // -------------------------------------------------------
  // 3. SET-ASIDE
  // -------------------------------------------------------
  if (sa.includes('8a') || sa.includes('8(a)')) {
    score += 20;
    reasons.push('8(a) set-aside — direct vehicle match for BLN24');
  } else if (sa.includes('sba') || sa.includes('small business') || sa.includes('wosb') || sa.includes('sdvosb')) {
    score += 10;
    reasons.push('Small business set-aside');
  } else if (!sa || sa.toLowerCase().includes('full and open') || sa.toLowerCase().includes('unrestricted')) {
    score -= 10;
    reasons.push('Full & Open — competing against all firm sizes; lower win probability without incumbent advantage');
  }

  // -------------------------------------------------------
  // 4. OUT OF SCOPE PENALTY
  // Hard pass signals based on actual BLN24 non-deliverables
  // -------------------------------------------------------
  const oos = [
    'medical device','medical equipment','laboratory equipment',
    'construction','facilities management','hvac','janitorial','custodial',
    'logistics','warehousing','supply chain','food service',
    'vehicle','aircraft','vessel','ship','weapon','ammunition','firearms',
    'hardware procurement','equipment procurement',
    'security guard','physical security',
  ];
  const oosHit = oos.filter(k => combined.includes(k));
  if (oosHit.length > 0) {
    score -= 40;
    reasons.push('OUT OF SCOPE: ' + oosHit.slice(0,2).join(', ') + ' — not in BLN24 delivery lanes');
  }

  // -------------------------------------------------------
  // 5. NO CAPABILITY MATCH PENALTY
  // If no lane matched at all, this is a speculative opp
  // -------------------------------------------------------
  if (matchedLanes.length === 0 && !reasons.some(r => r.includes('OUT OF SCOPE'))) {
    score -= 15;
    reasons.push('No direct capability lane match found — scope may not align with BLN24 proven delivery');
  }

  // -------------------------------------------------------
  // 6. TIER (context only, no score impact)
  // -------------------------------------------------------
  const midVal = (o.val_low && o.val_high) ? (o.val_low + o.val_high) / 2 : (o.val_low || o.val_high || null);
  let tier = null;
  if (midVal !== null) {
    if (midVal >= 20000000) tier = 1;
    else if (midVal >= 5000000) tier = 2;
    else if (midVal >= 500000) tier = 3;
  }

  let winProb;
  if (score >= 60) winProb = 'High (40-60%)';
  else if (score >= 35) winProb = 'Medium (20-40%)';
  else if (score >= 15) winProb = 'Low (10-20%)';
  else winProb = 'Very Low (<10%)';

  return { score, reasons, winProb, tier, matchedLanes };
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
          // Full description text for deeper scope analysis
          description: (r.description_text || '').substring(0, 2000),
          summary: (r.ai_summary || '').substring(0, 600),
          path: r.path || '',
          // Source path = actual SAM.gov or agency solicitation URL
          source_path: r.source_path || '',
          // Contact info
          contact_email: (r.primary_contact_email || {}).contact_email || '',
          contact_name: (r.primary_contact_email || {}).contact_name || '',
          is8a: sa.toLowerCase().includes('8a') || sa.toLowerCase().includes('8(a)'),
          isFullOpen,
          ericAlso: search.ericAlso || false,
        };

        const { score, reasons, winProb, tier, matchedLanes } = scoreOpp(opp);
        opp.capture_score = score;
        opp.win_reasons = reasons;
        opp.win_prob = winProb;
        opp.tier = tier;
        opp.matched_lanes = matchedLanes || [];
        // Scope tags: what type of work is this opp actually asking for
        const rawTags = extractScopeTags((opp.title||'') + ' ' + (opp.summary||'') + ' ' + (opp.description||''));
        const { owned, gaps, neutral } = classifyScopeTags(rawTags);
        opp.scope_tags = rawTags;
        opp.scope_owned = owned;   // BLN24 can credibly claim these
        opp.scope_gaps  = gaps;    // BLN24 sees these needs but can't prime them cleanly
        // Penalize opps where the primary need is a gap lane with no owned match
        if (gaps.length > 0 && owned.length === 0) {
          opp.capture_score = Math.max(0, opp.capture_score - 15);
          opp.win_reasons = [...(opp.win_reasons||[]), '⚠️ Scope gap: ' + gaps.join(', ') + ' — BLN24 has no confirmed prime delivery in these lanes'];
        } else if (gaps.length > 0) {
          opp.win_reasons = [...(opp.win_reasons||[]), '⚠️ Gap area detected: ' + gaps.join(', ') + ' — would need a teaming partner for this scope'];
        }

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

  // Run capability matrix enrichment
  const { execSync: es } = require('child_process');
  const tmpFile = OUT_FILE + '.tmp';
  fs.writeFileSync(tmpFile, JSON.stringify({ updated: new Date().toISOString(), count: allOpps.length, opps: allOpps }, null, 2));
  fs.renameSync(tmpFile, OUT_FILE);
  try {
    es(`python3 /Users/t24/Desktop/T24/hg-proxy/enrich-opps.py`, { stdio: 'inherit' });
    es(`python3 /Users/t24/Desktop/T24/hg-proxy/analyze-opps.py`, { stdio: 'inherit' });
  } catch(e) { console.log('Enrichment error:', e.message); }

  const output = JSON.parse(fs.readFileSync(OUT_FILE, 'utf8'));
  console.log(`Written ${output.opps.length} federal opps to ${OUT_FILE}`);

  try {
    execSync(`cd ${DASHBOARD_DIR} && git add opps.json && git diff --cached --quiet || (git commit -m "Update opps ${today}" && git push)`, { stdio: 'inherit' });
  } catch(e) {
    console.log('Git note:', e.message);
  }
}

main().catch(console.error);
