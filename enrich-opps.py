#!/usr/bin/env python3
"""
enrich-opps.py — Capability Matrix Generator (BLN24 Format)

Reads opps.json and generates a capability matrix per opp using BLN24's
standard format:
  - SOW/PWS task areas extracted from description
  - Score 0-4 per task (same rubric BLN24 uses internally)
  - Past performance references that back each score
  - Qualifying questions (go/no-go factors)

Score rubric (matches BLN24's internal standard):
  4 = Highly similar PP, size/scope, within 3 years
  3 = Similar PP within 3 years
  2 = Related PP, different context
  1 = Limited / adjacent experience
  0 = No experience
"""

import json, re
from pathlib import Path

OPPS_FILE = Path('/Users/t24/Desktop/T24/dashboard/opps.json')

# ─────────────────────────────────────────────────────────────────
# BLN24 PAST PERFORMANCE REFERENCE LIBRARY
# key = short label used in scoring rules
# value = { display, contracts, years_ago, score_weight }
# ─────────────────────────────────────────────────────────────────
PP = {
    # 4-point references (highly similar, recent, same scope)
    'IRS_HCD':    {'ref': 'IRS Human Centered Design & Research BPA ($7M)', 'score': 4,
                   'detail': 'HCD research, usability testing, UX strategy for IRS digital products'},
    'CMS_MNPS':   {'ref': 'CMS Marketplace Notice Production Services ($16M)', 'score': 4,
                   'detail': 'Strategic communications, notice production, plain language, multichannel outreach'},
    'NOAA_CLOUD': {'ref': 'NOAA NWS IDP Cloud Transition / App Mod (Clarity24, $7M)', 'score': 4,
                   'detail': 'Cloud migration, application modernization, AWS infrastructure (via Clarity24 JV)'},
    'CENSUS_EDL': {'ref': 'Census EDL Applications ($4.5M)', 'score': 4,
                   'detail': 'Enterprise data platform, application development, data architecture for Census programs'},
    'CENSUS_SRQA':{'ref': 'Census SRQA AI/ML/Data Quality ($4.1M)', 'score': 4,
                   'detail': 'Data quality, AI/ML, statistical analysis, survey methodology for Decennial Census'},
    'CENSUS_MAF': {'ref': 'Census MAF/TIGER Modernization & Cloud ($4.5M)', 'score': 4,
                   'detail': 'GIS data modernization, cloud migration, data engineering'},
    'MBDA_WEB':   {'ref': 'MBDA Website Redesign ($4.4M)', 'score': 4,
                   'detail': 'Full website redesign, information architecture, UX, web development for federal agency'},
    'CDC_NCHS':   {'ref': 'CDC NCHS Visual Communications ($3.6M)', 'score': 4,
                   'detail': 'Visual communications, multimedia production, health data visualization'},
    'HHS_OIDP':   {'ref': 'HHS OIDP Comprehensive Communications ($10.3M, Fors Marsh JV)', 'score': 4,
                   'detail': 'Infectious disease outreach, paid media, behavioral science, health communications'},
    'ED_DATA':    {'ref': 'Dept of Education EDARMST Data Analytics ($2.9M)', 'score': 4,
                   'detail': 'Data analytics, risk management, BI dashboards for federal education programs'},

    # 3-point references (similar, within 3 years)
    'HUD_FHEO':   {'ref': 'HUD FHEO Communications & Outreach ($2M)', 'score': 3,
                   'detail': 'Federal agency communications and outreach program'},
    'CBP_DT':     {'ref': 'CBP Digital Transformation (Clarity24, $1.4M)', 'score': 3,
                   'detail': 'Digital transformation, UX, web platform for DHS/CBP'},
    'CENSUS_DWS': {'ref': 'Census Digital Web Services III ($8.3M)', 'score': 4,
                   'detail': 'Census.gov modernization, AEM development (one of largest federal AEM deployments), CX platform, web development'},
    'USPTO_SURV': {'ref': 'USPTO Survey Support (Fors Marsh JV)', 'score': 3,
                   'detail': 'Survey design and administration, marketing consulting for USPTO'},
    'FTC_MEDIA':  {'ref': 'FTC Paid Advertising (Fors Marsh JV, $581K)', 'score': 3,
                   'detail': 'Targeted paid media, digital advertising for federal consumer protection'},
    'IRS_SBSE':   {'ref': 'IRS SB/SE BOD Leadership Initiative (Clarity24, $2.7M)', 'score': 4,
                   'detail': 'Leadership development, org transformation, culture assessment for 60+ IRS SB/SE executives, change management, workforce capacity building'},
    'CENSUS_CES':  {'ref': 'Census CES ADRM IT & Research Support ($7M)', 'score': 4,
                   'detail': 'Software engineering, application development (OnTheMap, QWI Explorer, Job-to-Job Flows), database admin, cloud + enterprise environments, Agile delivery, data science, statistical research, economists/statisticians/coders, federal security and 508'},
    'USDA_SOC':   {'ref': 'USDA Social Media & Digital Outreach ($141K)', 'score': 3,
                   'detail': 'Social media campaign management, digital content for USDA'},
    'USDA_FNS':   {'ref': 'USDA FNS WIC Digital Services (Clarity24, $2.2M)', 'score': 3,
                   'detail': 'Digital services for federal nutrition program (via Clarity24 JV)'},
    'IRS_OLS':    {'ref': 'IRS OLS (sub reference)', 'score': 3,
                   'detail': 'IRS digital systems support, stakeholder engagement'},
    'DHRA':       {'ref': 'DHRA Command Climate Research (Fors Marsh JV)', 'score': 3,
                   'detail': 'Behavioral science research, organizational climate, military context'},
    'OVERSIGHT':  {'ref': 'USPS OIG Oversight.gov Refresh ($387K)', 'score': 3,
                   'detail': 'Federal website redesign, UX, web development'},
    'CDC_COMMS':  {'ref': 'CDC Communications (DDT $138K, NAC $250K)', 'score': 3,
                   'detail': 'Health communications, digital outreach, content development for CDC'},
    'CMS_SPANISH':{'ref': 'CMS Spanish Language Medicare Campaign', 'score': 3,
                   'detail': 'Multilingual campaign, Spanish-language health communications'},

    # 2-point references (related, different context)
    'CENSUS_PHOTO':{'ref': 'Census Assignment Photography ($136K)', 'score': 2,
                    'detail': 'Federal photography services'},
    'DOI_VIDEO':  {'ref': 'DOI/NPS Video Production ($90K)', 'score': 2,
                   'detail': 'Video production for federal natural resources agency'},
    'USDA_FNS2':  {'ref': 'USDA NRCS/USFS Video/Photography ($138K)', 'score': 2,
                   'detail': 'Multimedia production for agriculture agencies'},
    'MCC_HCD':    {'ref': 'MCC HCD Due Diligence (if won)', 'score': 2,
                   'detail': 'International development context, HCD advisory'},
}

