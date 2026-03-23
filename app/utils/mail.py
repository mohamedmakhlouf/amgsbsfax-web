# ============================================================
# app/utils/mail.py
# Utilitaire envoi d'emails via API Brevo — AMGSBS Sfax
# ============================================================
import os
import requests
from threading import Thread
from flask import render_template, current_app

# Objet factice pour compatibilité avec __init__.py
class _FakeMail:
    def init_app(self, app):
        pass

mail = _FakeMail()

BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'


def _send_via_brevo(api_key, sender_email, sender_name, recipients, subject, html_body, text_body=None):
    """Envoi via l'API HTTP Brevo."""
    payload = {
        'sender': {'name': sender_name, 'email': sender_email},
        'to': [{'email': r} for r in recipients],
        'subject': subject,
        'htmlContent': html_body,
    }
    if text_body:
        payload['textContent'] = text_body

    try:
        response = requests.post(
            BREVO_API_URL,
            headers={
                'api-key': api_key,
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=15
        )
        if response.status_code in (200, 201):
            print(f"Email envoyé avec succès à {recipients}")
            return True
        else:
            print(f"Erreur Brevo API {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Erreur envoi email : {e}")
        return False


def _send_async(app, api_key, sender_email, sender_name, recipients, subject, html_body, text_body=None):
    """Envoi en arrière-plan pour ne pas bloquer la requête."""
    with app.app_context():
        _send_via_brevo(api_key, sender_email, sender_name, recipients, subject, html_body, text_body)


def send_email(subject, recipients, html_body, text_body=None):
    """Envoie un email HTML en arrière-plan via Brevo API."""
    app = current_app._get_current_object()
    api_key = os.environ.get('BREVO_API_KEY') or app.config.get('BREVO_API_KEY')
    sender_email = app.config.get('MAIL_DEFAULT_SENDER', 'amgsbsfax@gmail.com')
    sender_name = 'AMGSBS Sfax'

    if not api_key:
        app.logger.error("BREVO_API_KEY non configurée !")
        return False

    Thread(
        target=_send_async,
        args=(app, api_key, sender_email, sender_name, recipients, subject, html_body, text_body)
    ).start()
    return True


def send_confirmation_inscription(registration):
    """
    Envoie l'email de confirmation à l'inscrit.
    Appelé juste après db.session.commit() dans register.py
    """
    try:
        html = render_template(
            'emails/confirmation_inscription.html',
            registration=registration
        )
        send_email(
            subject   = f"Confirmation d'inscription - AMGSBS Sfax (Ref. #{registration.id:05d})",
            recipients= [registration.email],
            html_body = html,
            text_body = (
                f"Bonjour {registration.first_name} {registration.last_name},\n\n"
                f"Votre inscription a bien ete enregistree.\n"
                f"Reference : #{registration.id:05d}\n\n"
                f"Pour toute question : amgsbsfax@gmail.com\n\n"
                f"Cordialement,\nAMGSBS Sfax"
            )
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur send_confirmation_inscription : {e}")
        return False


def send_confirmation_email_admin(registration):
    """
    Envoyé depuis l'admin quand l'admin confirme manuellement une inscription.
    """
    try:
        html = render_template(
            'emails/confirmation_inscription.html',
            registration=registration
        )
        send_email(
            subject   = f"Votre inscription est confirmee - AMGSBS Sfax (Ref. #{registration.id:05d})",
            recipients= [registration.email],
            html_body = html,
            text_body = (
                f"Bonjour Dr. {registration.first_name} {registration.last_name},\n\n"
                f"Nous avons le plaisir de vous informer que votre inscription a ete confirmee.\n"
                f"Reference : #{registration.id:05d}\n"
                f"Evenement : {registration.event.title_fr if registration.event else ''}\n\n"
                f"Pour toute question : amgsbsfax@gmail.com\n\n"
                f"Cordialement,\nAMGSBS Sfax"
            )
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur send_confirmation_email_admin : {e}")
        return False