#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injecte WhatsApp sur le site :
   - pastille flottante (FAB) sur TOUTES les pages
   - bloc contact direct (WA + tel) sous le formulaire des 2 accueils (FR/EN)
Idempotent : relançable sans créer de doublons.
À poser à la racine du repo et exécuter : python3 add_whatsapp.py
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

WA_INTL    = "33669325385"      # numéro international sans le +
WA_DISPLAY = "06 69 32 53 85"   # affichage FR
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

# ---- pastille flottante (self-contained : porte son propre CSS) --------------
FAB = f'''<!-- wa-fab -->
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

# ---- bloc contact direct sous le formulaire ---------------------------------
CONTACT_CSS = '''<!-- wa-contact -->
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

def contact_block(lang):
    wa_label  = f"WhatsApp · {WA_DISPLAY}"
    tel_label = ("Appeler · " if lang == "FR" else "Call · ") + WA_DISPLAY
    intro     = "Ou contactez-nous directement" if lang == "FR" else "Or reach us directly"
    return (CONTACT_CSS +
            f'<div class="wa-contact"><span class="wa-or">{intro}</span><div class="wa-links">'
            f'<a class="wa-line" href="{WA_LINK}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24"><path d="{WA_GLYPH}"/></svg>{wa_label}</a>'
            f'<a class="tel-line" href="{TEL_LINK}">'
            f'<svg viewBox="0 0 24 24"><path d="{PHONE_GLYPH}"/></svg>{tel_label}</a>'
            f'</div></div>\n')

def inject_before_close(html, snippet):
    """Insère snippet avant </body> (sinon </html>, sinon en fin)."""
    for tag in ('</body>', '</html>'):
        i = html.lower().rfind(tag)
        if i != -1:
            return html[:i] + snippet + html[i:]
    return html + snippet

def add_fab(path):
    html = open(path, encoding='utf-8').read()
    if '<!-- wa-fab -->' in html:
        return False
    html = inject_before_close(html, FAB)
    open(path, 'w', encoding='utf-8').write(html)
    return True

def add_contact(path, lang):
    html = open(path, encoding='utf-8').read()
    if '<!-- wa-contact -->' in html or '</form>' not in html:
        return False
    # insère le bloc juste après le </form> du formulaire de contact
    html = html.replace('</form>', '</form>\n' + contact_block(lang), 1)
    open(path, 'w', encoding='utf-8').write(html)
    return True

def main():
    n_fab = n_ct = 0
    # 1. pastille dans le template (=> toutes les fiches FR générées)
    tpl = os.path.join(ROOT, 'template.html')
    if os.path.isfile(tpl) and add_fab(tpl):
        n_fab += 1; print('  FAB   template.html')
    # 2. pastille sur toutes les pages figées de static/
    static = os.path.join(ROOT, 'static')
    for dp, _, files in os.walk(static):
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(dp, f)
                if add_fab(p):
                    n_fab += 1; print('  FAB   ' + os.path.relpath(p, ROOT))
    # 3. bloc contact sous le formulaire des 2 accueils
    for rel, lang in (('static/index.html', 'FR'), ('static/en/index.html', 'EN')):
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p) and add_contact(p, lang):
            n_ct += 1; print('  CONT  ' + rel + f'  [{lang}]')
    print(f'\nOK — {n_fab} pastilles injectees, {n_ct} blocs contact.')

if __name__ == '__main__':
    main()