# ─────────────────────────────────────────────────────────────────
# TASK AREA DEFINITIONS
# Each task: keywords that identify this work area in solicitation text
# + scoring rules: which PP refs apply and at what score
# ─────────────────────────────────────────────────────────────────
TASK_AREAS = [
    {
        'task': 'Human-Centered Design & UX Research',
        'kw': ['human centered design','human-centered design','hcd','user experience','ux research','user research','usability testing','user testing','design thinking','service design','human factors'],
        'pp_refs': ['IRS_HCD', 'CBP_DT', 'CENSUS_DWS', 'MBDA_WEB'],
        'base_score': 4,
        'note': 'BLN24 strong prime — IRS HCD BPA $7M is direct comparable'
    },
    {
        'task': 'UX/UI Design & Prototyping',
        'kw': ['ui design','ux design','interface design','interaction design','wireframe','prototype','figma','design system','ui/ux','visual design system'],
        'pp_refs': ['IRS_HCD', 'MBDA_WEB', 'CBP_DT'],
        'base_score': 4,
        'note': 'BLN24 prime — IRS HCD BPA, Census DWS, MBDA web all included UI/UX'
    },
    {
        'task': 'Accessibility / Section 508 Compliance',
        'kw': ['accessibility','section 508','508 compliance','ada','wcag','screen reader','assistive technology'],
        'pp_refs': ['IRS_HCD', 'CENSUS_DWS'],
        'base_score': 3,
        'note': 'BLN24 prime — IRS HCD BPA scope included 508 compliance testing'
    },
    {
        'task': 'Customer Experience (CX) Strategy',
        'kw': ['customer experience','cx strategy','cx design','journey map','service blueprint','cx transformation'],
        'pp_refs': ['IRS_HCD', 'CBP_DT', 'CENSUS_DWS'],
        'base_score': 3,
        'note': 'BLN24 prime — CBP Digital Transformation (Clarity24), IRS HCD'
    },
    {
        'task': 'Strategic Communications Planning',
        'kw': ['communications strategy','communications plan','strategic communications','public affairs','communications framework','communications support'],
        'pp_refs': ['CMS_MNPS', 'HUD_FHEO', 'CDC_COMMS', 'HHS_OIDP'],
        'base_score': 4,
        'note': 'BLN24 strong prime — CMS MNPS $16M, HUD, CDC all strategic comms'
    },
    {
        'task': 'Health Communications & Outreach',
        'kw': ['health communications','public health campaign','health messaging','health outreach','health education','disease prevention','health awareness','clinical communications'],
        'pp_refs': ['CDC_COMMS', 'CDC_NCHS', 'HHS_OIDP', 'CMS_MNPS'],
        'base_score': 4,
        'note': 'BLN24 strong prime — CDC comms (DDT, NAC, NCHS), HHS OIDP (Fors Marsh JV), CMS'
    },
    {
        'task': 'Public Outreach & Stakeholder Engagement',
        'kw': ['outreach','stakeholder engagement','community engagement','public engagement','employer outreach','awareness campaign','program outreach'],
        'pp_refs': ['HUD_FHEO', 'HHS_OIDP', 'CDC_COMMS', 'CMS_MNPS'],
        'base_score': 3,
        'note': 'BLN24 prime — HUD FHEO, HRSA, USCIS outreach work'
    },
    {
        'task': 'Content Development & Plain Language',
        'kw': ['content development','content creation','content strategy','plain language','web content','notice production','written materials','publications','editorial','copywriting'],
        'pp_refs': ['CMS_MNPS', 'HUD_FHEO', 'CDC_COMMS'],
        'base_score': 4,
        'note': 'BLN24 prime — CMS MNPS $16M is core content/notice production work'
    },
    {
        'task': 'Digital Marketing & Paid Media',
        'kw': ['digital marketing','paid media','paid advertising','social media','digital campaign','advertising','media buy','lead generation','institutional advertising','marketing platform'],
        'pp_refs': ['HHS_OIDP', 'FTC_MEDIA', 'USDA_SOC', 'CDC_COMMS'],
        'base_score': 3,
        'note': 'BLN24 prime/JV — USDA social media, FTC paid media (Fors Marsh), HHS OIDP'
    },
    {
        'task': 'Multilingual / Spanish Language Communications',
        'kw': ['spanish language','multilingual','translation','bilingual','multicultural','language services','spanish-language'],
        'pp_refs': ['CMS_SPANISH', 'HHS_OIDP'],
        'base_score': 3,
        'note': 'BLN24 prime — CMS Spanish Language Medicare Campaign, HHS multilingual outreach'
    },
    {
        'task': 'Branding & Visual Identity',
        'kw': ['branding','brand strategy','logo','brand identity','visual identity','brand guidelines','brand refresh'],
        'pp_refs': ['MBDA_WEB', 'CENSUS_DWS'],
        'base_score': 4,
        'note': 'BLN24 prime — MBDA website/rebrand $4.4M, Census design services'
    },
    {
        'task': 'Graphic Design & Infographics',
        'kw': ['graphic design','visual design','infographic','layout design','print design','illustration','design deliverables'],
        'pp_refs': ['CDC_NCHS', 'MBDA_WEB', 'USDA_SOC'],
        'base_score': 3,
        'note': 'BLN24 prime — CDC NCHS visual comms, MBDA branding, USDA social media graphics'
    },
    {
        'task': 'Video Production & Multimedia',
        'kw': ['video production','video development','multimedia','photography','motion graphics','animation','audiovisual','visual communications','film'],
        'pp_refs': ['CDC_NCHS', 'DOI_VIDEO', 'USDA_FNS2', 'CENSUS_PHOTO'],
        'base_score': 4,
        'note': 'BLN24 prime — CDC NCHS visual comms $3.6M, DOI/USDA video work'
    },
    {
        'task': 'Large Format Print / Environmental Graphics',
        'kw': ['large format','building wrap','signage','banner','environmental graphics','print installation','wayfinding'],
        'pp_refs': ['CDC_NCHS', 'MBDA_WEB'],
        'base_score': 2,
        'note': 'BLN24 has production/visual design experience; large format print is adjacent'
    },
    {
        'task': 'Web Design & Development',
        'kw': ['web development','web design','website redesign','frontend','web application','portal','drupal','wordpress','web platform'],
        'pp_refs': ['MBDA_WEB', 'CENSUS_DWS', 'OVERSIGHT', 'CBP_DT'],
        'base_score': 4,
        'note': 'BLN24 prime — MBDA $4.4M, Census DWS, Oversight.gov, CBP.gov redesign (Clarity24)'
    },
    {
        'task': 'Digital Platform & Portal Development',
        'kw': ['digital platform','digital services','digital transformation','digital experience','information architecture','online platform','digital portal'],
        'pp_refs': ['CENSUS_DWS', 'MBDA_WEB', 'CBP_DT', 'USDA_FNS'],
        'base_score': 3,
        'note': 'BLN24 prime/JV — Census DWS, MBDA, CBP digital platform (Clarity24)'
    },
    {
        'task': 'Data Analytics & Business Intelligence',
        'kw': ['data analytics','data analysis','business intelligence','bi dashboard','analytics platform','reporting','data reporting','kpi dashboard','performance dashboard','databricks'],
        'pp_refs': ['CENSUS_CES', 'CENSUS_SRQA', 'ED_DATA', 'IRS_OLS'],
        'base_score': 4,
        'note': 'BLN24 prime — Census SRQA $4.1M (AI/ML/data), Education EDARMST $2.9M'
    },
    {
        'task': 'Data Visualization',
        'kw': ['data visualization','tableau','power bi','visualization','interactive chart','infographic data','visual analytics'],
        'pp_refs': ['CENSUS_SRQA', 'ED_DATA', 'CDC_NCHS'],
        'base_score': 3,
        'note': 'BLN24 prime — Census SRQA, Education data analytics, CDC NCHS visual data'
    },
    {
        'task': 'Data Engineering & ETL',
        'kw': ['data engineering','data pipeline','etl','data architecture','data management','data governance','data quality','data processing','data integration','sql','python'],
        'pp_refs': ['CENSUS_SRQA', 'CENSUS_MAF', 'CENSUS_EDL'],
        'base_score': 4,
        'note': 'BLN24 prime — Census SRQA, MAF/TIGER, EDL all heavy data engineering'
    },
    {
        'task': 'Survey Design & Research Methodology',
        # Require specific survey delivery phrases, not generic 'survey' mentions in data contexts
        'kw': ['survey design','survey methodology','survey administration','questionnaire design','data collection survey','administer survey','survey respondent','user survey','respondent survey'],
        'pp_refs': ['USPTO_SURV', 'CENSUS_SRQA', 'DHRA'],
        'base_score': 3,
        'note': 'BLN24 JV — USPTO survey support (Fors Marsh), Census data collection experience'
    },
    {
        'task': 'Behavioral Science & Research',
        'kw': ['behavioral science','behavioral research','behavior change','behavioral insights','behavioral economics','nudge','command climate'],
        'pp_refs': ['DHRA', 'HHS_OIDP'],
        'base_score': 3,
        'note': 'BLN24 JV — DHRA command climate (Fors Marsh), HHS OIDP behavioral comms'
    },
    {
        'task': 'Program Evaluation',
        'kw': ['program evaluation','impact evaluation','rct','quasi-experimental','effectiveness evaluation','outcome evaluation','formative evaluation'],
        'pp_refs': ['DHRA', 'CENSUS_SRQA'],
        'base_score': 2,
        'note': 'BLN24 JV — Fors Marsh has evaluation expertise; adjacent to Census SRQA QA work'
    },
    {
        'task': 'Cloud Migration & Infrastructure',
        'kw': ['cloud migration','cloud transition','cloud modernization','cloud infrastructure','aws','azure','iaas','paas','cloud platform'],
        'pp_refs': ['NOAA_CLOUD', 'CENSUS_MAF'],
        'base_score': 3,
        'note': 'BLN24 JV — Clarity24 delivered NOAA cloud migration $4.3M, Census MAF/TIGER'
    },
    {
        'task': 'Application Modernization',
        'kw': ['application modernization','app modernization','legacy modernization','system modernization','software modernization','legacy migration'],
        'pp_refs': ['NOAA_CLOUD', 'CENSUS_MAF', 'CENSUS_EDL'],
        'base_score': 3,
        'note': 'BLN24 JV — Clarity24 NOAA app mod $2.8M, Census MAF/TIGER modernization'
    },
    {
        'task': 'Human Capital & Workforce Development Advisory',
        # Require more specific phrases to avoid false positives from finance/IT tools
        'kw': ['workforce development program','leadership development program','leadership capacity','organizational transformation program','organizational change management for workforce','capacity building for staff','talent development program','workforce training program','skills development program','tvet','human capital development','human capital investment'],
        'pp_refs': ['IRS_SBSE'],
        'base_score': 4,
        'note': 'Via Clarity24 JV — IRS SB/SE BOD Leadership Initiative ($2.7M): leadership development, culture assessment for 60+ executives, org transformation, workforce capacity building. DIRECT reference for human capital/workforce advisory.'
    },
    {
        'task': 'Due Diligence & Technical Advisory',
        'kw': ['due diligence','technical advisory','consulting services','technical consulting','advisory support','subject matter expert','sme'],
        'pp_refs': ['IRS_HCD', 'CENSUS_SRQA', 'ED_DATA'],
        'base_score': 3,
        'note': 'BLN24 prime — consulting/advisory embedded in major contracts (IRS, Census, Education)'
    },
    {
        'task': 'International Development Context',
        'kw': ['developing countries','mcc','usaid','international development','global health','foreign assistance','international aid'],
        'pp_refs': ['IRS_HCD'],
        'base_score': 2,
        'note': 'BLN24 has HCD capability; international development context is adjacent but not primary lane'
    },
    {
        'task': 'Records & Information Management',
        'kw': ['records management','information management','records and information','document management','federal records','records system'],
        'pp_refs': [],
        'base_score': 1,
        'note': 'BLN24 has no confirmed prime delivery — would need a teaming partner'
    },
    # Gap areas — included to be honest, always score 0-1
    {
        'task': 'Cybersecurity / FISMA / Zero Trust',
        # Use specific phrases to avoid false positives:
        # 'soc' matches 'social', 'associated' etc; 'ato' matches 'data operations', 'nato' etc
        'kw': ['cybersecurity','fisma','zero trust','authorization to operate',' ato ','authority to operate',
               'security operations center','vulnerability management','nist 800-','pen testing',
               'penetration testing','cyber defense','incident response','security assessment',
               'information security','information assurance','splunk','devsecops','siem'],
        'pp_refs': [],
        'base_score': 0,
        'note': 'BLN24 gap — no confirmed prime cybersecurity delivery; would need dedicated cyber partner'
    },
    {
        'task': 'IT Infrastructure & Telecommunications',
        # Use specific full-word phrases; 'lan' and 'wan' match too many false positives (plan, planning, landscape)
        'kw': ['it infrastructure','network infrastructure','server hosting services','telecommunications services',
               'telephony services','wide area network','local area network','wireless network infrastructure',
               'data center operations','network engineering','fiber optic','network connectivity'],
        'pp_refs': [],
        'base_score': 0,
        'note': 'BLN24 gap — no IT infrastructure prime on record'
    },
    {
        'task': 'Software Development / SDLC',
        'kw': ['software development','application development','full software development lifecycle','sdlc','custom development',
               'software engineering','code development','web application development','api development',
               'adaptive forms','microservices','application modernization services','code enhancement',
               'develop applications','develops tests and deploys'],
        'pp_refs': ['CENSUS_CES', 'CENSUS_SRQA', 'CENSUS_EDL', 'CENSUS_DWS'],
        'base_score': 4,
        'note': 'BLN24 prime — Census CES $7M (OnTheMap, QWI Explorer, Job-to-Job Flows — real federal web applications with coders), Census SRQA full SDLC, Census EDL AWS platform, Census DWS AEM (largest federal AEM deployment), IRS Forms CI/CD'
    },
    {
        'task': 'Cloud Engineering / Infrastructure as Code',
        'kw': ['cloud migration','infrastructure as code','iac','aws','amazon web services','azure','cloud platform',
               'cloud architecture','cloud infrastructure','cloud services'],
        'pp_refs': ['CENSUS_MAF', 'NOAA_CLOUD', 'CENSUS_EDL'],
        'base_score': 3,
        'note': 'BLN24 prime (direct + JV) — Census MAF/TIGER cloud migration $4.5M (IaC, automated deployment), Census EDL AWS platform, NOAA cloud migration $7M via Clarity24'
    },
    {
        'task': 'DevSecOps / CI/CD Pipelines',
        'kw': ['devsecops','devops','ci/cd','jenkins','pipeline automation','containerization','kubernetes','docker',
               'continuous integration','continuous deployment','automated testing pipeline','release management'],
        'pp_refs': ['CENSUS_SRQA'],
        'base_score': 2,
        'note': 'Adjacent (2/4) — Census SRQA used agile + DevSecOps principles; IRS Forms Mod used CI/CD pipelines. Not standalone DevSecOps prime but confirmed delivery within broader contracts.'
    },
    {
        'task': 'CRM / Salesforce Implementation',
        'kw': ['crm','salesforce','microsoft dynamics','servicenow','customer relationship management'],
        'pp_refs': [],
        'base_score': 0,
        'note': 'BLN24 gap — no CRM implementation prime on record'
    },
    {
        'task': 'Training & eLearning Development',
        'kw': ['elearning','e-learning','training development','instructional design','lms','learning management','curriculum development','course development'],
        'pp_refs': [],
        'base_score': 1,
        'note': 'BLN24 adjacent — HHS/CDC knowledge transfer work exists but no standalone eLearning prime'
    },
    {
        'task': 'Workforce / Talent Development',
        'kw': ['workforce development','talent acquisition','recruitment','staffing','hr support','human resources','skills development'],
        'pp_refs': [],
        'base_score': 0,
        'note': 'BLN24 gap — not a service lane; teaming partner required'
    },
    {
        'task': 'IT Program Management / CIO Support',
        'kw': ['it governance','enterprise architecture','it portfolio','cio support','it strategy','capital planning','it program management'],
        'pp_refs': [],
        'base_score': 1,
        'note': 'BLN24 adjacent — program management embedded in delivery but no CIO-shop standalone prime'
    },
    {
        'task': 'Scientific / Laboratory Support',
        'kw': ['laboratory','scientific support','lab services','biological sampling','hatchery','aquatic','research program','scientific research'],
        'pp_refs': [],
        'base_score': 0,
        'note': 'BLN24 gap — not a service lane'
    },
    {
        'task': 'Medical Services',
        'kw': ['medical services','clinical','physician','nursing','patient care','medical support','healthcare provider','pathology'],
        'pp_refs': [],
        'base_score': 0,
        'note': 'BLN24 gap — not a service lane'
    },
    {
        'task': 'Space / Defense / ITAR',
        'kw': ['space technology','surveillance','reconnaissance','itar','missile','warfighter','tactical','cmmc level 2','signals intelligence'],
        'pp_refs': [],
        'base_score': 0,
        'note': 'BLN24 gap — not a service lane'
    },
]

