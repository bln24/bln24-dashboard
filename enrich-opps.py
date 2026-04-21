#!/usr/bin/env python3
"""
enrich-opps.py
Reads opps.json, analyzes each opp's full description using structured rules,
and produces a capability_matrix for each opp showing:
- What the government actually needs
- Whether BLN24 can deliver each item (own / gap / partner)
"""

import json, re, sys
from pathlib import Path

OPPS_FILE = Path('/Users/t24/Desktop/T24/dashboard/opps.json')

# BLN24 capability matrix definition
# Each entry: { 'capability': str, 'keywords': [str], 'bln24_status': 'prime'|'sub'|'jv'|'gap', 'evidence': str }
BLN24_MATRIX = [
    # === OWNED — BLN24 Prime ===
    {'cap': 'Human-Centered Design / UX',       'status': 'prime', 'evidence': 'IRS HCD BPA $7M, Census UX, CBP digital transformation',
     'kw': ['human centered design','human-centered design','hcd','user experience','ux ','ux research','service design','design thinking','user research','usability','user testing','human factors']},

    {'cap': 'Strategic Communications',          'status': 'prime', 'evidence': 'CMS MNPS $16M, CDC health comms $3.9M, HUD FHEO $2M',
     'kw': ['communications strategy','communications support','communications services','strategic communications','public affairs','communications plan','stakeholder communications']},

    {'cap': 'Health Communications & Outreach',  'status': 'prime', 'evidence': 'CDC DDT, CDC NAC, CDC NCHS, HHS OIDP $10M (Fors Marsh)',
     'kw': ['health communications','public health campaign','health outreach','health messaging','health education','disease prevention','health awareness','public health outreach']},

    {'cap': 'Outreach & Stakeholder Engagement', 'status': 'prime', 'evidence': 'HUD FHEO outreach, HRSA Marketing BPA, USCIS VER',
     'kw': ['outreach','stakeholder engagement','community engagement','public engagement','employer outreach','education campaign','awareness campaign','program outreach']},

    {'cap': 'Content Development & Plain Language','status': 'prime', 'evidence': 'CMS notice production $16M, CDC communications',
     'kw': ['content development','content creation','content strategy','plain language','web content','editorial','notice production','written materials','publications']},

    {'cap': 'Digital Marketing & Paid Media',    'status': 'prime', 'evidence': 'USDA social media, CDC digital, FTC paid advertising (Fors Marsh)',
     'kw': ['digital marketing','paid media','social media','digital campaign','advertising','marketing platform','lead generation','media buy','institutional advertising']},

    {'cap': 'Branding & Visual Identity',        'status': 'prime', 'evidence': 'MBDA website $4.4M, Census design services',
     'kw': ['branding','brand strategy','graphic design','visual design','logo','brand identity','creative services','brand guidelines','visual identity']},

    {'cap': 'Video Production & Multimedia',     'status': 'prime', 'evidence': 'CDC NCHS visual comms $3.6M, USDA, DOI, VA video',
     'kw': ['video production','multimedia','photography','motion graphics','animation','visual communications','audiovisual','film','video content','photo services']},

    {'cap': 'Web Design & Development',          'status': 'prime', 'evidence': 'MBDA website $4.4M, Census DWS, Oversight.gov $387K',
     'kw': ['web development','web design','website redesign','frontend','web application','portal','drupal','wordpress','web platform','cms development']},

    {'cap': 'Digital Platform & Experience',     'status': 'prime', 'evidence': 'Census Digital Web Services, CBP.gov redesign (Clarity24)',
     'kw': ['digital platform','digital services','digital transformation','digital experience','information architecture','digital presence','online platform']},

    {'cap': 'Data Analytics & Business Intelligence', 'status': 'prime', 'evidence': 'Census SRQA $4.1M, Dept of Education EDARMST $2.9M',
     'kw': ['data analytics','data analysis','business intelligence','reporting','bi dashboard','analytics platform','data visualization','statistical analysis','data-driven','quantitative analysis']},

    {'cap': 'Data Engineering & Management',     'status': 'prime', 'evidence': 'Census SRQA, MAF/TIGER, Census data archiving $4.5M',
     'kw': ['data engineering','data management','data architecture','data pipeline','data quality','data governance','data archiving','etl','data collection','data processing']},

    {'cap': 'Survey Design & Research',          'status': 'jv',    'evidence': 'USPTO survey support (BLN Fors Marsh JV), Census data collection',
     'kw': ['survey','survey design','survey methodology','survey administration','data collection survey','questionnaire','census survey','respondent']},

    {'cap': 'Behavioral Science & Research',     'status': 'jv',    'evidence': 'DHRA command climate (BLN Fors Marsh JV)',
     'kw': ['behavioral science','behavioral research','behavior change','social marketing','nudge','command climate','organizational climate','behavioral insights','behavioral economics']},

    {'cap': 'Translation & Multilingual',        'status': 'prime', 'evidence': 'CMS Spanish Language Campaign, FTC language resources (Fors Marsh)',
     'kw': ['translation','spanish language','multilingual','language services','interpretation','bilingual','cultural competency','multicultural','spanish-language']},

    {'cap': 'Accessibility (Section 508)',       'status': 'prime', 'evidence': 'IRS HCD BPA scope, Census web work',
     'kw': ['accessibility','section 508','508 compliance','ada compliance','wcag','screen reader','assistive technology']},

    # === JV / TEAMING ===
    {'cap': 'Cloud Migration & Infrastructure',  'status': 'jv',    'evidence': 'NOAA NWS IDP cloud $4.3M, NOAA app mod $2.8M (Clarity24 JV)',
     'kw': ['cloud migration','cloud transition','cloud modernization','aws','azure','google cloud','cloud infrastructure','cloud platform','cloud hosting','iaas','paas']},

    {'cap': 'Application Modernization',         'status': 'jv',    'evidence': 'NOAA app modernization $2.8M, Census MAF/TIGER (Clarity24 JV)',
     'kw': ['application modernization','app modernization','legacy modernization','system modernization','software modernization','it modernization','platform modernization','legacy migration']},

    {'cap': 'Program Evaluation',                'status': 'jv',    'evidence': 'DHRA research (Fors Marsh JV), Census SRQA quality assurance',
     'kw': ['program evaluation','impact evaluation','randomized controlled','rct','quasi-experimental','effectiveness evaluation','performance evaluation','outcome evaluation']},

    # === GAPS — Cannot Prime ===
    {'cap': 'Cybersecurity / FISMA / Zero Trust', 'status': 'gap',  'evidence': 'No BLN24 prime cybersecurity delivery on record',
     'kw': ['cybersecurity','fisma','zero trust','splunk','soc','security operations','vulnerability management','ato','authorization to operate','pen testing','cyber defense']},

    {'cap': 'DevSecOps / CI/CD',                 'status': 'gap',  'evidence': 'No BLN24 prime DevSecOps delivery on record',
     'kw': ['devsecops','devops','ci/cd','jenkins','github actions','containerization','kubernetes','docker','pipeline automation','agile delivery']},

    {'cap': 'IT Infrastructure / Telecom',       'status': 'gap',  'evidence': 'No BLN24 IT infrastructure prime on record',
     'kw': ['it infrastructure','network infrastructure','telecommunications','telephony','server hosting','network engineering','wan','lan','fiber','wireless infrastructure']},

    {'cap': 'IT Program Management / CIO Support','status': 'gap', 'evidence': 'No BLN24 CIO-shop IT governance prime on record',
     'kw': ['it governance','enterprise architecture','it portfolio','cio support','it program management','it strategy','it policy','it modernization strategy','capital planning']},

    {'cap': 'CRM / Salesforce Implementation',   'status': 'gap',  'evidence': 'No BLN24 CRM implementation prime on record',
     'kw': ['crm','salesforce','microsoft dynamics','servicenow','customer relationship management','crm implementation','crm licensing']},

    {'cap': 'Training & eLearning Development',  'status': 'gap',  'evidence': 'No BLN24 training/eLearning prime delivery on record',
     'kw': ['elearning','e-learning','training development','instructional design','lms','learning management','curriculum development','course development','training content']},

    {'cap': 'Scientific / Laboratory Support',   'status': 'gap',  'evidence': 'Not a BLN24 service lane',
     'kw': ['laboratory','scientific support','lab services','biological sampling','specimen','hatchery','aquatic','medical device','clinical','pathology','point of care']},

    {'cap': 'Medical Services',                  'status': 'gap',  'evidence': 'Not a BLN24 service lane',
     'kw': ['medical services','clinical psychologist','physician','medical technician','healthcare provider','nursing','medical support','patient care']},

    {'cap': 'Space / Defense Technology',        'status': 'gap',  'evidence': 'Not a BLN24 service lane',
     'kw': ['space technology','surveillance','reconnaissance','itar','missile','warfighter','cmmc','tactical','geospatial intelligence','signals intelligence']},

    {'cap': 'Software Licensing / Procurement',  'status': 'gap',  'evidence': 'Not a BLN24 service lane',
     'kw': ['software license','software procurement','enterprise license','seat license','subscription licensing','enterprise agreement']},
]

