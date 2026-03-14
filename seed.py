"""
seed.py — Crée toutes les tables dans PostgreSQL (Neon) + compte admin
Exécuter UNE SEULE FOIS : python seed.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():

    print("⏳ Connexion à la base de données...")
    print(f"   URL : {os.environ.get('DATABASE_URL','non définie')[:50]}...")

    # Créer toutes les tables
    db.create_all()
    print("✅ Toutes les tables créées avec succès !")

    # Créer le compte admin si absent
    admin_email = os.environ.get('ADMIN_EMAIL', 'hamadimakhlouf@yahoo.fr')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin1234!')

    existing = User.query.filter_by(email=admin_email).first()
    if not existing:
        admin = User(
            email    = admin_email,
            username = 'admin',
            is_admin = True,
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Compte admin créé : {admin_email}")
        print(f"   Mot de passe     : {admin_password}")
    else:
        print(f"ℹ️  Compte admin déjà existant : {admin_email}")

    print("")
    print("🎉 Base de données initialisée avec succès !")
    print("   Vous pouvez maintenant lancer : python run.py")