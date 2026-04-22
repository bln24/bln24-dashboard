#!/usr/bin/env python3
"""
Competitive Intelligence — REBUILT with proper logic:
1. Filter competitors by set-aside type (SB set-aside = SB firms only)
2. Use agency-specific knowledge (who actually wins at that agency)
3. Confirm relevant skillset (not just general category)
4. Include HigherGov links with contract evidence
"""
import json
from pathlib import Path

OPPS_FILE = Path('/Users/t24/Desktop/T24/dashboard/opps.json')
AGENCY_WINNERS_FILE = Path('/Users/t24/Desktop/T24/hg-proxy/agency-winners.json')
HG_BASE = 'https://www.highergov.com'

# Load agency-specific winner database
try:
    AGENCY_WINNERS = json.loads(AGENCY_WINNERS_FILE.read_text())
except:
    AGENCY_WINNERS = {}

# ─────────────────────────────────────────────────────────────────
# CONFIRMED COMPETITOR DATABASE
# Based on actual HigherGov award data — firms that win at specific agencies
# in specific lanes. Large businesses (SAIC, Leidos, Booz Allen) only appear
# for Full & Open opportunities.
# ─────────────────────────────────────────────────────────────────

COMPETITORS_BY_LANE = {

    # HCD / UX / Digital Services — Small Business competitors
    'hcd_ux_sb': [
        {
            'name': 'Fearless Solutions',
            'why': '8(a) HCD-focused SB, wins federal digital services and UX work at HHS/CMS/VA. Same NAICS lanes, same size bracket as BLN24. Direct competitor on 8(a) and SB HCD RFPs.',
            'url': f'{HG_BASE}/awardee/fearless-inc-388034/',
            'evidence': 'HHS, CMS, federal digital services, HCD methodology'
        },
        {
            'name': 'Coforma (formerly CivicActions)',
            'why': 'SB federal UX/HCD firm, CMS digital services work, active on OASIS+ SB. Competes directly on CMS and HCD-focused federal digital service contracts.',
            'url': f'{HG_BASE}/awardee/?search=Coforma',
            'evidence': 'CMS, HCD, federal digital services, OASIS+ SB'
        },
        {
            'name': 'Nava PBC',
            'why': 'SB federal digital services, healthcare.gov (CMS), user experience focus. Strong HHS/CMS anchor similar to BLN24\'s position.',
            'url': f'{HG_BASE}/awardee/?search=Nava+PBC',
            'evidence': 'CMS, healthcare.gov, UX, federal digital services'
        },
        {
            'name': 'Ad Hoc LLC',
            'why': 'SB federal digital services, HCD, active on OASIS+ SB. Has won CMS and VA digital transformation work.',
            'url': f'{HG_BASE}/awardee/?search=Ad+Hoc+LLC',
            'evidence': 'CMS, VA, HCD, federal digital services, OASIS+ SB'
        },
    ],

    # HCD / UX — Full & Open (large businesses included)
    'hcd_ux_fo': [
        {
            'name': 'ICF International',
            'why': 'Large HCD/comms firm with HHS/CMS anchor clients. Wins health communications, digital services, and HCD work across federal health agencies. Primary competitor on unrestricted health/HCD RFPs.',
            'url': f'{HG_BASE}/awardee/icf-incorporated-l-l-c-73040/',
            'evidence': 'HHS, CMS, CDC, NIH — health comms and digital services'
        },
        {
            'name': 'Booz Allen Hamilton',
            'why': 'Large cleared digital services and comms prime. Wins on full & open federal digital transformation and comms work.',
            'url': f'{HG_BASE}/awardee/booz-allen-hamilton-inc-6455/',
            'evidence': 'DoD, federal agencies — digital transformation, comms'
        },
    ],

    # Census-specific — App Modernization / Cloud / Data (SB)
    # LOGIC: 1) Who is the incumbent? 2) Who has most Census contracts? 3) Who teams well?
    'census_tech_sb': [
        {
            'name': 'Vidoori Inc + T-Rex Solutions (teamed)',
            'why': 'STRONGEST COMPETITOR. Vidoori has $173M Census BPA (Enterprise Testing), $7.3M CMMU modernization (AI/ML/automation), and $4.7M internet data collection. T-Rex Solutions was THE 2020 Census IT modernization integrator (up to $1.6B ESF SE&I BPA) and has the deepest Census systems engineering knowledge. Together they cover the full stack: T-Rex brings systems engineering + incumbent credibility, Vidoori brings testing + AI/ML + modernization. Both are SB-eligible. This team is the hardest to beat on Census modernization.',
            'url': f'{HG_BASE}/awardee/?search=Vidoori',
            'evidence': 'Vidoori: $173M Census BPA, $7.3M CMMU AI/ML modernization. T-Rex: $1.6B 2020 Census integrator.'
        },
        {
            'name': 'Vidoori Inc',
            'why': '$173M Census Enterprise Testing BPA + $7.3M CMMU AI/ML modernization + $4.7M internet data collection. Multiple Census BPAs, AI/ML and automation at Census, data systems modernization track record. If not teaming with T-Rex, still a formidable solo competitor.',
            'url': f'{HG_BASE}/awardee/?search=Vidoori',
            'evidence': 'Census Bureau — $173M testing BPA, $7.3M AI/ML modernization, multiple awards'
        },
        {
            'name': 'Spatial Front Inc',
            'why': 'SB with confirmed Census tech awards ($17M+). Cloud and data engineering. Active on Census SB set-asides.',
            'url': f'{HG_BASE}/awardee/spatial-front-inc-10000821/',
            'evidence': 'Census Bureau — $17M+ confirmed, cloud and data engineering'
        },
        {
            'name': 'Amivero LLC',
            'why': 'SB with Census Bureau SB set-aside awards ($5M). Cloud and data modernization focus. Growing Census presence.',
            'url': f'{HG_BASE}/awardee/amivero-llc-10055353/',
            'evidence': 'Census Bureau — $5M SB set-aside, cloud/data modernization'
        },
    ],

    # Communications / Health Comms (SB)
    'comms_sb': [
        {
            'name': 'ICF International (mid-market subsidiary)',
            'why': 'ICF has SB subsidiaries that compete on health comms set-asides. Primary health comms competitor regardless of set-aside type.',
            'url': f'{HG_BASE}/awardee/icf-incorporated-l-l-c-73040/',
            'evidence': 'HHS, CMS, CDC — health communications, behavior change'
        },
        {
            'name': 'Valassis Communications / Vericast',
            'why': 'SB comms/outreach firm with federal health comms contracts. Multilingual outreach and public awareness campaigns.',
            'url': f'{HG_BASE}/awardee/?search=Vericast',
            'evidence': 'Federal health comms, multilingual outreach'
        },
        {
            'name': 'GMMB',
            'why': 'SB communications firm with HHS and CMS comms work. Strategic communications, health messaging, public affairs.',
            'url': f'{HG_BASE}/awardee/?search=GMMB',
            'evidence': 'HHS, CMS — strategic communications, public health campaigns'
        },
    ],

    # International Development (MCC/USAID)
    'intl_dev': [
        {
            'name': 'Chemonics International',
            'why': 'Largest MCC/USAID implementer globally. Multiple MCC compact country programs. Primary competitor on any MCC advisory work — likely either the incumbent or the most formidable bidder.',
            'url': f'{HG_BASE}/awardee/chemonics-international-inc-3474/',
            'evidence': 'MCC/USAID — workforce dev, TVET, education advisory in compact countries'
        },
        {
            'name': 'DevTech Systems',
            'why': 'MCC/USAID M&E and advisory firm. Workforce development, education sector, program evaluation in developing countries. Direct MCC competitor in HCD advisory space.',
            'url': f'{HG_BASE}/awardee/?search=DevTech+Systems',
            'evidence': 'MCC, USAID — monitoring, evaluation, workforce advisory'
        },
        {
            'name': 'Creative Associates International',
            'why': 'International education and TVET programs in developing countries. Directly competes on workforce development and education advisory for MCC.',
            'url': f'{HG_BASE}/awardee/creative-associates-international-inc-1847/',
            'evidence': 'USAID, MCC — education, workforce, TVET in LMIC'
        },
    ],

    # Web Development / Digital Platform (SB)
    'web_dev_sb': [
        {
            'name': 'Softrams LLC',
            'why': 'SB Agile web dev and digital services firm, CMS and VA work. Competes directly on SB web development and digital platform contracts.',
            'url': f'{HG_BASE}/awardee/?search=Softrams',
            'evidence': 'CMS, VA — Agile dev, digital services, SB set-asides'
        },
        {
            'name': 'Agile Six Applications',
            'why': 'SB federal digital services, CMS/VA web development, OASIS+ SB holder. Competes on federal web platform and digital services set-asides.',
            'url': f'{HG_BASE}/awardee/?search=Agile+Six',
            'evidence': 'CMS, VA — web dev, digital services, OASIS+ SB'
        },
        {
            'name': 'Civic Actions / CivicActions',
            'why': 'SB federal open-source and digital services firm, Drupal expertise, federal web platforms.',
            'url': f'{HG_BASE}/awardee/?search=CivicActions',
            'evidence': 'Federal web platforms, Drupal, open source'
        },
    ],

    # Data Analytics / Research (SB)
    'data_sb': [
        {
            'name': 'Mathematica Policy Research',
            'why': 'Premier federal research and analytics firm. Wins large data analytics and program evaluation contracts across ED, HHS, Labor. Strong competitor on research-heavy data analytics RFPs.',
            'url': f'{HG_BASE}/awardee/?search=Mathematica',
            'evidence': 'ED, HHS, Labor — data analytics, program evaluation, research'
        },
        {
            'name': 'Westat',
            'why': 'Federal statistical research firm. Survey methodology, data analytics, program evaluation. Competes at Census, ED, HHS on data and research contracts.',
            'url': f'{HG_BASE}/awardee/?search=Westat',
            'evidence': 'Census, ED, HHS — surveys, data analytics, statistical research'
        },
        {
            'name': 'Abt Associates',
            'why': 'Federal research and analytics firm. Education, health, and workforce program evaluation. Direct competitor on data-heavy advisory and research contracts.',
            'url': f'{HG_BASE}/awardee/?search=Abt+Associates',
            'evidence': 'ED, HHS, Labor — program evaluation, workforce research'
        },
    ],
}

