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

# ============================================================================
#  WhatsApp : pastille flottante (toutes pages) + bloc contact (accueils FR/EN)
#  Injecté au build -> rien à lancer en local, Netlify s'en charge.
# ============================================================================
WA_INTL    = "33669325385"      # numéro international sans le +
WA_DISPLAY = "06 69 32 53 85"   # affichage
WA_LINK    = f"https://wa.me/{WA_INTL}"
TEL_LINK   = f"tel:+{WA_INTL}"

WA_GLYPH = ('M12 2.04c-5.5 0-9.96 4.46-9.96 9.96 0 1.76.46 3.45 1.34 4.96L2 22l5.2-1.36'
            'c1.46.8 3.1 1.22 4.76 1.22h.01c5.5 0 9.96-4.46 9.96-9.96 0-2.66-1.04-5.16-2.92-7.04'
            'A9.9 9.9 0 0 0 12 2.04zm5.84 14.06c-.25.7-1.44 1.33-1.99 1.41-.53.08-1.17.11-1.89-.12'
            '-.44-.14-1-.33-1.72-.64-3.03-1.31-5-4.36-5.16-4.56-.15-.2-1.23-1.63-1.23-3.11s.78-2.21'
            ' 1.05-2.51c.28-.3.6-.38.8-.38.2 0 .4 0 .57.01.18.01.43-.07.67.51.25.6.85 2.08.92 2.23'
            '.08.15.12.32.02.52-.1.2-.15.32-.3.5-.15.18-.31.4-.44.53-.15.15-.3.31-.13.6.17.3.76 1.25'
            ' 1.63 2.02 1.12.99 2.06 1.3 2.36 1.45.3.15.47.12.64-.07.18-.2.74-.86.94-1.16.2-.3.4-.25'
            '.67-.15.28.1 1.75.83 2.05.98.3.15.5.22.57.35.08.13.08.74-.17 1.44z')
PHONE_GLYPH = ('M6.62 10.79a15.5 15.5 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.03-.24 11.4 11.4 0 0 0'
               ' 3.57.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0'
               ' 1 1 1c0 1.24.2 2.44.57 3.57a1 1 0 0 1-.24 1.03l-2.21 2.19z')

WA_FAB = f'''<!-- wa-fab -->
<style>
.wa-fab{{position:fixed;right:18px;bottom:18px;z-index:900;width:56px;height:56px;border-radius:50%;
 background:#25D366;display:flex;align-items:center;justify-content:center;
 box-shadow:0 6px 20px rgba(0,0,0,.25);transition:transform .18s,box-shadow .18s}}
.wa-fab:hover{{transform:translateY(-2px) scale(1.05);box-shadow:0 10px 26px rgba(0,0,0,.32)}}
.wa-fab svg{{width:32px;height:32px;fill:#fff}}
@media(max-width:600px){{.wa-fab{{right:14px;bottom:14px;width:52px;height:52px}}.wa-fab svg{{width:30px;height:30px}}}}
</style>
<a class="wa-fab" href="{WA_LINK}" target="_blank" rel="noopener" aria-label="Contact WhatsApp" title="WhatsApp">
<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{WA_GLYPH}"/></svg></a>
'''

WA_CONTACT_CSS = '''<!-- wa-contact -->
<style>
.wa-contact{margin-top:22px;padding-top:20px;border-top:1px solid var(--ligne,#e5dfd2);text-align:center}
.wa-contact .wa-or{display:block;font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;
 color:var(--soft,#8a8272);margin-bottom:12px}
.wa-contact .wa-links{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.wa-contact a{display:inline-flex;align-items:center;gap:8px;padding:11px 18px;border-radius:4px;
 font-size:14px;text-decoration:none;transition:.18s;border:1px solid transparent}
.wa-contact .wa-line{background:#25D366;color:#fff}
.wa-contact .wa-line:hover{background:#1eba57}
.wa-contact .wa-line svg{width:18px;height:18px;fill:#fff}
.wa-contact .tel-line{background:transparent;color:var(--olivier,#5E6B45);border-color:var(--pierre,#B8AE99)}
.wa-contact .tel-line:hover{border-color:var(--olivier,#5E6B45);background:var(--creme,#F4F0E7)}
.wa-contact .tel-line svg{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:1.7}
</style>
'''

def wa_contact_block(lang):
    wa_label  = f"WhatsApp · {WA_DISPLAY}"
    tel_label = ("Appeler · " if lang == "FR" else "Call · ") + WA_DISPLAY
    intro     = "Ou contactez-nous directement" if lang == "FR" else "Or reach us directly"
    return (WA_CONTACT_CSS +
            f'<div class="wa-contact"><span class="wa-or">{intro}</span><div class="wa-links">'
            f'<a class="wa-line" href="{WA_LINK}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24"><path d="{WA_GLYPH}"/></svg>{wa_label}</a>'
            f'<a class="tel-line" href="{TEL_LINK}">'
            f'<svg viewBox="0 0 24 24"><path d="{PHONE_GLYPH}"/></svg>{tel_label}</a>'
            f'</div></div>\n')

def _inject_before(html, tag, snippet):
    i = html.lower().rfind(tag)
    return html[:i] + snippet + html[i:] if i != -1 else html + snippet

def inject_whatsapp():
    """Passe finale sur build/ : pastille partout + bloc contact sous les 2 formulaires."""
    n_fab = n_ct = 0
    for dp, _, files in os.walk(OUT):
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(dp, f)
            html = open(p, encoding='utf-8').read()
            changed = False
            # bloc contact sous le formulaire des accueils (index.html à la racine et /en/)
            rel = os.path.relpath(p, OUT).replace('\\', '/')
            if rel in ('index.html', 'en/index.html') and '<!-- wa-contact -->' not in html and '</form>' in html:
                lang = 'EN' if rel.startswith('en/') else 'FR'
                html = html.replace('</form>', '</form>\n' + wa_contact_block(lang), 1)
                changed = True; n_ct += 1
            # pastille flottante sur toutes les pages
            if '<!-- wa-fab -->' not in html:
                html = _inject_before(html, '</body>', WA_FAB)
                changed = True; n_fab += 1
            if changed:
                open(p, 'w', encoding='utf-8').write(html)
    print('  WhatsApp : %d pastilles, %d blocs contact' % (n_fab, n_ct))

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
            'CTA': ('<div class="fhero-cta"><a href="#book" class="cta-resa">Réserver — voir les disponibilités</a></div>'
                    if int(d.get('beds24_propid', 0)) in ACTIVE
                    else '<div class="fhero-cta"><a href="#book" class="cta-resa cta-soft">Réservation — nous contacter</a></div>'),
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
    # 5. WhatsApp : pastille sur toutes les pages + bloc contact sous les formulaires
    inject_whatsapp()
    return done

if __name__ == '__main__':
    for s in build():
        print('  %-12s %2d photos | %2d équip | résa=%s' % (s[0], s[1], s[2], 'widget' if s[3] else 'contact'))
