#!/usr/bin/env python3
"""
USASpending.gov API lookup for agency-specific contract winners.
Use this to update agency-winners.json with real data.
No API key required.
"""
import json, urllib.request, time
from pathlib import Path

AGENCY_WINNERS_FILE = Path('/Users/t24/Desktop/T24/hg-proxy/agency-winners.json')

AGENCY_MAP = {
    'U.S. Census Bureau': 'census_bureau',
    'Internal Revenue Service': 'irs',
    'Centers for Medicare & Medicaid Services': 'cms',
    'Drug Enforcement Administration': 'dea',
    'U.S. Citizenship and Immigration Services': 'dhs_uscis',
    'Department of Housing and Urban Development': 'hud',
    'Centers for Disease Control and Prevention': 'cdc',
    'Millennium Challenge Corporation': 'mcc',
    'Department of Education': 'education',
}

# BLN24 key NAICS codes by work type
NAICS_BY_TYPE = {
    'tech_modernization': ['541511', '541512', '541519'],
    'comms_outreach': ['541613', '541820', '541430'],
    'data_analytics': ['541511', '541519', '518210'],
    'hcd_ux': ['541511', '541990'],
}


def usaspending_search(agency_name, naics_codes, years_back=3, limit=20):
    """Search USASpending.gov for recent contract winners at a specific agency."""
    from datetime import datetime, timedelta
    start_date = (datetime.now() - timedelta(days=years_back * 365)).strftime('%Y-%m-%d')
    
    payload = json.dumps({
        'filters': {
            'time_period': [{'start_date': start_date, 'end_date': '2026-12-31'}],
            'agencies': [{'type': 'awarding', 'tier': 'subtier', 'name': agency_name}],
            'naics_codes': naics_codes,
            'award_type_codes': ['A', 'B', 'C', 'D'],
        },
        'fields': ['Recipient Name', 'Award Amount', 'Description', 
                   'Period of Performance Start Date', 'Type', 'recipient_uei',
                   'Recipient UEI', 'NAICS Code', 'awarding_agency_name'],
        'sort': 'Award Amount',
        'order': 'desc',
        'limit': limit,
        'page': 1,
    }).encode()
    
    req = urllib.request.Request(
        'https://api.usaspending.gov/api/v2/search/spending_by_award/',
        data=payload,
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            result = json.loads(r.read())
        return result.get('results', [])
    except Exception as e:
        print(f'  USASpending error for {agency_name}: {e}')
        return []


def pull_agency_winners(agency_name, work_type, agency_key, sub_key, limit=10):
    """Pull top winners at an agency for a given work type and format for agency-winners.json."""
    naics_codes = NAICS_BY_TYPE.get(work_type, NAICS_BY_TYPE['tech_modernization'])
    
    print(f'\nPulling {agency_name} / {work_type}...')
    results = usaspending_search(agency_name, naics_codes, limit=limit)
    
    if not results:
        print(f'  No results')
        return []
    
    winners = []
    seen = set()
    for r in results:
        name = r.get('Recipient Name', '?')
        amt = r.get('Award Amount', 0) or 0
        desc = (r.get('Description') or '')[:80]
        uei = r.get('Recipient UEI') or r.get('recipient_uei') or ''
        naics = r.get('NAICS Code', '')
        
        if name in seen or amt < 100000:  # skip tiny contracts
            continue
        seen.add(name)
        
        hg_url = f'https://www.highergov.com/awardee/?search={urllib.parse.quote(name.split()[0])}'
        
        winner = {
            'name': name,
            'why': f'Won ${amt/1e6:.1f}M at {agency_name} for {desc[:60]}. Agency-confirmed track record for this type of work.',
            'url': hg_url,
            'evidence': f'{agency_name} ${amt/1e6:.1f}M — {desc[:70]} (USASpending confirmed)',
            'amount_m': round(amt / 1e6, 1),
            'description': desc,
            'naics': naics,
            'sa': '',  # would need another lookup to determine set-aside
        }
        winners.append(winner)
        print(f'  {name[:40]} | ${amt/1e6:.1f}M | {desc[:50]}')
    
    return winners


def update_agency_winners_db():
    """Pull fresh data for key agencies and update the database."""
    import urllib.parse
    
    winners_db = json.loads(AGENCY_WINNERS_FILE.read_text())
    
    # Define what to pull
    lookups = [
        ('U.S. Census Bureau', 'tech_modernization', 'census_bureau', 'app_modernization_sb'),
        ('Centers for Medicare & Medicaid Services', 'tech_modernization', 'cms', 'tech_sb'),
        ('Centers for Medicare & Medicaid Services', 'hcd_ux', 'cms', 'hcd_sb'),
        ('Internal Revenue Service', 'hcd_ux', 'irs', 'hcd_sb'),
        ('Department of Housing and Urban Development', 'comms_outreach', 'hud', 'comms_sb'),
        ('Centers for Disease Control and Prevention', 'comms_outreach', 'cdc', 'comms_sb'),
        ('Drug Enforcement Administration', 'tech_modernization', 'doj_dea', 'web_comms_sb'),
    ]
    
    for agency_name, work_type, agency_key, sub_key in lookups:
        winners = pull_agency_winners(agency_name, work_type, agency_key, sub_key)
        if winners:
            if agency_key not in winners_db:
                winners_db[agency_key] = {}
            winners_db[agency_key][sub_key + '_usaspending'] = winners
            winners_db[agency_key]['_last_pulled'] = '2026-04-22'
        time.sleep(1)  # be nice to USASpending
    
    AGENCY_WINNERS_FILE.write_text(json.dumps(winners_db, indent=2))
    print(f'\nSaved updated agency-winners.json')


if __name__ == '__main__':
    import urllib.parse
    print('Pulling agency-specific winner data from USASpending.gov...')
    update_agency_winners_db()