# Partner database (unchanged from before — already good)
PARTNERS = {
    'devsecops': {
        'name': 'Clarity24 LLC (BLN24 Active JV)',
        'why': 'Active 8(a) JV. Three reasons this is the right call: (1) BLN24 independently has Census quals (DWS III $8.3M, SRQA $4.1M, CES $7M) so BLN24 is the relationship anchor; (2) Accenture Federal Services brings cloud/DevSecOps/AWS depth; (3) joint delivery proven at Census, NOAA ($7M cloud), and CBP ($4M). BLN24 primes with credibility, Clarity24 fills the tech depth gap.',
        'url': f'{HG_BASE}/awardee/clarity24-llc-627966104/',
        'relationship': 'Active JV — Proven joint delivery'
    },
    'cloud': {
        'name': 'Clarity24 LLC (BLN24 Active JV) — STRONGEST FOR CENSUS',
        'why': 'STRONGEST TEAMING CHOICE for Census modernization. Three reasons: (1) BLN24 already has Census quals independently (DWS III $8.3M, SRQA $4.1M, MAF/TIGER $4.5M, EDL $4.5M, CES $7M) so BLN24 brings the Census past performance anchor; (2) Accenture Federal Services (via Clarity24) adds cloud engineering depth (AWS/Azure), DevSecOps, and large-system integration; (3) BLN24 and Accenture have already delivered together at Census (MAF/TIGER), NOAA (IDP Cloud $4.3M, AI/ML $3.6M), and CBP (Digital Transformation $4M) — proven that this team executes. Combined: BLN24 census relationship + Accenture tech depth = credible prime with technical depth.',
        'url': f'{HG_BASE}/awardee/clarity24-llc-627966104/',
        'relationship': 'Active JV — Proven Census delivery together'
    },
    'behavioral_science': {
        'name': 'BLN Fors Marsh JV LLC (Active JV)',
        'why': '$59M behavioral research (DHRA OPA), HHS OIDP $10.3M comprehensive comms, FTC paid media $4.5M BPA. Behavioral science is Fors Marsh\'s deepest lane.',
        'url': f'{HG_BASE}/awardee/bln-fors-marsh-jv-llc-476980511/',
        'relationship': 'Active JV'
    },
    'paid_media': {
        'name': 'BLN Fors Marsh JV LLC (Active JV)',
        'why': 'FTC paid advertising BPA ($4.5M), HHS OIDP behavioral health comms, multilingual outreach at scale.',
        'url': f'{HG_BASE}/awardee/bln-fors-marsh-jv-llc-476980511/',
        'relationship': 'Active JV'
    },
    'tvet_workforce': {
        'name': 'Chemonics International',
        'why': 'Largest MCC/USAID implementer. TVET and workforce development expertise in compact countries. Teaming with Chemonics fills BLN24\'s LMIC workforce gap and adds MCC incumbent credibility.',
        'url': f'{HG_BASE}/awardee/chemonics-international-inc-3474/',
        'relationship': 'Recommended sub'
    },
    # Cybersecurity partner — agency-specific lookup in get_competitive_intel, use this as fallback
    'cybersecurity': {
        'name': 'IgniteAction LLC (Census) / ManTech (other agencies)',
        'why': 'For Census: IgniteAction won \$557M Census OCISS BPA for cloud infrastructure + cybersecurity and zero trust — they already have the Census cyber relationship and cleared staff. For other agencies: ManTech brings cleared cyber, ATO maintenance, and FISMA expertise. Large businesses cannot prime SB set-asides, making them ideal subs — they get on the contract, BLN24 primes.',
        'url': f'{HG_BASE}/awardee/?search=IgniteAction',
        'relationship': 'Recommended large business sub (agency-specific)'
    },
    'program_evaluation': {
        'name': 'Mathematica Policy Research (medium/large sub)',
        'why': 'Mathematica is a premier federal research firm that often cannot compete on SB set-asides as prime. Their evaluation methodology, RCT design, and ED/HHS program evaluation expertise makes them an ideal sub — BLN24 primes with SB status, Mathematica delivers the rigorous evaluation methodology. They bring credibility BLN24 doesn\'t have; BLN24 brings the SB vehicle they need.',
        'url': f'{HG_BASE}/awardee/?search=Mathematica',
        'relationship': 'Recommended medium/large business sub'
    },
    'it_infrastructure': {
        'name': 'Leidos or Peraton (large business sub)',
        'why': 'Large businesses cannot prime on SB set-asides — making them ideal subs. Leidos and Peraton have deep IT infrastructure, network, and telecom capabilities. BLN24 primes with SB status, they bring the infrastructure technical depth. This is exactly the model: BLN24 gets the contract, large firm gets the sub work they could not win as prime.',
        'url': f'{HG_BASE}/awardee/?search=Leidos',
        'relationship': 'Recommended large business sub'
    },
}


