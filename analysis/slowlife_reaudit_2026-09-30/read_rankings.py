import json
from pathlib import Path
import openpyxl

root = Path(__file__).resolve().parents[2]
dates = ['2026-09-18', '2026-09-24', '2026-09-30']
observed = {}
for date in dates:
    folder = 'ランキングレポート' if date == dates[-1] else 'reports'
    path = root / folder / f'growth_report_{date}.xlsx'
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = book['全差分'].iter_rows(values_only=True)
    headers = next(rows)
    records = []
    for n, values in enumerate(rows, 2):
        r = dict(zip(headers, values))
        r['source_row'] = n
        r['source_path'] = str(path)
        if r.get('rank') is not None:
            records.append(r)
    observed[date] = {str(r['work_id']): r for r in records}
    book.close()

latest = list(observed[dates[-1]].values())
for r in latest:
    r['observations'] = {d: {k: observed[d][str(r['work_id'])].get(k) for k in ['rank', 'star', 'episodes', 'chars', 'source_row']} for d in dates if str(r['work_id']) in observed[d]}
out = Path(__file__).parent / 'ranking_evidence.json'
out.write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding='utf-8')
print('counts', {g: sum(r['genre'] == g for r in latest) for g in set(r['genre'] for r in latest)})
for r in sorted((r for r in latest if r['genre_key'] == 'fantasy'), key=lambda x:x['rank']):
    a = r['observations'].get(dates[0], {}).get('star')
    delta = r['star'] - a if a is not None else None
    print(json.dumps({k:r.get(k) for k in ['rank','star','episodes','title','catchphrase','source_row']} | {'delta12d':delta}, ensure_ascii=False))
