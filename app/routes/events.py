# app/routes/events.py
from flask import Blueprint, render_template
from app.models import Event
from datetime import date

events_bp = Blueprint('events', __name__)

@events_bp.route('/')
def index():
    seminars = Event.query.filter_by(is_published=True, event_type='seminaire').order_by(Event.date_start).all()
    congres  = Event.query.filter_by(is_published=True, event_type='congres').order_by(Event.date_start).all()
    return render_template('events/index.html', seminars=seminars, congres=congres)

@events_bp.route('/<int:event_id>')
def detail(event_id):
    event  = Event.query.get_or_404(event_id)
    photos = event.photos.order_by('order').all()
    return render_template('events/detail.html', event=event, photos=photos)