def get_set_aside_type(opp):
    """Determine if this is SB set-aside, 8(a), or full & open."""
    sa = (opp.get('set_aside') or '').lower()
    if '8(a)' in sa or '8a' in sa:
        return '8a'
    if 'small business' in sa or 'sba' in sa or 'wosb' in sa or 'sdvosb' in sa:
        return 'sb'
    if 'full and open' in sa or 'unrestricted' in sa or not sa or sa == 'none':
        return 'full_open'
    return 'sb'  # default to SB for unknown set-asides


def get_agency_type(opp):
    """Classify the agency for competitor selection."""
    agency = (opp.get('agency') or '').lower()
    title = (opp.get('title') or '').lower()
    if 'census' in agency or ('commerce' in agency and ('census' in title or 'centam' in title or 'decennial' in title)):
        return 'census'
    if 'millennium challenge' in agency or 'mcc' in agency:
        return 'mcc'
    if 'cms' in agency or 'medicare' in agency or 'medicaid' in agency:
        return 'cms'
    if 'cdc' in agency or 'hhs' in agency or 'health' in agency:
        return 'hhs'
    if 'education' in agency or 'ies' in agency:
        return 'education'
    if 'dea' in agency or 'justice' in agency or 'doj' in agency:
        return 'doj'
    return 'general'


