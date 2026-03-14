# app/routes/register.py 28-02-2026
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Registration, Event, db
from datetime import datetime, date

register_bp = Blueprint('register', __name__)

@register_bp.route('/', methods=['GET', 'POST'])
def index():
    from datetime import date

    events = Event.query.filter(
        Event.is_published == True,
        Event.date_start >= date.today()
    ).order_by(Event.date_start).all()

    if request.method == 'POST':

        # ── Récupération event_id avec validation
        event_id_raw = request.form.get('event_id')

        if not event_id_raw:
            flash('Veuillez sélectionner un événement.', 'error')
            return render_template('register/index.html', events=events)

        try:
            event_id = int(event_id_raw)
        except (ValueError, TypeError):
            flash('Événement invalide.', 'error')
            return render_template('register/index.html', events=events)

        # Vérifier que l'événement existe bien
        event = Event.query.get(event_id)
        if not event:
            flash('Événement introuvable.', 'error')
            return render_template('register/index.html', events=events)

        # ── Récupération des autres champs
        try:
            birth_date_raw = request.form.get('birth_date')
            birth_date = datetime.strptime(birth_date_raw, '%Y-%m-%d').date() if birth_date_raw else None

            nights_count   = int(request.form.get('nights_count', 1) or 1)
            children_count = int(request.form.get('children_count', 0) or 0)

            reg = Registration(
                event_id         = event_id,
                sigle            = request.form.get('sigle'),
                first_name       = request.form.get('first_name', '').strip(),
                last_name        = request.form.get('last_name', '').strip(),
                birth_date       = birth_date,
                gender           = request.form.get('gender'),
                specialty        = request.form.get('specialty'),
                institution      = request.form.get('institution'),
                email            = request.form.get('email', '').strip(),
                phone            = request.form.get('phone'),
                hotel_requested  = request.form.get('hotel_requested') == '1',
                room_type        = request.form.get('room_type') or None,
                nights_count     = nights_count,
                with_spouse      = request.form.get('with_spouse') == '1',
                children_count   = children_count,
                transport_needed = request.form.get('transport_needed') == '1',
                payment_method   = request.form.get('payment_method'),
                special_requests = request.form.get('special_requests', ''),
            )

            db.session.add(reg)
            db.session.commit()

            flash('Votre inscription a été enregistrée avec succès !', 'success')
            return redirect(url_for('register.confirmation', reg_id=reg.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'inscription : {str(e)}', 'error')
            return render_template('register/index.html', events=events)

    return render_template('register/index.html', events=events)
@register_bp.route('/confirmation/<int:reg_id>')
def confirmation(reg_id):
    registration = Registration.query.get_or_404(reg_id)
    return render_template('register/confirmation.html', registration=registration)