STATUS_LABEL = {
    'prime': '✅ BLN24 Prime',
    'jv':    '🤝 JV / Teaming',
    'gap':   '❌ Gap — Cannot Prime',
}

def build_capability_matrix(opp):
    """Analyze full opp text and return structured capability matrix."""
    text = ((opp.get('title') or '') + ' ' +
            (opp.get('summary') or '') + ' ' +
            (opp.get('description') or '')).lower()

    matrix = []
    for item in BLN24_MATRIX:
        if any(k in text for k in item['kw']):
            # Find which specific keywords triggered the match
            matched_kw = [k for k in item['kw'] if k in text][:3]
            matrix.append({
                'capability':  item['cap'],
                'status':      item['status'],
                'status_label': STATUS_LABEL[item['status']],
                'evidence':    item['evidence'],
                'matched_on':  matched_kw,
            })

    # Derive overall fit
    has_prime = any(m['status'] == 'prime' for m in matrix)
    has_jv    = any(m['status'] == 'jv'    for m in matrix)
    has_gap   = any(m['status'] == 'gap'   for m in matrix)
    all_gap   = matrix and all(m['status'] == 'gap' for m in matrix)

    if all_gap:
        fit = 'Pass'
        fit_reason = 'All identified scope items fall outside BLN24\'s proven delivery lanes'
    elif has_prime and not has_gap:
        fit = 'Strong'
        fit_reason = 'Scope aligns directly with BLN24 prime delivery lanes'
    elif has_prime and has_gap:
        prime_caps = [m['capability'] for m in matrix if m['status'] == 'prime']
        gap_caps   = [m['capability'] for m in matrix if m['status'] == 'gap']
        fit = 'Moderate'
        fit_reason = f'BLN24 can own: {", ".join(prime_caps[:2])}. Gap areas need teaming: {", ".join(gap_caps[:2])}'
    elif has_jv:
        fit = 'JV Required'
        fit_reason = 'Scope matches BLN24 JV lanes (Clarity24 or Fors Marsh) — viable via teaming'
    elif not matrix:
        fit = 'Pass'
        fit_reason = 'No capability match found in scope text — likely out of BLN24 lanes entirely'
    else:
        fit = 'Weak'
        fit_reason = 'Partial scope match but no clear BLN24 prime lane'

    return {
        'items':      matrix,
        'fit':        fit,
        'fit_reason': fit_reason,
        'prime_count': sum(1 for m in matrix if m['status'] == 'prime'),
        'jv_count':    sum(1 for m in matrix if m['status'] == 'jv'),
        'gap_count':   sum(1 for m in matrix if m['status'] == 'gap'),
    }


def main():
    data = json.loads(OPPS_FILE.read_text())
    opps = data['opps']

    updated = 0
    for opp in opps:
        matrix = build_capability_matrix(opp)
        opp['capability_matrix'] = matrix
        updated += 1

    data['opps'] = opps
    OPPS_FILE.write_text(json.dumps(data, indent=2))
    print(f'Enriched {updated} opps with capability matrices')

    # Print top 10 for review
    print('\n=== TOP 10 OPPS — CAPABILITY MATRIX ===')
    for opp in sorted(opps, key=lambda x: -x.get('capture_score',0))[:10]:
        m = opp.get('capability_matrix', {})
        items = m.get('items', [])
        print(f'\n[{opp["capture_score"]}pts | {m.get("fit","?")}] {opp["title"][:65]}')
        print(f'  {opp["noticeCategory"].upper()} | {opp["agency"][:40]}')
        if items:
            for i in items:
                print(f'  {i["status_label"]}: {i["capability"]}')
                print(f'    → Evidence: {i["evidence"]}')
        else:
            print('  No capabilities matched in scope text')
        print(f'  Fit: {m.get("fit_reason","")}')


if __name__ == '__main__':
    main()
