"""
amgsbsfax-web — Modèles de base de données (PostgreSQL / Neon)
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


# ═══════════════════════════════════════════════════════════
#  UTILISATEUR ADMIN
# ═══════════════════════════════════════════════════════════
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    username      = db.Column(db.String(64),  unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ═══════════════════════════════════════════════════════════
#  MEMBRES DU BUREAU
# ═══════════════════════════════════════════════════════════
class Member(db.Model):
    __tablename__ = 'members'

    id           = db.Column(db.Integer, primary_key=True)
    # Bilingue
    name_fr      = db.Column(db.String(120), nullable=False)
    name_ar      = db.Column(db.String(120))
    role_fr      = db.Column(db.String(120), nullable=False)  # ex: Président
    role_ar      = db.Column(db.String(120))                  # ex: الرئيس
    bio_fr       = db.Column(db.Text)
    bio_ar       = db.Column(db.Text)
    # Photo (URL Cloudinary)
    photo_url    = db.Column(db.String(500))
    photo_public_id = db.Column(db.String(200))   # ID Cloudinary pour suppression
    # Ordre d'affichage
    order        = db.Column(db.Integer, default=0)
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Member {self.name_fr}>'


# ═══════════════════════════════════════════════════════════
#  ÉVÉNEMENTS (Congrès / Séminaires / Formations)
# ═══════════════════════════════════════════════════════════
class Event(db.Model):
    __tablename__ = 'events'

    id              = db.Column(db.Integer, primary_key=True)
    event_type      = db.Column(db.String(30), nullable=False)  # 'congres' | 'seminaire' | 'formation'
    # Contenu bilingue
    title_fr        = db.Column(db.String(250), nullable=False)
    title_ar        = db.Column(db.String(250))
    description_fr  = db.Column(db.Text)
    description_ar  = db.Column(db.Text)
    program_fr      = db.Column(db.Text)   # Programme détaillé
    program_ar      = db.Column(db.Text)
    # Dates
    date_start      = db.Column(db.Date, nullable=False)
    date_end        = db.Column(db.Date)
    # Lieu
    city            = db.Column(db.String(100))
    address         = db.Column(db.String(250))
    # Hôtel
    hotel_name      = db.Column(db.String(150))
    hotel_address   = db.Column(db.String(250))
    hotel_stars     = db.Column(db.Integer)
    hotel_nights    = db.Column(db.Integer)       # Nombre de nuitées
    hotel_price_night = db.Column(db.Float)       # Prix par nuit en DT
    hotel_map_url   = db.Column(db.String(500))   # Lien Google Maps
    # Transport
    transport_available = db.Column(db.Boolean, default=False)
    transport_details_fr = db.Column(db.Text)
    transport_details_ar = db.Column(db.Text)
    # Image (Cloudinary)
    image_url       = db.Column(db.String(500))
    image_public_id = db.Column(db.String(200))
    # Statut
    is_published    = db.Column(db.Boolean, default=False)
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    registrations   = db.relationship('Registration', backref='event', lazy='dynamic')
    abstracts       = db.relationship('Abstract', backref='event', lazy='dynamic')
    photos          = db.relationship('EventPhoto', backref='event', lazy='dynamic')

    def __repr__(self):
        return f'<Event {self.title_fr}>'


# ═══════════════════════════════════════════════════════════
#  INSCRIPTIONS
# ═══════════════════════════════════════════════════════════
class Registration(db.Model):
    __tablename__ = 'registrations'

    id              = db.Column(db.Integer, primary_key=True)
    event_id        = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    # Identité
    sigle           = db.Column(db.String(20))    # Dr. / Pr. / SF / Mr. / Mme
    first_name      = db.Column(db.String(100), nullable=False)
    last_name       = db.Column(db.String(100), nullable=False)
    birth_date      = db.Column(db.Date)
    gender          = db.Column(db.String(10))    # 'M' | 'F'
    specialty       = db.Column(db.String(150))
    institution     = db.Column(db.String(200))
    # Contact
    email           = db.Column(db.String(120), nullable=False)
    phone           = db.Column(db.String(30))
    # Hébergement
    hotel_requested = db.Column(db.Boolean, default=False)
    room_type       = db.Column(db.String(20))    # 'single' | 'double'
    nights_count    = db.Column(db.Integer, default=1)
    # Accompagnateurs
    with_spouse     = db.Column(db.Boolean, default=False)
    children_count  = db.Column(db.Integer, default=0)
    # Transport
    transport_needed = db.Column(db.Boolean, default=False)
    # Paiement
    payment_method  = db.Column(db.String(50))   # 'virement' | 'cheque' | 'especes' | 'enligne'
    payment_status  = db.Column(db.String(20), default='pending')  # 'pending' | 'paid' | 'cancelled'
    # Notes
    special_requests = db.Column(db.Text)
    # Statut
    status          = db.Column(db.String(20), default='submitted')  # 'submitted' | 'confirmed' | 'cancelled'
    registered_at   = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at    = db.Column(db.DateTime)

    @property
    def full_name(self):
        return f"{self.sigle} {self.first_name} {self.last_name}".strip()

    def __repr__(self):
        return f'<Registration {self.full_name} – Event {self.event_id}>'


# ═══════════════════════════════════════════════════════════
#  RÉSUMÉS / ABSTRACTS
# ═══════════════════════════════════════════════════════════
class Abstract(db.Model):
    __tablename__ = 'abstracts'

    id              = db.Column(db.Integer, primary_key=True)
    event_id        = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    # Auteurs
    author_name     = db.Column(db.String(200), nullable=False)
    author_institution = db.Column(db.String(200))
    # Contenu bilingue
    title_fr        = db.Column(db.String(300), nullable=False)
    title_ar        = db.Column(db.String(300))
    content_fr      = db.Column(db.Text, nullable=False)   # Résumé en français
    content_ar      = db.Column(db.Text)                    # Résumé en arabe
    # Type
    presentation_type = db.Column(db.String(30))  # 'oral' | 'poster' | 'keynote'
    # Récompense
    award           = db.Column(db.String(50))     # '1er_prix' | '2eme_prix' | '3eme_prix' | null
    is_featured     = db.Column(db.Boolean, default=False)  # Meilleur travail → affiché
    # Fichiers (Cloudinary)
    pptx_url        = db.Column(db.String(500))
    pptx_public_id  = db.Column(db.String(200))
    pdf_url         = db.Column(db.String(500))
    pdf_public_id   = db.Column(db.String(200))
    # Statut
    is_published    = db.Column(db.Boolean, default=False)
    submitted_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Abstract {self.title_fr[:50]}>'


# ═══════════════════════════════════════════════════════════
#  PHOTOS D'ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════
class EventPhoto(db.Model):
    __tablename__ = 'event_photos'

    id          = db.Column(db.Integer, primary_key=True)
    event_id    = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    url         = db.Column(db.String(500), nullable=False)
    public_id   = db.Column(db.String(200))     # ID Cloudinary
    caption_fr  = db.Column(db.String(300))
    caption_ar  = db.Column(db.String(300))
    is_cover    = db.Column(db.Boolean, default=False)   # Photo principale
    order       = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EventPhoto event={self.event_id}>'


# ═══════════════════════════════════════════════════════════
#  ACTUALITÉS / NEWS
# ═══════════════════════════════════════════════════════════
class News(db.Model):
    __tablename__ = 'news'

    id              = db.Column(db.Integer, primary_key=True)
    title_fr        = db.Column(db.String(250), nullable=False)
    title_ar        = db.Column(db.String(250))
    content_fr      = db.Column(db.Text, nullable=False)
    content_ar      = db.Column(db.Text)
    category        = db.Column(db.String(50))   # 'congres' | 'formation' | 'prix' | 'general'
    image_url       = db.Column(db.String(500))
    image_public_id = db.Column(db.String(200))
    is_published    = db.Column(db.Boolean, default=False)
    published_at    = db.Column(db.DateTime)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<News {self.title_fr[:50]}>'


# ═══════════════════════════════════════════════════════════
#  MESSAGES DE CONTACT
# ═══════════════════════════════════════════════════════════
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    email       = db.Column(db.String(120), nullable=False)
    subject     = db.Column(db.String(200))
    message     = db.Column(db.Text, nullable=False)
    is_read     = db.Column(db.Boolean, default=False)
    sent_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage from {self.email}>'

# ═══════════════════════════════════════════════════════════
#  GALERIE PHOTOS
# ═══════════════════════════════════════════════════════════
class GalleryPhoto(db.Model):
    __tablename__ = 'gallery_photos'

    id          = db.Column(db.Integer, primary_key=True)
    url         = db.Column(db.String(500), nullable=False)
    public_id   = db.Column(db.String(200))
    caption_fr  = db.Column(db.String(300))
    caption_ar  = db.Column(db.String(300))
    is_featured = db.Column(db.Boolean, default=False)
    order       = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<GalleryPhoto {self.caption_fr or self.id}>'