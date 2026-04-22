#!/usr/bin/env python3
"""
Add competitor and partner intelligence to each opp.
Based on agency, scope lanes, and gap areas — surfaces likely competitors
and recommended teaming partners with HigherGov links.
"""
import json
from pathlib import Path

OPPS_FILE = Path('/Users/t24/Desktop/T24/dashboard/opps.json')

HG_BASE = 'https://www.highergov.com'

# Competitor database by scope/agency type
COMPETITORS = {
    'hcd_ux': [
        {'name': 'ICF International', 'why': 'Large HCD/comms firm, HHS/CMS anchor client, OASIS+ prime — direct competitor on health/HCD RFPs', 'url': f'{HG_BASE}/awardee/icf-incorporated-l-l-c-73040/'},
        {'name': 'Fearless Solutions', 'why': '8(a) HCD-focused firm, federal digital services, same NAICS lanes as BLN24', 'url': f'{HG_BASE}/awardee/fearless-inc-388034/'},
        {'name': 'Coforma', 'why': 'Federal UX/HCD, CMS digital services work, OASIS+ holder', 'url': f'{HG_BASE}/awardee/?search=Coforma'},
        {'name': 'Ad Hoc LLC', 'why': 'Federal digital services, healthcare.gov (CMS), strong UX practice', 'url': f'{HG_BASE}/awardee/?search=Ad+Hoc+LLC'},
    ],
    'web_platform': [
        {'name': 'Softrams', 'why': '8(a), Agile dev, CMS/VA web work, same size bracket as BLN24', 'url': f'{HG_BASE}/awardee/?search=Softrams'},
        {'name': 'Unison', 'why': 'Federal Drupal/AEM specialist, Census and HHS web platform experience', 'url': f'{HG_BASE}/awardee/?search=Unison'},
        {'name': 'SAIC', 'why': 'Large IT/web platform prime, OASIS+ — threatens on full & open web dev', 'url': f'{HG_BASE}/awardee/science-applications-international-corporation-saic-25048/'},
    ],
    'comms': [
        {'name': 'ICF International', 'why': 'Major health/public affairs comms, CDC/HHS anchor — primary competitor on comms RFPs', 'url': f'{HG_BASE}/awardee/icf-incorporated-l-l-c-73040/'},
        {'name': 'Ketchum', 'why': 'Federal health comms, FDA/CDC campaigns, established agency relationships', 'url': f'{HG_BASE}/awardee/?search=Ketchum'},
        {'name': 'Booz Allen Hamilton', 'why': 'Large cleared comms, DoD/health — threatens on DoD and cleared comms work', 'url': f'{HG_BASE}/awardee/booz-allen-hamilton-inc-6455/'},
    ],
    'data_analytics': [
        {'name': 'Booz Allen Hamilton', 'why': 'Data/analytics powerhouse, federal AI/ML — competes on data engineering and analytics RFPs', 'url': f'{HG_BASE}/awardee/booz-allen-hamilton-inc-6455/'},
        {'name': 'Leidos', 'why': 'Federal data platforms, large data engineering contracts', 'url': f'{HG_BASE}/awardee/?search=Leidos'},
        {'name': 'Palantir', 'why': 'Federal data/AI, DoD and Intel — threatens on data analytics with cleared requirements', 'url': f'{HG_BASE}/awardee/?search=Palantir'},
    ],
    'intl_dev': [
        {'name': 'Chemonics International', 'why': 'Largest MCC/USAID implementer — likely incumbent or strong competitor on MCC work', 'url': f'{HG_BASE}/awardee/chemonics-international-inc-3474/'},
        {'name': 'DevTech Systems', 'why': 'MCC/USAID monitoring & evaluation, workforce dev, education advisory — direct MCC competitor', 'url': f'{HG_BASE}/awardee/?search=DevTech+Systems'},
        {'name': 'Creative Associates International', 'why': 'International education and workforce, TVET programs in developing countries', 'url': f'{HG_BASE}/awardee/creative-associates-international-inc-1847/'},
        {'name': 'Nathan Associates', 'why': 'Economic analysis, MCC cost-benefit methodology, workforce development advisory', 'url': f'{HG_BASE}/awardee/?search=Nathan+Associates'},
    ],
    'cloud_dev': [
        {'name': 'SAIC', 'why': 'Large cloud/IT prime, competes on cloud migration and app mod at federal scale', 'url': f'{HG_BASE}/awardee/science-applications-international-corporation-saic-25048/'},
        {'name': 'Peraton', 'why': 'Cloud infrastructure, DevSecOps — threatens on cloud/tech-heavy RFPs', 'url': f'{HG_BASE}/awardee/?search=Peraton'},
        {'name': 'ManTech', 'why': 'Federal IT/cloud, OASIS+ prime — competes on cloud migration and modernization', 'url': f'{HG_BASE}/awardee/?search=ManTech'},
    ],
}