SCORE_LABEL = {
    4: '4 — Highly Similar PP (≤3 yrs)',
    3: '3 — Similar PP (≤3 yrs)',
    2: '2 — Related PP, different context',
    1: '1 — Limited / Adjacent Experience',
    0: '0 — No Experience (Gap)',
}

SCORE_STATUS = {4: 'prime', 3: 'prime', 2: 'jv', 1: 'jv', 0: 'gap'}


def build_matrix(opp):
    text = (
        (opp.get('title') or '') + ' ' +
        (opp.get('summary') or '') + ' ' +
        (opp.get('description') or '')
    ).lower()

    matched_tasks = []
    for task in TASK_AREAS:
        hits = [k for k in task['kw'] if k in text]
        if hits:
            score = task['base_score']
            pp_refs = [PP[ref]['ref'] for ref in task['pp_refs'] if ref in PP]
            matched_tasks.append({
                'task':         task['task'],
                'score':        score,
                'score_label':  SCORE_LABEL[score],
                'status':       SCORE_STATUS[score],
                'pp_refs':      pp_refs,
                'note':         task['note'],
                'triggered_by': hits[:3],
            })

    # Sort: high scores first, gaps last
    matched_tasks.sort(key=lambda x: -x['score'])

    # Qualifying questions score
    qualify = _qualifying_score(opp, matched_tasks)

    # Overall fit
    fit, fit_reason = _overall_fit(matched_tasks)

    prime_tasks = [t for t in matched_tasks if t['score'] >= 3]
    jv_tasks    = [t for t in matched_tasks if t['score'] == 2]
    gap_tasks   = [t for t in matched_tasks if t['score'] <= 1]
    avg_score   = sum(t['score'] for t in matched_tasks) / len(matched_tasks) if matched_tasks else 0

    return {
        'tasks':         matched_tasks,
        'fit':           fit,
        'fit_reason':    fit_reason,
        'avg_score':     round(avg_score, 1),
        'prime_count':   len(prime_tasks),
        'jv_count':      len(jv_tasks),
        'gap_count':     len(gap_tasks),
        'total_tasks':   len(matched_tasks),
        'qualifying':    qualify,
    }


