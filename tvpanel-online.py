#!/usr/bin/env python3
"""Original-style gtkdialog TV panel with an IPTV-org catalogue."""
import base64, concurrent.futures, hashlib, html, json, os, re, shlex, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent
CFG=Path.home()/'.config/tvpanel-original'
CACHE=Path.home()/'.cache/tvpanel-original'
DB=CFG/'channels.json'
API='https://iptv-org.github.io/api/'
CHANNELS_PER_PAGE=30
COLUMNS=6
ORIGINAL=[('cgtn_news','cgtn_news.png'),('caglobal_news','caglobal.png'),('fox_news','fox_news.png'),('cna_news','cna_news.png'),('sky_newsuk','sky_news.png'),('aljazeera_hd','aljazeera_hd.png'),('france24_news','france24_news.png'),('abc_news_live','abc_news_live.png'),('dw_news','dw_news.png'),('euro_news','euro_news.png')]

def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f: json.dump(data,f,ensure_ascii=False,indent=2)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def http(url):
    try: return urlsplit(url).scheme in ('http','https') and bool(urlsplit(url).netloc) and not any(x in url for x in '\r\n')
    except (ValueError,AttributeError): return False

def load():
    data=json.loads((DB if DB.exists() else ROOT/'defaults.json').read_text())
    if not isinstance(data,list) or not all(isinstance(c,dict) and isinstance(c.get('name'),str) and http(c.get('url','')) for c in data):
        raise ValueError('The personal channel list is damaged; it has not been overwritten.')
    return data

def save(data):
    CFG.mkdir(parents=True,exist_ok=True)
    if DB.exists(): shutil.copy2(DB,CFG/'channels.json.bak')
    atomic(DB,data)

def dialog(*args):
    p=subprocess.run(['yad','--title=TVPanel',*args],stdout=subprocess.PIPE,text=True)
    return p.returncode,p.stdout.rstrip('\n')

def info(msg): dialog('--info','--text='+html.escape(str(msg)),'--button=Close:0')

def fetch(name,force=False):
    path=CACHE/(name+'.json')
    if path.exists() and not force and time.time()-path.stat().st_mtime<86400:
        return json.loads(path.read_text())
    try:
        req=Request(API+name+'.json',headers={'User-Agent':'TVPanel-Original-Online/1.4'})
        with urlopen(req,timeout=20) as r: raw=r.read(32*1024*1024+1)
        if len(raw)>32*1024*1024: raise ValueError('Catalogue is too large')
        data=json.loads(raw)
        if not isinstance(data,list): raise ValueError('Invalid catalogue')
        atomic(path,data); return data
    except Exception:
        if path.exists(): return json.loads(path.read_text())
        raise

def catalogue_data(force=False):
    progress=subprocess.Popen(['yad','--progress','--pulsate','--auto-close','--no-buttons','--text=Downloading the IPTV-org catalogue…'],stdin=subprocess.PIPE,text=True)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            results=list(ex.map(lambda n:fetch(n,force),('channels','streams','logos','countries')))
        return merge(*results)
    finally:
        if progress.stdin:
            try: progress.stdin.write('100\n'); progress.stdin.close()
            except BrokenPipeError: pass
        try: progress.wait(timeout=2)
        except subprocess.TimeoutExpired: progress.terminate()

def merge(channels,streams,logos,countries):
    meta={c['id']:c for c in channels if c.get('id') and not c.get('is_nsfw') and not c.get('closed')}
    flags={c['code']:c.get('name',c['code']) for c in countries if c.get('code')}
    images={}
    for l in logos:
        if l.get('channel') not in images and l.get('in_use',True) and http(l.get('url','')) and l.get('format') in ('PNG','JPEG','SVG'):
            images[l['channel']]=l['url']
    result=[]; seen=set()
    for s in streams:
        c=meta.get(s.get('channel'))
        if not c or not http(s.get('url','')) or s['url'] in seen: continue
        seen.add(s['url']); code=c.get('country','')
        result.append(dict(name=c['name'],country=flags.get(code,code),code=code,url=s['url'],
            logo=images.get(c['id'],''),quality=s.get('quality') or '',labels=', '.join(s.get('labels') or []),
            referrer=s.get('referrer') or '',user_agent=s.get('user_agent') or ''))
    return sorted(result,key=lambda c:(c['name'].casefold(),c['quality']))