# Partner database by gap type
PARTNERS = {
    'devsecops': {
        'name': 'Clarity24 LLC (BLN24 JV)',
        'why': 'Active 8(a) JV — AWS cloud delivery (NOAA $7M), app modernization, DevSecOps. Fills the tech depth gap.',
        'url': f'{HG_BASE}/awardee/clarity24-llc-627966104/',
        'relationship': 'Active JV'
    },
    'cloud': {
        'name': 'Clarity24 LLC (BLN24 JV)',
        'why': 'NOAA IDP Cloud Migration ($4.3M), NOAA AI/ML ($3.6M), CBP Digital ($4M). Cloud is Clarity24\'s core lane.',
        'url': f'{HG_BASE}/awardee/clarity24-llc-627966104/',
        'relationship': 'Active JV'
    },
    'behavioral_science': {
        'name': 'BLN Fors Marsh JV LLC',
        'why': 'Active 8(a) JV — $59M behavioral research (DHRA OPA), HHS OIDP $10.3M, FTC paid media. Behavioral science is Fors Marsh\'s core lane.',
        'url': f'{HG_BASE}/awardee/bln-fors-marsh-jv-llc-476980511/',
        'relationship': 'Active JV'
    },
    'paid_media': {
        'name': 'BLN Fors Marsh JV LLC',
        'why': 'FTC paid advertising ($4.5M BPA), HHS OIDP health comms. Multilingual and targeted paid media.',
        'url': f'{HG_BASE}/awardee/bln-fors-marsh-jv-llc-476980511/',
        'relationship': 'Active JV'
    },
    'tvet_workforce': {
        'name': 'Chemonics International',
        'why': 'Largest MCC/USAID implementer. Deep TVET and workforce development in compact countries. Sub arrangement fills BLN24\'s international workforce gap.',
        'url': f'{HG_BASE}/awardee/chemonics-international-inc-3474/',
        'relationship': 'Recommended sub'
    },
    'cybersecurity': {
        'name': 'SAIC or ManTech',
        'why': 'Large cleared cyber primes on OASIS+. Sub arrangement covers ATO maintenance and FISMA compliance without BLN24 holding the ATO.',
        'url': f'{HG_BASE}/awardee/science-applications-international-corporation-saic-25048/',
        'relationship': 'Recommended sub'
    },
    'program_evaluation': {
        'name': 'Mathematica or Westat',
        'why': 'Rigorous evaluation methodology, RCT design, USAID and ED program evaluation history. Fills BLN24\'s standalone evaluation methodology gap.',
        'url': f'{HG_BASE}/awardee/?search=Mathematica',
        'relationship': 'Recommended sub'
    },
    'it_infrastructure': {
        'name': 'Peraton or Leidos',
        'why': 'Large IT infrastructure primes on OASIS+. Sub arrangement covers network, server hosting, telecom without BLN24 holding that prime.',
        'url': f'{HG_BASE}/awardee/?search=Peraton',
        'relationship': 'Recommended sub'
    },
}

