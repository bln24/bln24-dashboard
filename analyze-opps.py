#!/usr/bin/env python3
"""
analyze-opps.py
Writes Rex's plain-English analysis to each opp:
  - what_they_need: 2-3 sentence plain English scope summary
  - rex_take: Rex's assessment — fit, risk, recommendation
  - watch_notes: things to monitor / questions to ask
These are manually authored for thin/important opps,
auto-generated from description for opps with good text.
"""

import json, re
from pathlib import Path

OPPS_FILE = Path('/Users/t24/Desktop/T24/dashboard/opps.json')

# Manual analysis for opps with thin descriptions or needing deeper context
# Key = title substring match (case-insensitive)
MANUAL_ANALYSIS = {
    'SETSS IDIQ': {
        'what_they_need': 'NOAA\'s vehicle for Science, Engineering, and Technical Support Services across its research offices — weather, oceans, fisheries, atmospheric research. Task orders span scientific program support, systems engineering, data management, IT systems, and environmental compliance across ~235 NOAA facilities.',
        'rex_take': 'Clarity24 JV has $7M in confirmed NOAA delivery (cloud migration, app modernization), which is real past performance. But SETSS is primarily a science and engineering vehicle — meteorology, oceanography, fisheries, facilities. BLN24\'s lanes (HCD, comms, data analytics) are narrow within this IDIQ. Best path is monitoring for specific task orders in digital/data/comms scope rather than pursuing the IDIQ prime. Due Jan 2027 — early awareness only.',
        'watch_notes': 'Watch for task order RFPs under the existing SETSS vehicle that align with digital, UX, or data analytics scope. Clarity24\'s NOAA relationship is the asset here. Avoid chasing the IDIQ prime unless a teaming partner with deep NOAA scientific credentials is in place.',
        'recommendation': 'Watch / Sub',
    },
    'Decennial Transformation': {
        'what_they_need': 'Census Bureau\'s massive digital modernization initiative — the CenTAM framework — covering IT systems for the 2030 Decennial Census. Includes application development, legacy modernization, cloud migration, data collection platforms, and systems to support economic, geographic, and demographic programs. Multiple separate contract awards expected under this framework.',
        'rex_take': 'Clarity24 JV has direct Census past performance ($4.5M MAF/TIGER modernization, $4.5M EDL Applications, $2.8M NOAA app mod). Census is also BLN24\'s highest-value client ($18.4M). This is a real opportunity — but it\'s a large technology modernization vehicle, not comms or HCD. The question is which specific task areas under CenTAM align with what Clarity24 can actually deliver vs. what larger primes will own. Full & Open means big integrators will compete.',
        'watch_notes': 'Get into the weeds on the CenTAM acquisition structure — it\'s a collection of complementary contracts, not one big award. Find which specific package maps to digital modernization vs. IT infrastructure vs. data engineering. Clarity24 should be positioned for the digital/app mod pieces. Due 2027 — shape now.',
        'recommendation': 'Pursue via Clarity24 JV',
    },
    'Census Transformation': {
        'what_they_need': 'Same as CenTAM above — Census Bureau\'s 2030 Decennial modernization framework. This may be the same opportunity listed twice under different search results.',
        'rex_take': 'Likely same opp as CenTAM Decennial Transformation. Verify if these are the same solicitation or different contract packages under the same framework.',
        'watch_notes': 'Confirm whether this is a duplicate of the Decennial Transformation opp or a separate package.',
        'recommendation': 'Verify / Watch',
    },
    'ADDP Digital Incentives': {
        'what_they_need': 'Census Bureau program using digital incentives (push notifications, targeted outreach, behavioral nudges) to improve survey response rates for the American Community Survey (ACS) and other Census data collection programs. Contractor provides digital engagement tools, incentive design, and behavioral strategies to drive participation.',
        'rex_take': 'This sits squarely in BLN24\'s lane — digital engagement, outreach design, behavioral nudges. Census is the highest-value client ($18.4M in wins). The behavioral science angle connects to the BLN Fors Marsh JV. Main risk: this may be an existing program going to recompete on an existing vehicle. Need to know who the incumbent is and whether it\'s a set-aside.',
        'watch_notes': 'Confirm set-aside type (currently unlisted). Find the incumbent. If it\'s a small business set-aside with a weak incumbent, this is a genuine pursue. Fors Marsh JV is a natural fit for the behavioral/incentive design component.',
        'recommendation': 'Pursue — confirm set-aside',
    },
    'VER Outreach': {
        'what_they_need': 'USCIS needs outreach and education services to raise awareness of E-Verify, SAVE, and I-9 programs among employers. Contractor designs and delivers marketing campaigns, stakeholder communications, content development, and digital outreach to drive employer enrollment in voluntary verification programs.',
        'rex_take': 'Clean BLN24 fit — outreach, stakeholder engagement, content development, digital campaign work. HUD FHEO ($2M) and HRSA Marketing BPA are direct comparables in scope and structure. The "Cybersecurity" flag in the matrix is noise — it likely came from USCIS mentioning SOC compliance in a boilerplate section, not as a deliverable. Real scope here is comms and outreach only. The gap is that USCIS isn\'t a current BLN24 client — cold agency.',
        'watch_notes': 'USCIS is DHS. BLN24 has DHS in the past performance folder. Verify which DHS contract that covers. If it\'s a legitimate past performance claim, this becomes stronger. Research the incumbent.',
        'recommendation': 'Pursue — verify DHS PP claim',
    },
    'MVN LOGOs': {
        'what_they_need': 'USACE New Orleans District needs three large building wrap installs (80" high, custom widths) for its HQ building — corporate branding / environmental graphics. Contractor must produce and install the wraps, obtaining Adobe source files from the government POC.',
        'rex_take': 'BLN24 can design these — MBDA branding and Census visual design are real comparables. But this is a production + installation job, not a strategy engagement. The "Cybersecurity/ATO" flag in the matrix is noise — that\'s boilerplate SOW language, not a real deliverable. Main risk: installation requires a local New Orleans vendor or sub. Small contract (~$50-150K estimated). Not worth the operational complexity unless BLN24 has a production partner in Louisiana.',
        'watch_notes': 'Check if BLN24 has a production/installation sub in the Gulf region. If yes, pursue as a quick win. If no, pass — the margin on a wrap install doesn\'t justify finding a new sub.',
        'recommendation': 'Pursue if production sub exists — otherwise pass',
    },
    'RRB Proactive Lead Generation': {
        'what_they_need': 'Oregon National Guard Recruiting and Retention Battalion needs a specialized digital advertising platform that uses registrar-verified college enrollment data to identify and target eligible recruits across 1,500+ universities. Contractor provides targeted institutional advertising — reaching college students with recruiting messages based on verified enrollment data rather than self-reported job board data.',
        'rex_take': 'BLN24 can do the digital marketing piece — FTC paid media (Fors Marsh JV) and USDA social media are real comparables. But this is military recruiting advertising, which has a specific compliance and targeting context BLN24 hasn\'t operated in. The "Workforce/Talent Development" gap flag is real — military recruiting is a specialized lane. Also, Oregon National Guard is a state-level guard unit, which is technically federal but unusual client for BLN24.',
        'watch_notes': 'Verify whether National Guard contracts are federal or SLED. If federal and SBA set-aside, evaluate whether the digital marketing component alone is large enough to pursue. The targeting/data platform component may require a tech partner.',
        'recommendation': 'Weak pursue — verify federal vs SLED status',
    },
    'HCD Due Diligence': {
        'what_they_need': 'Millennium Challenge Corporation (MCC) needs a firm to provide technical advisory consulting for their Human & Community Development (HCD) practice — supporting due diligence on education, workforce development, health, and behavioral UX programs in developing countries. Work includes reviewing partner proposals, conducting data-driven analysis, scoping field visits, and supporting capacity building across MCC\'s investment portfolio.',
        'rex_take': 'BLN24\'s HCD capability (IRS $7M BPA) is the strongest match — human-centered design, UX research, behavioral insights. The wrinkle: MCC operates in developing countries, not domestic federal agencies. The scope requires international development context and subject matter expertise in education/workforce systems in developing economies. BLN24 doesn\'t have that track record. Due April 23 — three days out. Cold agency, international context, 3-day window = cold submission. Pattern that loses. Unless Brian has an MCC relationship, this is a pass despite the HCD alignment.',
        'watch_notes': 'Ask Brian: any MCC relationship? Any international development teaming partner? If no to both, this is a training exercise — not a real pursue. Flag MCC as an agency to build toward for future cycles.',
        'recommendation': 'Pass — cold agency, international context, 3-day deadline',
    },
    'Non-Telecommunication Support': {
        'what_they_need': 'DOT OCIO needs support for its Common Operating Environment (COE) — specifically the non-core telecommunications components: server hosting, network connectivity, cybersecurity operations, disaster recovery, wireless services, incident management, help desk, and move/add/change support across DOT HQ and field sites nationwide.',
        'rex_take': 'This is pure IT infrastructure — servers, networking, telecom, security operations. The "Strategic Communications" hit in the matrix was noise from the word "communications" appearing in the description. Zero BLN24 delivery lanes here. The description is explicit: server hosting, wireless infrastructure, incident management. Pass.',
        'watch_notes': 'Remove "communications services" from the comms keyword set if it\'s triggering on IT infrastructure descriptions — it\'s causing false positives.',
        'recommendation': 'Pass — IT infrastructure, not BLN24 scope',
    },
    'LCOMMS Recompete': {
        'what_they_need': 'NOAA recompete of its Laboratory Communications support vehicle — likely covering internal communications, public affairs, digital communications, or science communications support across NOAA labs and research programs.',
        'rex_take': 'LCOMMS (Lab Comms) at NOAA is right in BLN24\'s lane if it\'s science communications, digital content, or public affairs support. NOAA is a past performance agency ($7M via Clarity24). Need to confirm scope before evaluating — "LCOMMS" is ambiguous.',
        'watch_notes': 'Pull the existing LCOMMS contract from USASpending to understand scope. If it\'s science comms/outreach, this is a genuine pursue. If it\'s IT/network comms infrastructure, pass.',
        'recommendation': 'Research scope — potential strong pursue',
    },
}

