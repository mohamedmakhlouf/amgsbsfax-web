# app/routes/contact.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import ContactMessage, db

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        # Le formulaire a deux champs séparés : first_name + last_name
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name', '').strip()
        name       = f"{first_name} {last_name}".strip() or 'Anonyme'

        email   = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        # Validation
        if not name or name == 'Anonyme':
            flash('Veuillez saisir votre nom.', 'error')
            return render_template('contact/index.html')
        if not email:
            flash('Veuillez saisir votre email.', 'error')
            return render_template('contact/index.html')
        if not message:
            flash('Veuillez saisir votre message.', 'error')
            return render_template('contact/index.html')

        try:
            msg = ContactMessage(
                name    = name,
                email   = email,
                subject = subject or 'Sans objet',
                message = message,
            )
            db.session.add(msg)
            db.session.commit()
            flash('Votre message a été envoyé. Nous vous répondrons dans les plus brefs délais.', 'success')
            return redirect(url_for('contact.index'))

        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de l'envoi. Veuillez réessayer.", 'error')

    return render_template('contact/index.html')