# Lane-to-competitor mapping
LANE_TO_COMPETITORS = {
    'Human-Centered Design': 'hcd_ux',
    'UX Research': 'hcd_ux',
    'Behavior': 'hcd_ux',
    'Web Design': 'web_platform',
    'Digital Platform': 'web_platform',
    'Application Modernization': 'cloud_dev',
    'Cloud Migration': 'cloud_dev',
    'Software Development': 'cloud_dev',
    'Strategic Communications': 'comms',
    'Health Communications': 'comms',
    'Public Outreach': 'comms',
    'Data Analytics': 'data_analytics',
    'Data Engineering': 'data_analytics',
    'Due Diligence': 'intl_dev',
    'Workforce Development': 'intl_dev',
    'International': 'intl_dev',
}

# Gap-to-partner mapping
GAP_TO_PARTNERS = {
    'DevSecOps': 'devsecops',
    'Cybersecurity': 'cybersecurity',
    'Cloud Engineering': 'cloud',
    'Workforce / Talent': 'tvet_workforce',
    'IT Infrastructure': 'it_infrastructure',
    'Program Evaluation': 'program_evaluation',
    'Scientific': None,  # Not a BLN24 lane, no good partner
    'Medical Services': None,
}


def get_competitive_intel(opp):
    cm = opp.get('capability_matrix', {})
    tasks = cm.get('tasks', [])
    title = (opp.get('title') or '').lower()
    agency = (opp.get('agency') or '').lower()

    # Determine competitor sets based on matched lanes
    competitor_sets = set()
    for task in tasks:
        task_name = task.get('task', '')
        for lane_key, comp_key in LANE_TO_COMPETITORS.items():
            if lane_key.lower() in task_name.lower():
                competitor_sets.add(comp_key)

    # Override for MCC/intl dev
    if 'millennium challenge' in agency or 'mcc' in agency or 'usaid' in title:
        competitor_sets.add('intl_dev')

    # Collect unique competitors (max 3)
    competitors = []
    seen_names = set()
    for cs in list(competitor_sets)[:3]:
        for comp in COMPETITORS.get(cs, [])[:2]:
            if comp['name'] not in seen_names:
                competitors.append(comp)
                seen_names.add(comp['name'])
            if len(competitors) >= 4:
                break

    # Determine partner needs based on gaps
    partners = []
    seen_partner_names = set()
    for task in tasks:
        if task.get('score', 0) == 0:
            task_name = task.get('task', '')
            for gap_key, partner_key in GAP_TO_PARTNERS.items():
                if gap_key.lower() in task_name.lower() and partner_key:
                    partner = PARTNERS.get(partner_key)
                    if partner and partner['name'] not in seen_partner_names:
                        partners.append(partner)
                        seen_partner_names.add(partner['name'])
                    break

    # Always surface JV partners when relevant
    if any('behavioral' in t.get('task','').lower() or 'paid media' in t.get('task','').lower() 
           for t in tasks if t.get('score', 0) >= 3):
        fors_marsh = PARTNERS['behavioral_science']
        if fors_marsh['name'] not in seen_partner_names:
            partners.append(fors_marsh)
            seen_partner_names.add(fors_marsh['name'])

    if any('cloud' in t.get('task','').lower() or 'software dev' in t.get('task','').lower()
           for t in tasks if t.get('score', 0) >= 3):
        clarity = PARTNERS['cloud']
        if clarity['name'] not in seen_partner_names:
            partners.append(clarity)
            seen_partner_names.add(clarity['name'])

    return {
        'competitors': competitors[:4],
        'partners': partners[:3],
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
    print(f'Added competitive intel to {updated}/{len(opps)} opps')

    # Sample output
    print('\nSample — top 3 opps:')
    for opp in opps[:3]:
        intel = opp.get('competitive_intel', {})
        print(f'\n[{opp["capture_score"]}pts] {opp["title"][:55]}')
        for c in intel.get('competitors', []):
            print(f'  ⚔️  Competitor: {c["name"]}')
        for p in intel.get('partners', []):
            print(f'  🤝 Partner: {p["name"]} ({p["relationship"]})')


if __name__ == '__main__':
    main()