def _qualifying_score(opp, tasks):
    """Assess the go/no-go qualifying factors BLN24 uses internally."""
    sa = (opp.get('set_aside') or '').lower()
    score = {}

    # Set-aside
    if '8(a)' in sa or '8a' in sa:
        score['set_aside'] = {'q': 'Set-Aside', 'answer': '8(a) — Direct vehicle match', 'score': 5}
    elif 'small business' in sa or 'sba' in sa or 'wosb' in sa:
        score['set_aside'] = {'q': 'Set-Aside', 'answer': 'Small Business set-aside', 'score': 4}
    elif not sa or 'full and open' in sa or 'unrestricted' in sa:
        score['set_aside'] = {'q': 'Set-Aside', 'answer': 'Full & Open — harder to win', 'score': 2}
    else:
        score['set_aside'] = {'q': 'Set-Aside', 'answer': sa[:40], 'score': 3}

    # Capability alignment
    if tasks:
        avg = sum(t['score'] for t in tasks) / len(tasks)
        cap_q = 'Do we have the capabilities needed?'
        if avg >= 3.5: score['capability'] = {'q': cap_q, 'answer': 'Yes — strong alignment', 'score': 5}
        elif avg >= 2.5: score['capability'] = {'q': cap_q, 'answer': 'Mostly — some gap areas', 'score': 3}
        elif avg >= 1.5: score['capability'] = {'q': cap_q, 'answer': 'Partial — significant gaps', 'score': 2}
        else: score['capability'] = {'q': cap_q, 'answer': 'No — primarily gap work', 'score': 1}

    # Notice type
    ncat = opp.get('noticeCategory', '')
    if ncat == 'rfp':
        score['notice'] = {'q': 'Notice Type', 'answer': 'RFP — active solicitation, actionable now', 'score': 5}
    elif ncat == 'rfi':
        score['notice'] = {'q': 'Notice Type', 'answer': 'RFI — intel gathering, position early', 'score': 4}
    elif ncat == 'forecast':
        score['notice'] = {'q': 'Notice Type', 'answer': 'Forecast — early awareness, shape before RFP', 'score': 3}

    # Value
    vl, vh = opp.get('val_low'), opp.get('val_high')
    mid = ((vl or 0) + (vh or 0)) / 2 if (vl or vh) else None
    if mid:
        if mid >= 5000000:
            score['value'] = {'q': 'Contract Value', 'answer': f'${mid/1e6:.1f}M — Tier 2+ (BLN24 has won at this range)', 'score': 4}
        elif mid >= 500000:
            score['value'] = {'q': 'Contract Value', 'answer': f'${mid/1e6:.1f}M — Tier 3 (BLN24 sweet spot)', 'score': 5}
        else:
            score['value'] = {'q': 'Contract Value', 'answer': f'${mid/1e3:.0f}K — Below $500K (small win)', 'score': 2}
    else:
        score['value'] = {'q': 'Contract Value', 'answer': 'Value not listed — check solicitation', 'score': 3}

    return list(score.values())