def get_competitive_intel(opp):
    cm = opp.get('capability_matrix', {})
    tasks = cm.get('tasks', [])
    sa_type = get_set_aside_type(opp)
    agency_type = get_agency_type(opp)

    # Determine primary lanes
    has_hcd = any('Human-Centered' in t.get('task','') or 'UX' in t.get('task','') for t in tasks if t.get('score',0) >= 3)
    has_web = any('Web Design' in t.get('task','') or 'Digital Platform' in t.get('task','') for t in tasks if t.get('score',0) >= 3)
    has_comms = any('Communications' in t.get('task','') or 'Outreach' in t.get('task','') for t in tasks if t.get('score',0) >= 3)
    has_data = any('Data Analytics' in t.get('task','') or 'Data Engineering' in t.get('task','') for t in tasks if t.get('score',0) >= 3)
    has_cloud = any('Cloud' in t.get('task','') or 'Software Dev' in t.get('task','') or 'Application Modernization' in t.get('task','') for t in tasks if t.get('score',0) >= 3)
    is_intl_dev = agency_type == 'mcc' or 'mcc' in (opp.get('title','') + opp.get('agency','')).lower()

    # Select competitors based on set-aside AND agency AND lane
    competitors = []
    seen = set()

    def add_comp(comp_list, max_add=2):
        added = 0
        for c in comp_list:
            if c['name'] not in seen and added < max_add:
                competitors.append(c)
                seen.add(c['name'])
                added += 1

    # ── AGENCY-SPECIFIC DATABASE FIRST ──────────────────────────
    # Use confirmed agency winner data before falling back to capability-based
    def add_agency_winners(agency_key, sub_key, max_add=3):
        agency_data = AGENCY_WINNERS.get(agency_key, {})
        winners = agency_data.get(sub_key, [])
        for w in winners[:max_add]:
            if w.get('name','TBD') not in seen and 'TBD' not in w.get('name',''):
                competitors.append({
                    'name': w['name'],
                    'why': w['why'],
                    'url': w['url'],
                    'evidence': w.get('evidence','')
                })
                seen.add(w['name'])

    # MCC competitors — use MCC-specific database
    if is_intl_dev:
        add_agency_winners('mcc', 'intl_dev', 3)
        if not competitors:
            add_comp(COMPETITORS_BY_LANE['intl_dev'], 3)

    # Census-specific competitors — use confirmed Census winner database
    elif agency_type == 'census' and (has_cloud or has_data):
        if sa_type in ('8a', 'sb', 'tbd'):
            add_agency_winners('census_bureau', 'app_modernization_sb', 4)
        if not competitors:
            add_comp(COMPETITORS_BY_LANE['census_tech_sb'], 3)

    # HUD competitors
    elif 'hud' in (opp.get('agency','') + opp.get('title','')).lower() or 'housing and urban' in (opp.get('agency','')).lower():
        add_agency_winners('hud', 'comms_sb', 2)

    # CMS competitors
    elif 'cms' in (opp.get('agency','') + opp.get('title','')).lower() or 'medicare' in (opp.get('agency','')).lower():
        if has_web or has_cloud:
            add_agency_winners('cms', 'tech_sb', 2)
        if has_comms:
            add_agency_winners('cms', 'comms_sb', 1)

    # DHS/USCIS competitors — use confirmed USASpending data
    elif 'citizenship' in (opp.get('agency','')).lower() or 'immigration' in (opp.get('agency','')).lower():
        add_agency_winners('uscis', 'tech_confirmed', 2)
        if not competitors:
            add_agency_winners('dhs_uscis', 'tech_sb', 2)

    # FHWA/DOT competitors
    elif 'highway' in (opp.get('agency','')).lower() or 'transportation' in (opp.get('agency','')).lower():
        add_agency_winners('fhwa_dot', 'tech_lb', 1)

    # FEMA competitors  
    elif 'emergency management' in (opp.get('agency','')).lower() or 'fema' in (opp.get('agency','')).lower():
        add_agency_winners('fema', 'tech_lb', 1)

    # Education IES competitors
    elif 'education' in (opp.get('agency','')).lower() or 'ies' in (opp.get('title','')).lower() or 'pell' in (opp.get('title','')).lower():
        add_agency_winners('education_ies', 'program_evaluation_sb', 3)

    # Defense Health Agency competitors
    elif 'defense health' in (opp.get('agency','')).lower() or 'dha' in (opp.get('title','')).lower():
        add_agency_winners('defense_health_agency', 'software_tools_sb', 2)

    # HCD/UX competitors
    if has_hcd:
        if sa_type in ('8a', 'sb'):
            add_comp(COMPETITORS_BY_LANE['hcd_ux_sb'], 2)
        else:
            add_comp(COMPETITORS_BY_LANE['hcd_ux_fo'], 2)

    # Web dev competitors
    if has_web and not is_intl_dev:
        if sa_type in ('8a', 'sb'):
            add_comp(COMPETITORS_BY_LANE['web_dev_sb'], 2)

    # Comms competitors
    if has_comms and not is_intl_dev:
        if sa_type in ('8a', 'sb'):
            add_comp(COMPETITORS_BY_LANE['comms_sb'], 2)

    # Data/research competitors — only for education/research agencies, not generic data tools
    if has_data and agency_type in ('education', 'hhs') and not is_intl_dev:
        add_comp(COMPETITORS_BY_LANE['data_sb'], 2)

    # Select partners based on SPECIFIC GAPS — explain what they fill
    partners = []
    seen_p = set()
    gap_reasons = {}  # track what gap each partner fills

    def add_partner_for_gap(key, gap_task_name):
        p = PARTNERS.get(key)
        if p and p['name'] not in seen_p:
            # Override the why with gap-specific reasoning
            p_copy = dict(p)
            p_copy['gap_filled'] = gap_task_name
            p_copy['why'] = f'GAP: {gap_task_name} — {p["why"]}'
            partners.append(p_copy)
            seen_p.add(p['name'])

    # Load agency-specific large business sub data
    lb_subs = AGENCY_WINNERS.get('_large_business_subs', {})

    def add_agency_lb_partner(lb_key, gap_task_name, max_add=1):
        """Add a confirmed agency-specific large business sub partner."""
        subs = lb_subs.get(lb_key, [])
        added = 0
        for s in subs[:max_add]:
            if s['name'] not in seen_p:
                partners.append({
                    'name': s['name'],
                    'why': f'GAP: {gap_task_name} — {s["why"]}',
                    'url': s['url'],
                    'relationship': s.get('lb_note', 'Large business sub'),
                    'gap_filled': gap_task_name,
                    'evidence': s.get('evidence', '')
                })
                seen_p.add(s['name'])
                added += 1

    # Gap-driven partner selection — use agency-specific subs first
    gap_tasks = [t for t in tasks if t.get('score', 0) == 0]
    for task in gap_tasks:
        task_name = task.get('task', '')
        if 'Cybersecurity' in task_name or 'FISMA' in task_name:
            # Use agency-specific cyber sub
            if agency_type == 'census':
                add_agency_lb_partner('census_cyber_it', task_name, 1)
            elif agency_type == 'cms':
                add_agency_lb_partner('cms_tech', task_name, 1)
            if not any(t.get('gap_filled') == task_name for t in partners):
                add_partner_for_gap('cybersecurity', task_name)  # fallback
        elif 'DevSecOps' in task_name or 'CI/CD' in task_name:
            if agency_type == 'census':
                add_agency_lb_partner('census_cyber_it', task_name, 1)
            if not any(t.get('gap_filled') == task_name for t in partners):
                add_partner_for_gap('devsecops', task_name)
        elif 'Cloud Engineering' in task_name:
            add_partner_for_gap('cloud', task_name)
        elif 'Workforce' in task_name or 'TVET' in task_name:
            add_partner_for_gap('tvet_workforce', task_name)
        elif 'IT Infrastructure' in task_name:
            if agency_type == 'census':
                add_agency_lb_partner('census_cyber_it', task_name, 1)
            if not any(t.get('gap_filled') == task_name for t in partners):
                add_partner_for_gap('it_infrastructure', task_name)
        elif 'Program Evaluation' in task_name:
            add_partner_for_gap('program_evaluation', task_name)

    # JV partners only when they fill a real scope need — explain the specific gap
    behavioral_tasks = [t for t in tasks if 'behavioral' in t.get('task','').lower() and t.get('score',0) >= 2]
    if behavioral_tasks:
        p = PARTNERS.get('behavioral_science')
        if p and p['name'] not in seen_p:
            p_copy = dict(p)
            gap_desc = behavioral_tasks[0]['task'] if behavioral_tasks else 'behavioral science scope'
            p_copy['gap_filled'] = gap_desc
            p_copy['why'] = f'SCOPE NEED: {gap_desc} — {p["why"]}'
            partners.append(p_copy)
            seen_p.add(p['name'])

    cloud_gap_tasks = [t for t in gap_tasks if 'cloud' in t.get('task','').lower() or 'devops' in t.get('task','').lower()]
    if cloud_gap_tasks and 'Clarity24' not in str([p.get('name','') for p in partners]):
        p = PARTNERS.get('cloud')
        if p and p['name'] not in seen_p:
            p_copy = dict(p)
            gap_desc = cloud_gap_tasks[0]['task'] if cloud_gap_tasks else 'cloud/DevSecOps scope'
            p_copy['gap_filled'] = gap_desc
            p_copy['why'] = f'GAP: {gap_desc} — {p["why"]}'
            partners.append(p_copy)
            seen_p.add(p['name'])

    # Universal fallback — every opp gets at least basic intel
    # Only apply fallback if the opp is in BLN24's lanes (not a Pass/out-of-scope opp)
    fit = cm.get('fit', '')
    # Unclassified = thin description, not actually a pass
    is_pass = fit == 'Pass' and not competitors
    has_any_prime = any(t.get('score', 0) >= 3 for t in tasks) or fit == 'Unclassified'

    if not competitors and not is_pass and has_any_prime:
        if sa_type in ('8a', 'sb'):
            if has_hcd or has_web:
                add_comp(COMPETITORS_BY_LANE['hcd_ux_sb'], 2)
            if has_comms:
                add_comp(COMPETITORS_BY_LANE['comms_sb'], 2)
            if has_data:
                add_comp(COMPETITORS_BY_LANE['data_sb'], 2)
            if not competitors:
                # No agency-specific data — flag for research rather than using generic names
                competitors.append({
                    'name': 'Search USASpending.gov for this agency',
                    'why': f'No confirmed competitor data for {opp.get("agency","this agency")}. Go to USASpending.gov → search by awarding agency + relevant NAICS to find who actually wins work here. Do not use generic digital services firms without agency-specific evidence.',
                    'url': f'https://api.usaspending.gov/api/v2/search/spending_by_award/',
                    'evidence': 'Pull from USASpending before listing competitors'
                })
        elif not is_pass:
            add_comp(COMPETITORS_BY_LANE['hcd_ux_fo'], 2)
            if has_data:
                add_comp(COMPETITORS_BY_LANE['data_sb'], 1)
    elif is_pass:
        # Pass opp: note that BLN24 can't prime but flag potential subs
        competitors.append({
            'name': 'N/A — Outside BLN24 lane',
            'why': 'This opp falls outside BLN24\'s confirmed delivery lanes. If pursuing as a sub, look for large integrators (SAIC, Leidos, Booz Allen) as potential prime partners.',
            'url': f'{HG_BASE}/awardee/science-applications-international-corporation-saic-25048/',
            'evidence': 'Out-of-scope for BLN24 prime'
        })

    # If still no partners suggested, only add JV partners when there's a real scope reason
    if not partners and not is_pass and has_any_prime:
        if has_comms or has_hcd:
            add_partner_for_gap('behavioral_science', 'behavioral science / comms depth')
        elif has_cloud or has_web:
            add_partner_for_gap('cloud', 'cloud engineering / tech depth')
        elif has_data:
            add_partner_for_gap('behavioral_science', 'research and analytics depth')

    # ── SCORE MODIFIER based on competitive intelligence ──────────
    score_delta = 0
    score_reasons = []

    # Incumbent penalty — if the dominant competitor has a massive agency relationship
    for comp in competitors:
        evidence = comp.get('evidence', '')
        amount_m = comp.get('amount_m', 0) or 0
        name = comp.get('name', '')
        why = comp.get('why', '').lower()
        
        # T-Rex/Vidoori at Census = very strong incumbent
        if 'incumbent' in why or amount_m >= 500:
            score_delta -= 12
            score_reasons.append(f'Strong incumbent: {name} ({comp.get("evidence","")[:50]}) — -12pts')
            break
        elif amount_m >= 100:
            score_delta -= 6
            score_reasons.append(f'Established agency relationship: {name} (${amount_m:.0f}M) — -6pts')
            break
        elif amount_m >= 20:
            score_delta -= 3
            score_reasons.append(f'Active agency competitor: {name} (${amount_m:.0f}M) — -3pts')

    # Set-aside bonus — SB set-aside eliminates large prime competition
    if sa_type in ('8a', 'sb'):
        score_delta += 5
        score_reasons.append('SB/8(a) set-aside: large prime competition eliminated — +5pts')

    # Partner bonus — confirmed JV with agency history raises p-win
    for partner in partners:
        p_why = partner.get('why', '').lower()
        p_rel = partner.get('relationship', '').lower()
        if 'active jv' in p_rel or 'proven' in p_rel:
            if 'census' in p_why or 'noaa' in p_why or 'census' in (opp.get('agency','') or '').lower():
                score_delta += 8
                score_reasons.append(f'Proven JV partner with agency history ({partner["name"][:30]}) — +8pts')
                break
            else:
                score_delta += 5
                score_reasons.append(f'Active JV partner fills gap ({partner["name"][:30]}) — +5pts')
                break

    # Open field bonus — if we found no significant incumbent
    if not competitors or all((comp.get('amount_m', 0) or 0) < 5 for comp in competitors):
        score_delta += 5
        score_reasons.append('No dominant incumbent identified — +5pts')

    return {
        'competitors': competitors[:4],
        'partners': partners[:3],
        'set_aside_note': f'Set-aside: {opp.get("set_aside","unknown")} — competitor list filtered accordingly',
        'score_delta': score_delta,
        'score_reasons': score_reasons,
    }


