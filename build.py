#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les fiches HTML depuis les fichiers de contenu /content/properties/*.md
Photos hébergées en local (uploads/). Galerie complète + lightbox."""
import re, os, json, shutil, urllib.parse, yaml

ROOT = os.path.dirname(os.path.abspath(__file__))
ICONS = json.load(open(os.path.join(ROOT, 'icon_library.json'), encoding='utf-8'))
CONTENT = os.path.join(ROOT, 'content')
PROPDIR = os.path.join(CONTENT, 'properties')
UPLOADS = os.path.join(CONTENT, 'uploads')
OUT = os.path.join(ROOT, 'build')

TEMPLATE = open(os.path.join(ROOT, 'template.html'), encoding='utf-8').read()
SPEC_ICONS = json.load(open(os.path.join(ROOT, 'spec_icons.json')))
WIDGET = open(os.path.join(ROOT, 'booking_widget.html'), encoding='utf-8').read()
CONTACT = open(os.path.join(ROOT, 'booking_contact.html'), encoding='utf-8').read()

ACTIVE = {67356, 66303, 137400}  # Nîmes : réservation en ligne active

def parse_md(path):
    txt = open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', txt, re.S)
    data = yaml.safe_load(m.group(1)) or {}
    data['description'] = m.group(2).strip()
    return data

def esc(s): return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def render_specs(specs):
    out = []
    for i, s in enumerate(specs[:4]):
        icon = SPEC_ICONS[i] if i < len(SPEC_ICONS) else SPEC_ICONS[-1]
        m = re.match(r'^\s*([0-9]+|✓|—)\s*(.*)$', s)
        if m: val, lab = m.group(1), m.group(2)
        else: val, lab = '✓', s
        out.append(f'<div class="spec">{icon}<div class="t"><b>{esc(val)}</b><span>{esc(lab)}</span></div></div>')
    return '\n'.join(out)

def render_gallery(photos):
    photos = [(p[1:] if isinstance(p, str) and p.startswith('/') else p) for p in (photos or [])]
    if not photos:
        return '<div class="gal" style="margin-top:12px"></div>'
    cells = []
    cells.append(f'<img class="big" src="{photos[0]}" onclick="lbOpen(0)">')
    for i in range(1, min(6, len(photos))):
        cells.append(f'<div><img src="{photos[i]}" loading="lazy" onclick="lbOpen({i})"></div>')
    if len(photos) > 6:
        extra = len(photos) - 6
        label = f'+ {extra} photo' + ('s' if extra > 1 else '')
        cells.append(f'<div class="more" onclick="lbOpen(6)"><img src="{photos[6]}" loading="lazy"><span>{label}</span></div>')
    grid = '<div class="gal" style="margin-top:12px">\n' + '\n'.join(cells) + '\n</div>'
    # lightbox data + markup
    arr = json.dumps(photos)
    lb = f'''
<div id="lightbox" onclick="lbBg(event)">
  <span id="lbClose" onclick="lbClose()">×</span>
  <span id="lbPrev" onclick="lbNav(-1)">‹</span>
  <img id="lbImg" src="">
  <span id="lbNext" onclick="lbNav(1)">›</span>
  <div id="lbCount"></div>
</div>
<script>
var lbPhotos = {arr}, lbI = 0;
function lbOpen(i){{lbI=i;document.getElementById('lbImg').src=lbPhotos[i];
  document.getElementById('lbCount').textContent=(i+1)+' / '+lbPhotos.length;
  document.getElementById('lightbox').style.display='flex';}}
function lbClose(){{document.getElementById('lightbox').style.display='none';}}
function lbNav(d){{lbI=(lbI+d+lbPhotos.length)%lbPhotos.length;lbOpen(lbI);}}
function lbBg(e){{if(e.target.id==='lightbox')lbClose();}}
document.addEventListener('keydown',function(e){{
  if(document.getElementById('lightbox').style.display==='flex'){{
    if(e.key==='Escape')lbClose();if(e.key==='ArrowRight')lbNav(1);if(e.key==='ArrowLeft')lbNav(-1);}}}});
</script>'''
    return grid + lb

LB_CSS = '''
#lightbox{display:none;position:fixed;inset:0;z-index:999;background:rgba(20,20,16,.94);
  align-items:center;justify-content:center}
#lightbox img{max-width:88vw;max-height:84vh;object-fit:contain;border-radius:2px;box-shadow:0 10px 40px rgba(0,0,0,.5)}
#lbClose{position:absolute;top:18px;right:26px;font-size:40px;color:#fff;cursor:pointer;line-height:1;opacity:.85}
#lbPrev,#lbNext{position:absolute;top:50%;transform:translateY(-50%);font-size:54px;color:#fff;cursor:pointer;
  user-select:none;padding:0 22px;opacity:.8;transition:opacity .2s}
#lbPrev:hover,#lbNext:hover,#lbClose:hover{opacity:1}
#lbPrev{left:10px}#lbNext{right:10px}
#lbCount{position:absolute;bottom:22px;left:50%;transform:translateX(-50%);color:#fff;font-size:13px;
  letter-spacing:.1em;opacity:.85}
.gal .big,.gal img{cursor:pointer}
@media(max-width:600px){#lbPrev,#lbNext{font-size:38px;padding:0 12px}}
'''

def render_amenities(ams):
    out = []
    for a in ams:
        if isinstance(a, dict):
            label, icon = a.get('label', ''), a.get('icon', 'Défaut')
        else:
            label, icon = a, 'Défaut'
        svg = ICONS.get(icon, ICONS['Défaut'])
        out.append(f'<div class="it">{svg}<span>{esc(label)}</span></div>')
    return '\n'.join(out)

def render_points(points):
    return '<ul>\n' + '\n'.join(f'<li>{esc(p)}</li>' for p in points) + '\n</ul>'

def render_desc(body):
    paras = [p.strip() for p in body.split('\n\n') if p.strip()]
    lead = f'<p class="lead">{esc(paras[0])}</p>' if paras else ''
    prose = '<div class="prose">' + ''.join(f'<p>{esc(p)}</p>' for p in paras[1:]) + '</div>' if len(paras) > 1 else '<div class="prose"></div>'
    return lead, prose

def render_booking(propid):
    if int(propid) in ACTIVE:
        w = WIDGET
        # remplacer le propid partout dans le widget
        w = re.sub(r'bookWidget-37951-\d+-0-(\d+)', lambda m: f'bookWidget-37951-{propid}-0-'+m.group(1), w)
        w = re.sub(r'propid:\s*\d+', f'propid:{propid}', w)
        return w
    return CONTACT

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    # 1. pages annexes (accueil, histoire, guides, légal, img/, en/)
    STATIC = os.path.join(ROOT, 'static')
    if os.path.isdir(STATIC):
        for item in os.listdir(STATIC):
            s = os.path.join(STATIC, item); d = os.path.join(OUT, item)
            shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy(s, d)
    # 2. photos (content/uploads -> build/uploads)
    os.makedirs(os.path.join(OUT, 'uploads'), exist_ok=True)
    for f in os.listdir(UPLOADS):
        shutil.copy(os.path.join(UPLOADS, f), os.path.join(OUT, 'uploads', f))
    # 3. interface d'admin (build/admin/)
    ADMIN = os.path.join(ROOT, 'admin')
    if os.path.isdir(ADMIN):
        shutil.copytree(ADMIN, os.path.join(OUT, 'admin'))
    # 4. fiches générées depuis le contenu
    done = []
    for fn in sorted(os.listdir(PROPDIR)):
        if not fn.endswith('.md'): continue
        d = parse_md(os.path.join(PROPDIR, fn))
        lead, prose = render_desc(d['description'])
        html = TEMPLATE
        repl = {
            'ACCENT': d.get('accent', '#5E6B45'),
            'NAME': esc(d.get('name', '')),
            'TAGLINE': esc(d.get('tagline', '')),
            'POLE': esc(d.get('pole', '')),
            'SPECS': render_specs(d.get('specs', [])),
            'GALLERY': render_gallery(d.get('photos', [])),
            'LEAD': lead,
            'PROSE': prose,
            'AMENITIES': render_amenities(d.get('amenities', [])),
            'ADDRESS': esc(d.get('adresse', '')),
            'POINTS': render_points(d.get('points', [])),
            'DISCLAIMER': esc(d.get('disclaimer', '')),
            'MAPQ': urllib.parse.quote(d.get('pole', '') + ', France'),
            'BOOKING': render_booking(d.get('beds24_propid', 0)),
        }
        for k, v in repl.items():
            html = html.replace('{{' + k + '}}', v)
        # injecter le CSS lightbox avant </style>
        html = html.replace('</style>', LB_CSS + '\n</style>', 1)
        # nettoyer accent restant dans icônes génériques
        html = html.replace('{{ACCENT}}', d.get('accent', '#5E6B45'))
        open(os.path.join(OUT, d['slug'] + '.html'), 'w', encoding='utf-8').write(html)
        done.append((d['slug'], len(d.get('photos', [])), len(d.get('amenities', [])), int(d.get('beds24_propid', 0)) in ACTIVE))
    return done

if __name__ == '__main__':
    for s in build():
        print('  %-12s %2d photos | %2d équip | résa=%s' % (s[0], s[1], s[2], 'widget' if s[3] else 'contact'))
