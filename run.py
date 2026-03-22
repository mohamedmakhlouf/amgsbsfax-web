# run.py — Démarrage amgsbsfax-web
import os
from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'production'))

with app.app_context():
    try:
        from app import db
        from app.models import User
        db.create_all()
        if not User.query.filter_by(email='hamadimakhlouf@yahoo.fr').first():
            u = User(username='admin', email='hamadimakhlouf@yahoo.fr')
            u.set_password(os.environ.get('ADMIN_PASSWORD', 'Amgsbs@SfaxMars2026'))
            db.session.add(u)
            db.session.commit()
            print('Admin créé sur Supabase !')
    except Exception as e:
        print(f'Erreur : {e}')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5003)))
