from pathlib import Path
from collections import Counter,defaultdict
from statistics import median
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).parent
rows=json.loads((P/'observations.json').read_text(encoding='utf8'))
current=[r for r in rows if r.get('rank') is not None]
days=defaultdict(dict)
for r in current: days[r['date']][r['work_id']]=r
print('CURRENT',len(current),'unique',len({r['work_id'] for r in current}))
print('MISSING_GENRES',[(d,dict(Counter(r['genre_key'] for r in rs.values()))) for d,rs in days.items() if len(rs)!=200])
print('INTRO_COVERAGE',[(d,sum(bool(r.get('intro')) for r in rs.values()),len(rs)) for d,rs in days.items() if d in ['2026-07-31','2026-08-31','2026-09-11','2026-09-16','2026-09-18','2026-09-24']])
latest=days['2026-09-24']
out={}
for start,end in [('2026-08-01','2026-08-08'),('2026-08-31','2026-09-07'),('2026-09-11','2026-09-18'),('2026-09-18','2026-09-24')]:
    a,b=days[start],days[end]
    n=(__import__('datetime').date.fromisoformat(end)-__import__('datetime').date.fromisoformat(start)).days
    comp=[]
    for id in a.keys() & b.keys():
        r=b[id];p=a[id]; diff=r['star']-p['star']
        comp.append({'work_id':id,'title':r['title'],'genre':r['genre'],'rank':r['rank'],'rank_start':p['rank'],'star_start':p['star'],'star':r['star'],'gain':diff,'per_day':round(diff/n,2),'elapsed_days':r['elapsed_days'],'intro':r.get('intro'),'url':r['work_url']})
    comp.sort(key=lambda r:-r['per_day'])
    out[start+'_'+end]=comp
    print('PERIOD',start,end,'days',n,'paired',len(comp),'entry',len(b.keys()-a.keys()),'exit',len(a.keys()-b.keys()))
    for g in ['現代ファンタジー','異世界ファンタジー']:
        gs=[r for r in comp if r['genre']==g];print('GENRE',g,len(gs),'median/day',median(r['per_day'] for r in gs))
        for r in gs[:12]:print(json.dumps({k:v for k,v in r.items() if k not in ('intro','url')},ensure_ascii=False))
(P/'comparisons.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('LATEST_AGE',dict(Counter('<=30' if r['elapsed_days']<=30 else '31-60' if r['elapsed_days']<=60 else '>60' for r in latest.values())))
print('LATEST_GENRE_AGE',[(g,median(r['elapsed_days'] for r in latest.values() if r['genre']==g),sum(r['elapsed_days']<=30 for r in latest.values() if r['genre']==g)) for g in ['現代ファンタジー','異世界ファンタジー']])
print('SEPT24_NEW',dict(Counter(r['genre'] for r in latest.values() if r['区分']=='新規')))
print('SEPT24_FANTASY_PRIOR',Counter(r['区分'] for r in latest.values() if r['genre_key']=='fantasy'))
print('SEPT24_FANTASY_REOBSERVED21',len({i for i,r in latest.items() if r['genre_key']=='fantasy'} & days['2026-09-21'].keys()))
print('GENRE_TOP20')
for g in ['action','fantasy']:
    for r in sorted([r for r in latest.values() if r['genre_key']==g],key=lambda r:r['rank'])[:20]:
        print(json.dumps({k:r.get(k) for k in ('work_id','genre','rank','title','star','elapsed_days')},ensure_ascii=False))
