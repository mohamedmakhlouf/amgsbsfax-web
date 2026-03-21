# create_admin.py — À exécuter une seule fois puis supprimer
import os
from app import create_app, db
from app.models import User

app = create_app('production')
with app.app_context():
    # Vérifier si admin existe déjà
    if not User.query.filter_by(username='hamadimakhlouf@yahoo.fr').first():
        u = User(username='hamadimakhlouf@yahoo.fr')
        u.set_password('Amgsbs@SfaxMars2026')
        db.session.add(u)
        db.session.commit()
        print('Admin créé !')
    else:
        print('Admin existe déjà.')
