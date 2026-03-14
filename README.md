# amgsbsfax-web
## Site Officiel — Association Médicale des Gynécologues et Sages-Femmes de Sfax (AMGSBS Tunisie)

**Stack technique :** Python Flask · PostgreSQL (Neon) · Cloudinary · GitHub · Render

---

## 📁 Structure du Projet

```
amgsbsfax-web/
│
├── app/
│   ├── __init__.py          # Factory Flask + extensions
│   ├── models.py            # Modèles SQLAlchemy (toutes les tables)
│   ├── routes/
│   │   ├── main.py          # Page Accueil
│   │   ├── events.py        # Séminaires & Congrès
│   │   ├── register.py      # Inscription + Réservation hôtel
│   │   ├── abstracts.py     # Résumés & Exposés PPTX
│   │   ├── contact.py       # Formulaire Contact
│   │   └── admin.py         # Tableau de bord Admin (protégé)
│   ├── templates/           # Fichiers HTML Jinja2
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── events/
│   │   ├── register/
│   │   ├── abstracts/
│   │   ├── contact/
│   │   └── admin/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── utils/
│       └── cloudinary_helper.py
│
├── config.py                # Configuration (dev / prod)
├── run.py                   # Démarrage local
├── wsgi.py                  # Point d'entrée Render (gunicorn)
├── seed.py                  # Initialisation DB + admin
├── render.yaml              # Config déploiement Render
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🗄️ Tables de Base de Données

| Table               | Description                                      |
|---------------------|--------------------------------------------------|
| `users`             | Comptes administrateurs (login)                  |
| `members`           | Membres du bureau (photo, rôle FR/AR)            |
| `events`            | Congrès, séminaires, formations                  |
| `registrations`     | Inscriptions avec hébergement & transport        |
| `abstracts`         | Résumés + fichiers PPTX/PDF (Cloudinary)         |
| `event_photos`      | Galerie photos par événement (Cloudinary)        |
| `news`              | Actualités bilingues                             |
| `contact_messages`  | Messages du formulaire contact                   |

---

## ⚙️ Installation Locale

### 1. Cloner le projet
```bash
git clone https://github.com/VOTRE_USERNAME/amgsbsfax-web.git
cd amgsbsfax-web
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditez .env avec vos vraies valeurs
```

### 5. Initialiser la base de données
```bash
python seed.py
```

### 6. Lancer le serveur
```bash
python run.py
# → http://localhost:5000
# → Admin : http://localhost:5000/admin/login
```

---

## 🗃️ Configuration Neon (PostgreSQL)

1. Créer un compte sur [neon.tech](https://neon.tech)
2. Créer un projet `amgsbsfax`
3. Copier la **Connection string** dans `.env` → `DATABASE_URL`

---

## 🖼️ Configuration Cloudinary

1. Créer un compte sur [cloudinary.com](https://cloudinary.com)
2. Récupérer `Cloud name`, `API Key`, `API Secret`
3. Ajouter dans `.env`

---

## 🚀 Déploiement sur Render

1. Pousser le code sur GitHub
2. Créer un nouveau **Web Service** sur [render.com](https://render.com)
3. Connecter le dépôt GitHub `amgsbsfax-web`
4. Ajouter les variables d'environnement dans le Dashboard Render
5. Render déploiera automatiquement à chaque `git push`

---

## 🌐 Bilingue FR / AR

Le site supporte le Français et l'Arabe avec direction RTL automatique.
- Changer de langue : `/lang/fr` ou `/lang/ar`
- Toutes les tables ont des champs `_fr` et `_ar`

---

## 🔐 Accès Admin

- URL : `/admin/login`
- Email : défini dans `ADMIN_EMAIL` (`.env`)
- Mot de passe : défini dans `ADMIN_PASSWORD` (`.env`)

**Fonctionnalités Admin :**
- Tableau de bord avec statistiques
- Gestion des membres du bureau (+ photos)
- Gestion des événements (congrès, séminaires)
- Suivi des inscriptions (confirmation/annulation)
- Gestion des résumés et fichiers PPTX
- Publication des actualités
- Lecture des messages de contact