def _overall_fit(tasks):
    if not tasks:
        return 'Unclassified', 'No task areas identified in scope text — review solicitation directly'

    scores = [t['score'] for t in tasks]
    avg = sum(scores) / len(scores)
    high = [t for t in tasks if t['score'] >= 3]
    gap = [t for t in tasks if t['score'] == 0]
    all_gap = all(t['score'] == 0 for t in tasks)

    if all_gap:
        return 'Pass', 'All identified task areas fall outside BLN24\'s proven delivery lanes'
    if avg >= 3.5 and not gap:
        return 'Strong', 'BLN24 can prime all or most identified task areas with recent past performance'
    if avg >= 2.5 and len(high) >= len(gap):
        high_names = [t['task'] for t in high[:2]]
        gap_names = [t['task'] for t in gap[:2]]
        if gap_names:
            return 'Moderate', f'Can prime: {", ".join(high_names)}. Needs teaming for: {", ".join(gap_names)}'
        return 'Moderate', f'Can prime most: {", ".join(high_names)}. Some areas need partner'
    if avg >= 1.5:
        return 'Weak / JV', 'Majority of task areas require teaming — may not be best lead'
    return 'Pass', 'Scope primarily outside BLN24 delivery lanes'


def main():
    data = json.loads(OPPS_FILE.read_text())
    opps = data['opps']

    for opp in opps:
        opp['capability_matrix'] = build_matrix(opp)

    data['opps'] = opps
    OPPS_FILE.write_text(json.dumps(data, indent=2))
    print(f'Enriched {len(opps)} opps with BLN24-format capability matrices')

    # Print top 8
    print('\n=== TOP 8 — BLN24 CAPABILITY MATRIX ===')
    for opp in sorted(opps, key=lambda x: -x.get('capture_score', 0))[:8]:
        m = opp['capability_matrix']
        print(f'\n[{opp["capture_score"]}pts | {m["fit"]} | Avg score: {m["avg_score"]}/4] {opp["title"][:65]}')
        print(f'  {opp["noticeCategory"].upper()} | {opp["agency"][:45]}')
        print(f'  Tasks matched: {m["total_tasks"]} ({m["prime_count"]} prime · {m["jv_count"]} JV · {m["gap_count"]} gap)')
        for t in m['tasks']:
            pp = (', '.join(t['pp_refs'][:2])) if t['pp_refs'] else 'No PP reference'
            print(f'  [{t["score"]}/4] {t["task"]}')
            print(f'       PP: {pp}')
            if t['score'] == 0: print(f'       ⚠ {t["note"]}')
        print(f'  → {m["fit_reason"]}')


if __name__ == '__main__':
    main()