def generate_auto_analysis(opp):
    """Generate a basic analysis from description text for opps without manual analysis."""
    desc = (opp.get('description') or '') + ' ' + (opp.get('summary') or '')
    title = opp.get('title', '')
    agency = opp.get('agency', '')
    nc = opp.get('noticeCategory', '')
    sa = opp.get('set_aside', '') or 'None listed'
    cm = opp.get('capability_matrix', {})
    fit = cm.get('fit', 'Unclassified')
    avg = cm.get('avg_score', 0)

    prime_tasks = [t for t in cm.get('tasks', []) if t.get('score', 0) >= 3]
    gap_tasks = [t for t in cm.get('tasks', []) if t.get('score', 0) == 0]

    what = desc[:400].strip() if desc.strip() else 'Scope not available in HigherGov — view solicitation directly.'

    if fit == 'Strong' and prime_tasks:
        take = f'BLN24 has strong capability alignment on this opp. Key areas: {", ".join(t["task"] for t in prime_tasks[:3])}. Past performance backs it up. Worth a closer look.'
    elif fit in ('Moderate', 'Weak / JV') and prime_tasks:
        prime_str = ', '.join(t['task'] for t in prime_tasks[:2])
        gap_str = ', '.join(t['task'] for t in gap_tasks[:2]) if gap_tasks else 'none'
        take = f'BLN24 can cover: {prime_str}. Gap areas requiring teaming: {gap_str}. Evaluate whether the BLN24 scope is large enough to prime.'
    elif fit == 'Pass':
        take = 'Scope falls outside BLN24 proven delivery lanes. Pass unless a specific sub opportunity exists.'
    else:
        take = f'Limited scope data available. Review full solicitation before evaluating. Set-aside: {sa}.'

    return {
        'what_they_need': what,
        'rex_take': take,
        'watch_notes': f'Review the full solicitation at source. Set-aside: {sa}. Notice type: {nc.upper()}.',
        'recommendation': fit if fit != 'Unclassified' else 'Review Needed',
    }


def main():
    data = json.loads(OPPS_FILE.read_text())
    opps = data['opps']

    manual_count = 0
    auto_count = 0

    for opp in opps:
        title = (opp.get('title') or '').lower()

        # Check for manual analysis
        matched = None
        for key, analysis in MANUAL_ANALYSIS.items():
            if key.lower() in title:
                matched = analysis
                break

        if matched:
            opp['rex_analysis'] = matched
            manual_count += 1
        else:
            opp['rex_analysis'] = generate_auto_analysis(opp)
            auto_count += 1

    data['opps'] = opps
    OPPS_FILE.write_text(json.dumps(data, indent=2))
    print(f'Analysis written: {manual_count} manual + {auto_count} auto-generated = {len(opps)} total')


if __name__ == '__main__':
    main()