def play(c):
    if not shutil.which('mpv'): return info('mpv is missing. Install it using the package manager.')
    CFG.mkdir(parents=True,exist_ok=True)
    shots=Path('/files/media/images/TV_panel_screenshots'); shots.mkdir(parents=True,exist_ok=True)
    args=['mpv','--geometry=50%:50%','--hwdec=auto-safe','--no-border','--autofit=1280x720','--screenshot-directory='+str(shots)]
    for key,flag in [('referrer','--referrer='),('user_agent','--user-agent=')]:
        value=c.get(key,'')
        if value and not any(x in value for x in '\r\n'): args.append(flag+value)
    with (CFG/'mpv.log').open('w') as log:
        subprocess.Popen(args+['--',c['url']],stdout=log,stderr=log,start_new_session=True)

def icon(c):
    # A physical 96px SVG canvas prevents large source logos from growing the UI.
    CACHE.mkdir(parents=True,exist_ok=True)
    ident=hashlib.sha256(c['url'].encode()).hexdigest()
    source=None
    old=c.get('icon','')
    if old and Path(old).is_file(): source=Path(old)
    if source is None:
        for suffix in ('.png','.jpg'):
            candidate=CACHE/(ident+suffix)
            if candidate.is_file(): source=candidate; break
    content='<rect x="3" y="5" width="26" height="20" rx="3" fill="#20546b" stroke="#64d7ff" stroke-width="2"/><path d="M11 29h10M16 25v4" stroke="#64d7ff" stroke-width="2"/>'
    if source is not None:
        raw=source.read_bytes()
        mime='image/png' if raw.startswith(b'\x89PNG') else 'image/jpeg' if raw.startswith(b'\xff\xd8') else 'image/svg+xml'
        encoded=base64.b64encode(raw).decode('ascii')
        content='<image width="32" height="32" preserveAspectRatio="xMidYMid meet" xlink:href="data:'+mime+';base64,'+encoded+'"/>'
    path=CACHE/(ident+'-icons96.svg')
    svg='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="96" height="96" viewBox="0 0 32 32">'+content+'</svg>'
    if not path.exists() or path.read_text()!=svg: path.write_text(svg)
    return str(path)

def download_icon(c):
    if not http(c.get('logo','')): return
    ident=hashlib.sha256(c['url'].encode()).hexdigest(); CACHE.mkdir(parents=True,exist_ok=True)
    try:
        with urlopen(Request(c['logo'],headers={'User-Agent':'TVPanel/1.0'}),timeout=8) as r:
            raw=r.read(2*1024*1024+1); mime=r.headers.get_content_type()
        suffix={'image/png':'.png','image/jpeg':'.jpg','image/svg+xml':'.svg'}.get(mime)
        # External SVGs may reference remote resources; use generated local SVG instead.
        if suffix in ('.png','.jpg') and len(raw)<=2*1024*1024:
            (CACHE/(ident+suffix)).write_bytes(raw)
    except Exception: pass

def catalogue():
    try: data=catalogue_data()
    except Exception as e: return info('Could not download the catalogue. Check your Internet connection.\n'+str(e))
    while True:
        rc,query=dialog('--form','--width=560','--text=Search by name and/or country. ES: Spain · GB/UK: United Kingdom (includes Scotland).\nLeave both fields empty to show all channels.',
            '--field=Channel name','', '--field=Country (code or name)','', '--separator=\t',
            '--button=Close:1','--button=Refresh catalogue:2','--button=Search:0')
        if rc not in (0,2): return
        if rc==2:
            try: data=catalogue_data(True)
            except Exception as e: info(e)
            continue
        fields=query.split('\t'); name=(fields[0] if fields else '').strip().casefold(); country=(fields[1] if len(fields)>1 else '').strip().casefold()
        aliases={'españa':'es','spain':'es','escocia':'gb','scotland':'gb','edinburgo':'gb','edimburgo':'gb','reino unido':'gb','uk':'gb','edinburgh':'gb'}
        country=aliases.get(country,country)
        if country=='gb': country='uk'
        selected=[c for c in data if name in c['name'].casefold() and (not country or country==c['code'].casefold() or country in c['country'].casefold())]
        if not selected: info('No streams found. Try another name or country.'); continue
        while True:
            args=['--list','--width=980','--height=600','--text=Select a stream: Watch opens mpv; Add saves it as a panel button.\nA channel may have several quality options. Some streams have restrictions.',
                '--column=ID:NUM','--column=Channel','--column=Country','--column=Quality','--column=Notes','--hide-column=1','--print-column=1','--separator=',
                '--search-column=2','--button=Back:1','--button=Watch:0','--button=Add to panel:2']
            for i,c in enumerate(selected): args.extend([str(i),c['name'],c['country'],c['quality'],c['labels']])
            code,out=dialog(*args)
            if code not in (0,2): break
            if not out.isdigit() or int(out)>=len(selected): info('Select a channel.'); continue
            c=selected[int(out)]
            if code==0: play(c)
            else:
                current=load()
                if any(x['url']==c['url'] for x in current): info('This stream is already on the panel.'); continue
                download_icon(c); save(current+[c]); info('Channel added. It will appear when you return to the panel.'); return