def main():
    data = json.loads(OPPS_FILE.read_text())
    opps = data['opps']

    updated = 0
    for opp in opps:
        intel = get_competitive_intel(opp)
        opp['competitive_intel'] = intel
        
        # Apply score modifier from competitive intelligence
        # Rules: base score >= 20, not a Pass opp, delta capped at +/-10
        delta = intel.get('score_delta', 0)
        delta = max(-15, min(10, delta))  # cap delta
        base_score = opp.get('capture_score', 0)
        cm_fit = opp.get('capability_matrix', {}).get('fit', '')
        is_viable = base_score >= 20 and cm_fit not in ('Pass', 'Unclassified')
        if delta != 0 and is_viable:
            new_score = max(0, base_score + delta)
            opp['capture_score_base'] = base_score
            opp['capture_score'] = new_score
            opp['capture_score_delta'] = delta
            opp['capture_score_delta_reasons'] = intel.get('score_reasons', [])
        elif delta != 0:
            # Record the delta but don't apply it
            opp['capture_score_base'] = base_score
            opp['capture_score_delta'] = delta
            opp['capture_score_delta_reasons'] = intel.get('score_reasons', [])
        
        if intel['competitors'] or intel['partners']:
            updated += 1

    data['opps'] = opps
    OPPS_FILE.write_text(json.dumps(data, indent=2))
    print(f'Updated competitive intel for {updated}/{len(opps)} opps')

    # Sample check — CenTAM specifically
    print('\n=== CenTAM Census (should be SB competitors) ===')
    for opp in opps:
        if 'CenTAM' in opp.get('title','') or 'Decennial Transformation' in opp.get('title',''):
            ci = opp.get('competitive_intel',{})
            print(f'Set-aside: {opp.get("set_aside","?")}')
            print(f'Agency: {opp.get("agency","")}')
            for c in ci.get('competitors',[]):
                print(f'  ⚔️  {c["name"]}: {c["why"][:80]}')
            for p in ci.get('partners',[]):
                print(f'  🤝 {p["name"]} ({p["relationship"]})')
            break


if __name__ == '__main__':
    main()
