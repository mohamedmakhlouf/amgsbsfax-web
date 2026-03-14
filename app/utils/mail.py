# ============================================================
# app/utils/mail.py
# Utilitaire envoi d'emails — AMGSBS Sfax
# ============================================================
from flask import render_template, current_app
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()


def _send_async(app, msg):
    """Envoi en arrière-plan pour ne pas bloquer la requête."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"ERREUR EMAIL : {e}")
            app.logger.error(f"Erreur envoi email : {e}")


def send_email(subject, recipients, html_body, text_body=None):
    """Envoie un email HTML en arrière-plan."""
    app = current_app._get_current_object()
    msg = Message(
        subject    = subject,
        sender     = app.config.get('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME')),
        recipients = recipients,
    )
    msg.html = html_body
    if text_body:
        msg.body = text_body
    Thread(target=_send_async, args=(app, msg)).start()


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
            subject    = f"Confirmation d'inscription - AMGSBS Sfax (Ref. #{registration.id:05d})",
            recipients = [registration.email],
            html_body  = html,
            text_body  = (
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
    Envoye depuis l'admin quand l'admin confirme manuellement une inscription.
    """
    try:
        html = render_template(
            'emails/confirmation_inscription.html',
            registration=registration
        )
        send_email(
            subject    = f"Votre inscription est confirmee - AMGSBS Sfax (Ref. #{registration.id:05d})",
            recipients = [registration.email],
            html_body  = html,
            text_body  = (
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
