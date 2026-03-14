# app/routes/main.py
from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import date
from app.models import Member, News, Event, EventPhoto

main_bp = Blueprint('main', __name__)


@main_bp.route('/lang/<lang>')
def set_language(lang):
    """Changement de langue FR/AR"""
    session['lang'] = lang if lang in ('fr', 'ar') else 'fr'
    # Retourner à la page précédente
    return redirect(request.referrer or url_for('main.index'))


@main_bp.route('/')
def index():
    # ── Membres du bureau
    members = Member.query.filter_by(is_active=True).order_by(Member.order).all()

    # ── Actualités
    news = News.query.filter_by(is_published=True)\
                     .order_by(News.published_at.desc())\
                     .limit(8).all()

    # ── Événements à venir
    upcoming_events = Event.query.filter(
        Event.is_published == True,
        Event.date_start >= date.today()
    ).order_by(Event.date_start).limit(3).all()

    # ── Prochain événement (pour le hero)
    next_event = Event.query.filter(
        Event.is_published == True,
        Event.date_start >= date.today()
    ).order_by(Event.date_start).first()

    # ── Statistiques
    membres_count    = Member.query.filter_by(is_active=True).count()
    events_count     = Event.query.filter_by(is_published=True).count()
    seminaires_count = Event.query.filter_by(is_published=True, event_type='seminaire').count()
    congres_count    = Event.query.filter_by(is_published=True, event_type='congres').count()
    years_count      = 15

    # ── Photos galerie
    gallery_photos = EventPhoto.query\
                               .order_by(EventPhoto.uploaded_at.desc())\
                               .limit(8).all()

    return render_template('main/index.html',
        members          = members,
        news             = news,
        upcoming_events  = upcoming_events,
        next_event       = next_event,
        membres_count    = membres_count,
        events_count     = events_count,
        seminaires_count = seminaires_count,
        congres_count    = congres_count,
        years_count      = years_count,
        gallery_photos   = gallery_photos,
    )