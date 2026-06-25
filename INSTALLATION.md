# Installation de l'outil d'administration — Domaine des Prépresses

Ce guide t'amène de zéro à un site où **tes cousins gèrent eux-mêmes photos et textes**.
À faire **une seule fois**. Compte ~30 minutes. Suis les étapes dans l'ordre.

---

## Vue d'ensemble (pour comprendre où on va)

```
   Tes cousins                  GitHub                    Netlify
  (page /admin)  ──éditent──▶  (stocke le contenu) ──▶  (reconstruit + publie)
                                                         = le site en ligne
```

Tes cousins ne verront JAMAIS GitHub. Ils vont juste sur `domainedesprepresses.fr/admin`,
se connectent avec un email + mot de passe, et modifient. Le reste est automatique.

---

## ÉTAPE 1 — Créer un compte GitHub (5 min)

1. Va sur **github.com** → **Sign up**.
2. Crée ton compte (email, mot de passe, nom d'utilisateur). C'est gratuit.
3. Valide ton email.

---

## ÉTAPE 2 — Créer le dépôt et y déposer les fichiers (10 min)

1. Une fois connecté, clique le **+** en haut à droite → **New repository**.
2. **Repository name** : `domaine-prepresses`
3. Laisse **Public** (ou Private, peu importe), **ne coche rien d'autre**, clique **Create repository**.
4. Sur la page qui s'affiche, clique le lien **« uploading an existing file »**
   (ou : bouton **Add file → Upload files**).
5. **Glisse-dépose TOUT le contenu** du dossier que je t'ai fourni (le dossier `cms/`) :
   - les dossiers `content/`, `admin/`, `static/`
   - les fichiers `build.py`, `template.html`, `netlify.toml`, `icon_library.json`,
     `booking_widget.html`, `booking_contact.html`, `spec_icons.json`
   > 💡 Glisse les dossiers ET les fichiers d'un coup. GitHub conserve l'arborescence.
6. En bas, clique **Commit changes**.

✅ Ton contenu est maintenant sur GitHub.

---

## ÉTAPE 3 — Connecter Netlify au dépôt (5 min)

> On remplace ton déploiement « glisser-déposer » par un déploiement connecté à GitHub.

1. Sur **Netlify**, va dans ton équipe → **Add new site** → **Import an existing project**.
2. Choisis **GitHub** → autorise Netlify à accéder à ton GitHub.
3. Sélectionne le dépôt **`domaine-prepresses`**.
4. Netlify lit automatiquement le fichier `netlify.toml` → les réglages se remplissent seuls :
   - **Build command** : `pip install pyyaml --quiet && python3 build.py`
   - **Publish directory** : `build`
5. Clique **Deploy**. Attends 1-2 min : Netlify construit le site.

✅ Le site se reconstruit désormais tout seul à chaque modification.

> ⚠️ **Ton domaine** `domainedesprepresses.fr` est rattaché à ton ANCIEN site Netlify.
> Quand ce nouveau site marche, tu déplaceras le domaine dessus
> (Site settings → Domain management → Add domain). Je te guiderai le moment venu.

---

## ÉTAPE 4 — Activer la connexion des éditeurs (5 min)

> C'est ce qui permet à tes cousins de se connecter à `/admin` avec un simple email.

1. Sur le site Netlify, va dans **Site configuration** (ou **Settings**) → **Identity**.
2. Clique **Enable Identity**.
3. Dans **Identity → Registration**, mets **« Invite only »**
   (seules les personnes que tu invites pourront entrer).
4. Toujours dans **Identity**, descends à **Services → Git Gateway** → clique **Enable Git Gateway**.
   *(C'est lui qui permet à l'admin d'enregistrer les modifs dans GitHub automatiquement.)*

---

## ÉTAPE 5 — Inviter tes cousins (2 min)

1. **Identity → Invite users** → entre les emails de Martin et Clément → **Send**.
2. Ils reçoivent un email → ils cliquent le lien → choisissent un mot de passe.
3. C'est fait : ils peuvent aller sur **domainedesprepresses.fr/admin** et se connecter.

> 🔑 Invite-toi toi-même aussi pour tester.

---

## C'est fini ! Comment ça marche au quotidien

**Tes cousins** vont sur `/admin`, se connectent, cliquent un logement, modifient
(photos en glisser-déposer, textes, équipements + icônes), cliquent **Enregistrer**.
→ Netlify reconstruit le site en ~2 min. **Tu n'as plus rien à faire.**

**Toi**, tu n'interviens que si tu veux changer le design ou ajouter une page.

---

## En cas de souci

- **L'admin affiche une erreur de connexion** : vérifie que **Git Gateway** est bien activé (Étape 4.4).
- **Une modif n'apparaît pas** : va dans Netlify → onglet **Deploys**, regarde si le build a réussi (vert).
  S'il est rouge, clique dessus pour voir l'erreur et envoie-la moi.
- **Besoin d'aide** : reviens vers moi avec une capture, on débogue ensemble.
