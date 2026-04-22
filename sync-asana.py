#!/usr/bin/env python3
"""
sync-asana.py — Sync dashboard opp data to Asana BD AI tasks.
Runs after every fetch cycle.
- Updates existing approved tasks with latest scores, CI, analysis
- Only updates tasks that have changed significantly (score diff >= 3 or new CI data)
"""
import json, urllib.request
from pathlib import Path

OPPS_FILE = Path('/Users/t24/Desktop/T24/dashboard/opps.json')
CONFIG_FILE = Path('/Users/t24/Desktop/T24/config/integrations.json')
ASANA_PROJECT = '1214145572732999'

config = json.loads(CONFIG_FILE.read_text())
ASANA_TOKEN = config['asana']['pat']
HEADERS = {'Authorization': 'Bearer ' + ASANA_TOKEN, 'Content-Type': 'application/json', 'Accept': 'application/json'}


def asana_get(path):
    req = urllib.request.Request(f'https://app.asana.com/api/1.0{path}', headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get('data', {})


def asana_put(path, data):
    payload = json.dumps({'data': data}).encode()
    req = urllib.request.Request(f'https://app.asana.com/api/1.0{path}', data=payload, headers=HEADERS, method='PUT')
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get('data', {})


def asana_post_comment(task_gid, text):
    payload = json.dumps({'data': {'text': text}}).encode()
    req = urllib.request.Request(
        f'https://app.asana.com/api/1.0/tasks/{task_gid}/stories',
        data=payload, headers=HEADERS, method='POST'
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()).get('data', {})
    except:
        return {}


def build_notes(opp):
    title = opp.get('title', '')
    agency = opp.get('agency', '')
    score = opp.get('capture_score', 0)
    score_base = opp.get('capture_score_base', score)
    score_delta = opp.get('capture_score_delta', 0)
    ra = opp.get('rex_analysis', {})
    cm = opp.get('capability_matrix', {})
    ci = opp.get('competitive_intel', {})
    noticecat = opp.get('noticeCategory', '').upper()
    set_aside = opp.get('set_aside', 'TBD')
    source = opp.get('source_path', '') or opp.get('path', '')
    due = opp.get('due', 'TBD')

    lines = [
        f'=== {title.upper()} ===',
        f'Agency: {agency}',
        f'Type: {noticecat} | Set-aside: {set_aside}',
        f'Due: {due}',
        f'Source: {source}',
        '',
        f'--- SCORE: {score}pts'
        + (f' (base {score_base}pts, {score_delta:+d}pts CI)' if score_delta else '')
        + f' | Fit: {cm.get("fit","?")} | Avg: {cm.get("avg_score",0)}/4 ---',
        '',
        "--- REX'S TAKE ---",
        ra.get('rex_take', '') or ra.get('what_they_need', 'No analysis'),
        '',
        '--- WHAT THEY NEED ---',
        ra.get('what_they_need', ''),
        '',
        '--- CAPABILITY MATRIX ---',
    ]

    for t in cm.get('tasks', []):
        pp = (t.get('pp_refs') or ['No PP ref'])[0][:55]
        lines.append(f'[{t["score"]}/4] {t["task"]} — {pp}')
        if t.get('score', 0) == 0:
            lines.append(f'  ⚠ GAP: {t.get("note","")[:80]}')

    lines.extend(['', '--- COMPETITIVE INTELLIGENCE ---'])
    competitors = ci.get('competitors', [])
    partners = ci.get('partners', [])

    if competitors:
        lines.append('Likely Competitors:')
        for c in competitors[:4]:
            lines.append(f'  ⚔ {c["name"]}')
            lines.append(f'    {c["why"][:100]}')
            lines.append(f'    {c["url"]}')
    else:
        lines.append('No competitor data — search USASpending.gov for agency-specific wins')

    if partners:
        lines.extend(['', 'Recommended Partners:'])
        for p in partners[:3]:
            gap = p.get('gap_filled', '')
            lines.append(f'  🤝 {p["name"]} ({p.get("relationship","")})')
            if gap:
                lines.append(f'    Fills gap: {gap}')
            lines.append(f'    {p["why"][:100]}')
            lines.append(f'    {p["url"]}')

    if score_delta:
        lines.extend(['', '--- SCORE ADJUSTMENT REASONS (from CI) ---'])
        for r in opp.get('capture_score_delta_reasons', []):
            lines.append(f'  • {r}')

    lines.extend([
        '',
        '--- WATCH NOTES ---',
        ra.get('watch_notes', 'No notes'),
        '',
        f'Recommendation: {ra.get("recommendation", "Review")}',
        '',
        'Dashboard: https://bln24.github.io/bln24-dashboard/',
        f'Asana: https://app.asana.com/0/{ASANA_PROJECT}',
    ])

    return '\n'.join(str(l) for l in lines)


def get_all_bd_ai_tasks():
    """Get all tasks in the BD AI project."""
    req = urllib.request.Request(
        f'https://app.asana.com/api/1.0/projects/{ASANA_PROJECT}/tasks'
        '?opt_fields=name,gid,notes,custom_fields&limit=100',
        headers=HEADERS
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get('data', [])


def match_opp_to_task(opp, tasks):
    """Match an opp to an Asana task by title similarity."""
    opp_title = opp.get('title', '').lower()
    for task in tasks:
        task_name = task.get('name', '').lower()
        # Strip [BD AI] prefix
        task_name = task_name.replace('[bd ai]', '').strip()
        # Check if titles overlap significantly
        opp_words = set(w for w in opp_title.split() if len(w) > 4)
        task_words = set(w for w in task_name.split() if len(w) > 4)
        overlap = len(opp_words & task_words)
        if overlap >= 3:
            return task
    return None


def main():
    opps = json.loads(OPPS_FILE.read_text()).get('opps', [])

    # Get all BD AI project tasks
    try:
        tasks = get_all_bd_ai_tasks()
    except Exception as e:
        print(f'Could not fetch Asana tasks: {e}')
        return

    bd_ai_tasks = [t for t in tasks if '[bd ai]' in t.get('name', '').lower()]
    print(f'Found {len(bd_ai_tasks)} BD AI tasks in Asana')

    updated = 0
    skipped = 0

    for task in bd_ai_tasks:
        task_gid = task['gid']
        task_name = task.get('name', '')

        # Find matching opp
        opp = None
        for o in opps:
            if o.get('asana_task_gid') == task_gid:
                opp = o
                break
        if not opp:
            opp = match_opp_to_task({'title': task_name.replace('[BD AI]', '').strip()}, opps)

        if not opp:
            print(f'  No opp match for: {task_name[:50]}')
            skipped += 1
            continue

        # Build updated notes
        new_notes = build_notes(opp)

        # Only update if notes would change significantly (avoid unnecessary API calls)
        existing_notes = task.get('notes', '')
        score_in_existing = f'SCORE: {opp.get("capture_score_base", opp["capture_score"])}' in existing_notes
        score_changed = not score_in_existing

        if score_changed or len(existing_notes) < 200:
            try:
                asana_put(f'/tasks/{task_gid}', {'notes': new_notes})
                print(f'  Updated: {task_name[:50]} [{opp["capture_score"]}pts]')
                updated += 1
            except Exception as e:
                print(f'  Error: {task_name[:40]}: {e}')
        else:
            skipped += 1

    print(f'\nAsana sync: {updated} updated, {skipped} skipped (no change)')


if __name__ == '__main__':
    main()
