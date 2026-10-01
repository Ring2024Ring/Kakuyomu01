import urllib.request,sys,json,datetime
from collections import Counter
from pathlib import Path
from lxml import html
sys.stdout.reconfigure(encoding='utf-8')
out={}
for genre in ['all']:
    u=f'https://kakuyomu.jp/rankings/{genre}/weekly?work_variation=all'
    if genre=='all':s=Path(__file__).with_name('live_all_weekly.html').read_bytes()
    else:s=urllib.request.urlopen(u,timeout=30).read()
    t=html.fromstring(s)
    items=t.xpath('//li[contains(@class,"Rankings_item")]')
    rs=[]
    for i,item in enumerate(items,1):
        title=item.xpath('.//h3//a[starts-with(@href,"/works/")]')[0]
        href=title.get('href')
        links=item.xpath('.//a[@href=$url]',url=href)
        intro=links[-1].text_content().strip()
        genres=item.xpath('.//a[starts-with(@href,"/genres/")]')
        rs.append({'rank':i,'title':title.text_content(),'url':'https://kakuyomu.jp'+href,'genre':[x.text_content() for x in genres],'intro':intro})
    out[genre]={'url':u,'checked_at':datetime.datetime.now().isoformat(),'rows':rs}
    print(genre,'rows',len(rs),'top20_genres',dict(Counter(g for r in rs[:20] for g in r['genre'])))
    for r in rs[:(20 if genre=='all' else 5)]:
        print(json.dumps({k:v for k,v in r.items() if k!='intro'},ensure_ascii=False))
        if genre not in ['all','romance','love_story']:print(r['intro'])
Path(__file__).with_name('live_rankings.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
