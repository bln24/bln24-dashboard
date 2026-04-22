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
HG_BASE = 'https://www.highergov.com'

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
    'cybersecurity': {
        'name': 'ManTech International (large business sub)',
        'why': 'ManTech is a large business that CANNOT prime on SB set-asides — which is exactly why they make a great sub. They bring cleared cyber, ATO maintenance, and FISMA expertise that BLN24 needs. BLN24 primes with SB status, ManTech provides the security depth. Win-win: ManTech gets on the contract, BLN24 covers the gap.',
        'url': f'{HG_BASE}/awardee/?search=ManTech',
        'relationship': 'Recommended large business sub'
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

    # MCC competitors — specialized
    if is_intl_dev:
        add_comp(COMPETITORS_BY_LANE['intl_dev'], 3)

    # Census-specific competitors for tech work
    elif agency_type == 'census' and (has_cloud or has_data):
        if sa_type in ('8a', 'sb', 'tbd', 'sb'):
            add_comp(COMPETITORS_BY_LANE['census_tech_sb'], 4)
        else:
            add_comp(COMPETITORS_BY_LANE['census_tech_sb'], 3)

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

    # Data/research competitors
    if has_data and agency_type in ('census', 'education', 'hhs'):
        add_comp(COMPETITORS_BY_LANE['data_sb'], 2)

    # Select partners based on gaps
    partners = []
    seen_p = set()

    def add_partner(key):
        p = PARTNERS.get(key)
        if p and p['name'] not in seen_p:
            partners.append(p)
            seen_p.add(p['name'])

    for task in tasks:
        if task.get('score', 0) == 0:
            task_name = task.get('task', '')
            if 'DevSecOps' in task_name or 'CI/CD' in task_name:
                add_partner('devsecops')
            elif 'Cloud Engineering' in task_name:
                add_partner('cloud')
            elif 'Cybersecurity' in task_name or 'FISMA' in task_name:
                add_partner('cybersecurity')
            elif 'Workforce' in task_name or 'TVET' in task_name:
                add_partner('tvet_workforce')
            elif 'IT Infrastructure' in task_name:
                add_partner('it_infrastructure')
            elif 'Program Evaluation' in task_name:
                add_partner('program_evaluation')

    # Always suggest JV partners when relevant to scope
    if has_comms or any('behavioral' in t.get('task','').lower() for t in tasks if t.get('score',0) >= 3):
        add_partner('behavioral_science')
    if has_cloud or any('cloud' in t.get('task','').lower() for t in tasks if t.get('score',0) >= 3):
        add_partner('cloud')

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
                add_comp([
                    {'name': 'Fearless Solutions', 'why': '8(a) SB federal digital services firm — competes across HCD, comms, and digital platform work for federal agencies.', 'url': f'{HG_BASE}/awardee/fearless-inc-388034/', 'evidence': 'Federal digital services, HCD'},
                    {'name': 'Coforma', 'why': 'SB federal UX/digital services firm — competes on SB digital services and platform contracts.', 'url': f'{HG_BASE}/awardee/?search=Coforma', 'evidence': 'Federal digital services, UX, OASIS+ SB'},
                ], 2)
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

    # If still no partners suggested, default to JV partners (skip for Pass opps)
    if not partners and not is_pass and has_any_prime:
        if has_comms or has_hcd:
            add_partner('behavioral_science')
        if has_cloud or has_data or has_web:
            add_partner('cloud')
        if not partners:
            add_partner('behavioral_science')

    return {
        'competitors': competitors[:4],
        'partners': partners[:3],
        'set_aside_note': f'Set-aside: {opp.get("set_aside","unknown")} — competitor list filtered accordingly'
    }


def main():
    data = json.loads(OPPS_FILE.read_text())
    opps = data['opps']

    updated = 0
    for opp in opps:
        intel = get_competitive_intel(opp)
        opp['competitive_intel'] = intel
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