def panel_xml(data,page):
    esc=lambda s:html.escape(str(s),quote=True)
    items=data[page*CHANNELS_PER_PAGE:(page+1)*CHANNELS_PER_PAGE]; rows=[]
    for start in range(0,len(items),COLUMNS):
        buttons=[]
        for j,c in enumerate(items[start:start+COLUMNS],page*CHANNELS_PER_PAGE+start):
            cmd=shlex.join([sys.executable,str(ROOT/'tvpanel-online.py'),'play',str(j)])+' &'
            buttons.append('<button relief="2" width-request="104" height-request="104" tooltip-text="'+esc(c['name'])+'"><width>96</width><height>96</height><input file>'+esc(icon(c))+'</input><action>'+esc(cmd)+'</action></button>')
        rows.append('<hbox homogeneous="true" spacing="2">'+''.join(buttons)+'</hbox>')
    def control(stock,tip,action):
        return '<button tooltip-text="'+tip+'"><width>16</width><height>16</height><input file stock="'+stock+'"></input><action type="exit">'+action+'</action></button>'
    controls=control('gtk-add','Add channels from Internet','CATALOG')+control('gtk-remove','Remove channel','REMOVE')
    if page: controls+=control('gtk-go-back','Previous page','PREV')
    if (page+1)*CHANNELS_PER_PAGE<len(data): controls+=control('gtk-go-forward','Next page','NEXT')
    controls+=control('gtk-close','Close','QUIT')
    title='TVPanel 1.4 — '+str(page+1)+'/'+str(max(1,(len(data)+CHANNELS_PER_PAGE-1)//CHANNELS_PER_PAGE))
    return '<window title="'+title+'" resizable="false"><vbox border-width="4" spacing="2">'+''.join(rows)+'<hbox homogeneous="true">'+controls+'</hbox></vbox></window>'

def remove():
    data=load(); args=['--list','--width=600','--height=400','--column=ID','--column=Channel','--hide-column=1','--print-column=1','--separator=','--button=Cancel:1','--button=Remove:0']
    for i,c in enumerate(data): args.extend([str(i),c['name']])
    rc,out=dialog(*args)
    if rc==0 and out.isdigit() and int(out)<len(data):
        rc,_=dialog('--question','--text=Remove this channel from the panel?','--button=Cancel:1','--button=Remove:0')
        if rc==0: data.pop(int(out)); save(data)

def main():
    if len(sys.argv)>1 and sys.argv[1]=='play':
        data=load(); idx=int(sys.argv[2])
        if 0<=idx<len(data): play(data[idx])
        return
    gtk=shutil.which('gtkdialog3') or shutil.which('gtkdialog')
    if not gtk or not shutil.which('yad'): sys.exit('gtkdialog (or gtkdialog3), yad and python3 are required.')
    page=0
    while True:
        data=load(); page=min(page,max(0,(len(data)-1)//CHANNELS_PER_PAGE))
        env=os.environ.copy(); env['TVPANEL_XML']=panel_xml(data,page)
        p=subprocess.run([gtk,'--center','--program=TVPANEL_XML'],env=env,stdout=subprocess.PIPE,text=True)
        match=re.search(r'^EXIT="([A-Z]+)"$',p.stdout,re.M); action=match.group(1) if match else 'QUIT'
        if action=='CATALOG': catalogue(); page=max(0,(len(load())-1)//CHANNELS_PER_PAGE)
        elif action=='REMOVE': remove()
        elif action=='NEXT': page+=1
        elif action=='PREV': page=max(0,page-1)
        else: return

if __name__=='__main__':
    try: main()
    except Exception as e:
        if shutil.which('yad'): info('TVPanel: '+str(e))
        else: print(e,file=sys.stderr)
