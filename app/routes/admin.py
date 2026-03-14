# app/routes/admin.py 03 mars 2026
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Member, Event, Registration, Abstract, News, ContactMessage, GalleryPhoto, db
from app.utils.cloudinary_helper import upload_file, delete_file
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# ── HELPERS ───────────────────────────────────────────────
def _upload(file_obj, folder):
    """Upload vers Cloudinary et retourne (url, public_id)."""
    if file_obj and file_obj.filename:
        try:
            result = upload_file(file_obj, folder=folder)
            return result.get('secure_url',''), result.get('public_id','')
        except Exception as e:
            flash(f"Erreur upload : {e}", 'error')
    return None, None

# ── AUTH ──────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Email ou mot de passe incorrect.', 'error')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

# ── DASHBOARD ─────────────────────────────────────────────
@admin_bp.route('/')
@login_required
def dashboard():
    from app.models import EventPhoto
    stats = {
        'members':       Member.query.count(),
        'events':        Event.query.count(),
        'registrations': Registration.query.count(),
        'abstracts':     Abstract.query.count(),
        'news':          News.query.count(),
        'messages':      ContactMessage.query.filter_by(is_read=False).count(),
    }
    recent_regs  = Registration.query.order_by(Registration.registered_at.desc()).limit(10).all()
    recent_msgs  = ContactMessage.query.order_by(ContactMessage.sent_at.desc()).limit(8).all()
    return render_template('admin/dashboard.html',
        stats=stats, recent_regs=recent_regs, recent_msgs=recent_msgs,
        now=datetime.utcnow())

# ── MEMBRES ───────────────────────────────────────────────
@admin_bp.route('/membres')
@login_required
def members():
    members = Member.query.order_by(Member.order).all()
    return render_template('admin/members.html', members=members)

@admin_bp.route('/membres/ajouter', methods=['GET', 'POST'])
@login_required
def member_add():
    if request.method == 'POST':
        url, pid = _upload(request.files.get('photo'), 'amgsbsfax/members')
        m = Member(
            name_fr   = request.form.get('name_fr'),
            name_ar   = request.form.get('name_ar'),
            role_fr   = request.form.get('role_fr'),
            role_ar   = request.form.get('role_ar'),
            bio_fr    = request.form.get('bio_fr'),
            bio_ar    = request.form.get('bio_ar'),
            order     = int(request.form.get('order') or 1),
            is_active = request.form.get('is_active') == '1',
            photo_url       = url,
            photo_public_id = pid,
        )
        db.session.add(m)
        db.session.commit()
        flash('Membre ajouté avec succès !', 'success')
        return redirect(url_for('admin.members'))
    return render_template('admin/member_form.html', member=None)

@admin_bp.route('/membres/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def member_edit(id):
    m = Member.query.get_or_404(id)
    if request.method == 'POST':
        m.name_fr   = request.form.get('name_fr')
        m.name_ar   = request.form.get('name_ar')
        m.role_fr   = request.form.get('role_fr')
        m.role_ar   = request.form.get('role_ar')
        m.bio_fr    = request.form.get('bio_fr')
        m.bio_ar    = request.form.get('bio_ar')
        m.order     = int(request.form.get('order') or 1)
        m.is_active = request.form.get('is_active') == '1'
        photo = request.files.get('photo')
        if photo and photo.filename:
            if m.photo_public_id:
                delete_file(m.photo_public_id)
            url, pid = _upload(photo, 'amgsbsfax/members')
            m.photo_url, m.photo_public_id = url, pid
        db.session.commit()
        flash('Membre mis à jour !', 'success')
        return redirect(url_for('admin.members'))
    return render_template('admin/member_form.html', member=m)

@admin_bp.route('/membres/<int:id>/supprimer', methods=['POST'])
@login_required
def member_delete(id):
    m = Member.query.get_or_404(id)
    if m.photo_public_id:
        delete_file(m.photo_public_id)
    db.session.delete(m)
    db.session.commit()
    flash('Membre supprimé.', 'info')
    return redirect(url_for('admin.members'))

# ── ÉVÉNEMENTS ────────────────────────────────────────────
@admin_bp.route('/evenements')
@login_required
def events():
    events = Event.query.order_by(Event.date_start.desc()).all()
    return render_template('admin/events.html', events=events)

@admin_bp.route('/evenements/ajouter', methods=['GET', 'POST'])
@login_required
def event_add():
    if request.method == 'POST':
        url, pid = _upload(request.files.get('image'), 'amgsbsfax/events')
        def parse_date(s):
            return datetime.strptime(s, '%Y-%m-%d').date() if s else None
        ev = Event(
            title_fr            = request.form.get('title_fr'),
            title_ar            = request.form.get('title_ar'),
            description_fr      = request.form.get('description_fr'),
            description_ar      = request.form.get('description_ar'),
            program_fr          = request.form.get('program_fr'),
            event_type          = request.form.get('event_type', 'congres'),
            date_start          = parse_date(request.form.get('date_start')),
            date_end            = parse_date(request.form.get('date_end')),
            city                = request.form.get('city'),
            address             = request.form.get('address'),
            hotel_name          = request.form.get('hotel_name'),
            hotel_address       = request.form.get('hotel_address'),
            hotel_stars         = int(request.form.get('hotel_stars') or 0) or None,
            hotel_nights        = int(request.form.get('hotel_nights') or 0) or None,
            hotel_price_night   = float(request.form.get('hotel_price_night') or 0) or None,
            transport_available = request.form.get('transport_available') == '1',
            transport_details_fr= request.form.get('transport_details_fr'),
            is_published        = request.form.get('is_published') == '1',
            image_url           = url,
            image_public_id     = pid,
        )
        db.session.add(ev)
        db.session.commit()
        flash('Événement créé avec succès !', 'success')
        return redirect(url_for('admin.events'))
    return render_template('admin/event_form.html', event=None)

@admin_bp.route('/evenements/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def event_edit(id):
    ev = Event.query.get_or_404(id)
    if request.method == 'POST':
        def parse_date(s):
            return datetime.strptime(s, '%Y-%m-%d').date() if s else None
        ev.title_fr             = request.form.get('title_fr')
        ev.title_ar             = request.form.get('title_ar')
        ev.description_fr       = request.form.get('description_fr')
        ev.description_ar       = request.form.get('description_ar')
        ev.program_fr           = request.form.get('program_fr')
        ev.event_type           = request.form.get('event_type', 'congres')
        ev.date_start           = parse_date(request.form.get('date_start'))
        ev.date_end             = parse_date(request.form.get('date_end'))
        ev.city                 = request.form.get('city')
        ev.address              = request.form.get('address')
        ev.hotel_name           = request.form.get('hotel_name')
        ev.hotel_address        = request.form.get('hotel_address')
        ev.hotel_stars          = int(request.form.get('hotel_stars') or 0) or None
        ev.hotel_nights         = int(request.form.get('hotel_nights') or 0) or None
        ev.hotel_price_night    = float(request.form.get('hotel_price_night') or 0) or None
        ev.transport_available  = request.form.get('transport_available') == '1'
        ev.transport_details_fr = request.form.get('transport_details_fr')
        ev.is_published         = request.form.get('is_published') == '1'
        img = request.files.get('image')
        if img and img.filename:
            if ev.image_public_id:
                delete_file(ev.image_public_id)
            ev.image_url, ev.image_public_id = _upload(img, 'amgsbsfax/events')
        db.session.commit()
        flash('Événement mis à jour !', 'success')
        return redirect(url_for('admin.events'))
    return render_template('admin/event_form.html', event=ev)

@admin_bp.route('/evenements/<int:id>/supprimer', methods=['POST'])
@login_required
def event_delete(id):
    ev = Event.query.get_or_404(id)
    if ev.image_public_id:
        delete_file(ev.image_public_id)
    db.session.delete(ev)
    db.session.commit()
    flash('Événement supprimé.', 'info')
    return redirect(url_for('admin.events'))

# ── INSCRIPTIONS ──────────────────────────────────────────
@admin_bp.route('/inscriptions')
@login_required
def registrations():
    status = request.args.get('status')
    q = Registration.query.order_by(Registration.registered_at.desc())
    if status:
        q = q.filter_by(status=status)
    regs = q.all()
    return render_template('admin/registrations.html', regs=regs)

@admin_bp.route('/inscriptions/<int:id>/statut', methods=['POST'])
@login_required
def registration_status(id):
    r = Registration.query.get_or_404(id)
    r.status = request.form.get('status', r.status)
    if r.status == 'confirmed':
        r.confirmed_at = datetime.utcnow()
    db.session.commit()
    flash('Statut mis à jour.', 'success')
    return redirect(url_for('admin.registrations'))

@admin_bp.route('/inscriptions/<int:id>/supprimer', methods=['POST'])
@login_required
def registration_delete(id):
    r = Registration.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()
    flash('Inscription supprimée.', 'info')
    return redirect(url_for('admin.registrations'))

# ── RÉSUMÉS ───────────────────────────────────────────────
@admin_bp.route('/resumes')
@login_required
def abstracts():
    abstracts = Abstract.query.order_by(Abstract.submitted_at.desc()).all()
    return render_template('admin/abstracts.html', abstracts=abstracts)

@admin_bp.route('/resumes/ajouter', methods=['GET', 'POST'])
@login_required
def abstract_add():
    events = Event.query.filter_by(is_published=True).order_by(Event.date_start.desc()).all()
    if request.method == 'POST':
        pptx_url, pptx_pid = _upload(request.files.get('pptx'), 'amgsbsfax/pptx')
        pdf_url,  pdf_pid  = _upload(request.files.get('pdf'),  'amgsbsfax/pdf')
        a = Abstract(
            event_id           = request.form.get('event_id') or None,
            author_name        = request.form.get('author_name'),
            author_institution = request.form.get('author_institution'),
            title_fr           = request.form.get('title_fr'),
            title_ar           = request.form.get('title_ar'),
            content_fr         = request.form.get('content_fr'),
            presentation_type  = request.form.get('presentation_type'),
            award              = request.form.get('award') or None,
            is_featured        = request.form.get('is_featured') == '1',
            is_published       = request.form.get('is_published') == '1',
            pptx_url           = pptx_url,
            pptx_public_id     = pptx_pid,
            pdf_url            = pdf_url,
            pdf_public_id      = pdf_pid,
        )
        db.session.add(a)
        db.session.commit()
        flash('Résumé ajouté !', 'success')
        return redirect(url_for('admin.abstracts'))
    return render_template('admin/abstract_form.html', abstract=None, events=events)

@admin_bp.route('/resumes/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def abstract_edit(id):
    a = Abstract.query.get_or_404(id)
    events = Event.query.filter_by(is_published=True).order_by(Event.date_start.desc()).all()
    if request.method == 'POST':
        a.event_id           = request.form.get('event_id') or None
        a.author_name        = request.form.get('author_name')
        a.author_institution = request.form.get('author_institution')
        a.title_fr           = request.form.get('title_fr')
        a.title_ar           = request.form.get('title_ar')
        a.content_fr         = request.form.get('content_fr')
        a.presentation_type  = request.form.get('presentation_type')
        a.award              = request.form.get('award') or None
        a.is_featured        = request.form.get('is_featured') == '1'
        a.is_published       = request.form.get('is_published') == '1'
        pptx = request.files.get('pptx')
        if pptx and pptx.filename:
            if a.pptx_public_id: delete_file(a.pptx_public_id, 'raw')
            a.pptx_url, a.pptx_public_id = _upload(pptx, 'amgsbsfax/pptx')
        pdf = request.files.get('pdf')
        if pdf and pdf.filename:
            if a.pdf_public_id: delete_file(a.pdf_public_id, 'raw')
            a.pdf_url, a.pdf_public_id = _upload(pdf, 'amgsbsfax/pdf')
        db.session.commit()
        flash('Résumé mis à jour !', 'success')
        return redirect(url_for('admin.abstracts'))
    return render_template('admin/abstract_form.html', abstract=a, events=events)

@admin_bp.route('/resumes/<int:id>/supprimer', methods=['POST'])
@login_required
def abstract_delete(id):
    a = Abstract.query.get_or_404(id)
    if a.pptx_public_id: delete_file(a.pptx_public_id, 'raw')
    if a.pdf_public_id:  delete_file(a.pdf_public_id,  'raw')
    db.session.delete(a)
    db.session.commit()
    flash('Résumé supprimé.', 'info')
    return redirect(url_for('admin.abstracts'))


@admin_bp.route('/resumes/<int:id>/publier', methods=['POST'])
@login_required
def abstract_toggle_publish(id):
    a = Abstract.query.get_or_404(id)
    a.is_published = not a.is_published
    db.session.commit()
    if a.is_published:
        flash('Resume publie sur le site.', 'success')
    else:
        flash('Resume depublie.', 'info')
    return redirect(url_for('admin.abstracts'))

# ── ACTUALITÉS ────────────────────────────────────────────
@admin_bp.route('/actualites')
@login_required
def news():
    news_list = News.query.order_by(News.published_at.desc()).all()
    return render_template('admin/news.html', news_list=news_list)

@admin_bp.route('/actualites/ajouter', methods=['GET', 'POST'])
@login_required
def news_add():
    if request.method == 'POST':
        url, pid = _upload(request.files.get('image'), 'amgsbsfax/news')
        n = News(
            title_fr     = request.form.get('title_fr'),
            title_ar     = request.form.get('title_ar'),
            content_fr   = request.form.get('content_fr'),
            content_ar   = request.form.get('content_ar'),
            category     = request.form.get('category', 'Général'),
            is_published = request.form.get('is_published') == '1',
            image_url    = url,
            image_public_id = pid,
            published_at = datetime.utcnow(),
        )
        db.session.add(n)
        db.session.commit()
        flash('Actualité publiée !', 'success')
        return redirect(url_for('admin.news'))
    return render_template('admin/news_form.html', item=None)

@admin_bp.route('/actualites/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    n = News.query.get_or_404(id)
    if request.method == 'POST':
        n.title_fr     = request.form.get('title_fr')
        n.title_ar     = request.form.get('title_ar')
        n.content_fr   = request.form.get('content_fr')
        n.content_ar   = request.form.get('content_ar')
        n.category     = request.form.get('category', 'Général')
        n.is_published = request.form.get('is_published') == '1'
        img = request.files.get('image')
        if img and img.filename:
            if n.image_public_id: delete_file(n.image_public_id)
            n.image_url, n.image_public_id = _upload(img, 'amgsbsfax/news')
        db.session.commit()
        flash('Actualité mise à jour !', 'success')
        return redirect(url_for('admin.news'))
    return render_template('admin/news_form.html', item=n)

@admin_bp.route('/actualites/<int:id>/supprimer', methods=['POST'])
@login_required
def news_delete(id):
    n = News.query.get_or_404(id)
    if n.image_public_id: delete_file(n.image_public_id)
    db.session.delete(n)
    db.session.commit()
    flash('Actualité supprimée.', 'info')
    return redirect(url_for('admin.news'))

# ── MESSAGES ──────────────────────────────────────────────
@admin_bp.route('/messages')
@login_required
def messages():
    msgs = ContactMessage.query.order_by(ContactMessage.sent_at.desc()).all()
    return render_template('admin/messages.html', msgs=msgs)

@admin_bp.route('/messages/<int:id>')
@login_required
def message_read(id):
    msg = ContactMessage.query.get_or_404(id)
    if not msg.is_read:
        msg.is_read = True
        db.session.commit()
    return render_template('admin/message_detail.html', msg=msg)

@admin_bp.route('/messages/<int:id>/supprimer', methods=['POST'])
@login_required
def message_delete(id):
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message supprimé.', 'info')
    return redirect(url_for('admin.messages'))
# ── GALERIE PHOTOS ────────────────────────────────────────
@admin_bp.route('/galerie')
@login_required
def gallery():
    photos = GalleryPhoto.query.order_by(GalleryPhoto.order, GalleryPhoto.uploaded_at.desc()).all()
    return render_template('admin/gallery.html', photos=photos)

@admin_bp.route('/galerie/ajouter', methods=['GET', 'POST'])
@login_required
def gallery_add():
    if request.method == 'POST':
        file = request.files.get('photo')
        if not file or not file.filename:
            flash('Veuillez sélectionner une photo.', 'error')
            return render_template('admin/gallery_form.html', item=None)
        url, pid = _upload(file, 'amgsbsfax/gallery')
        if not url:
            flash('Erreur upload Cloudinary.', 'error')
            return render_template('admin/gallery_form.html', item=None)
        photo = GalleryPhoto(
            url         = url,
            public_id   = pid,
            caption_fr  = request.form.get('caption_fr', ''),
            caption_ar  = request.form.get('caption_ar', ''),
            is_featured = request.form.get('is_featured') == '1',
            order       = int(request.form.get('order', 0) or 0),
            is_active   = True,
        )
        db.session.add(photo)
        db.session.commit()
        flash('Photo ajoutée avec succès !', 'success')
        return redirect(url_for('admin.gallery'))
    return render_template('admin/gallery_form.html', item=None)

@admin_bp.route('/galerie/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def gallery_edit(id):
    photo = GalleryPhoto.query.get_or_404(id)
    if request.method == 'POST':
        photo.caption_fr  = request.form.get('caption_fr', '')
        photo.caption_ar  = request.form.get('caption_ar', '')
        photo.is_featured = request.form.get('is_featured') == '1'
        photo.order       = int(request.form.get('order', 0) or 0)
        photo.is_active   = request.form.get('is_active') == '1'
        file = request.files.get('photo')
        if file and file.filename:
            if photo.public_id:
                delete_file(photo.public_id)
            photo.url, photo.public_id = _upload(file, 'amgsbsfax/gallery')
        db.session.commit()
        flash('Photo mise à jour !', 'success')
        return redirect(url_for('admin.gallery'))
    return render_template('admin/gallery_form.html', item=photo)

@admin_bp.route('/galerie/<int:id>/supprimer', methods=['POST'])
@login_required
def gallery_delete(id):
    photo = GalleryPhoto.query.get_or_404(id)
    if photo.public_id:
        delete_file(photo.public_id)
    db.session.delete(photo)
    db.session.commit()
    flash('Photo supprimée.', 'info')
    return redirect(url_for('admin.gallery'))

# ── CONFIRMATION INSCRIPTION + EMAIL ──────────────────────
@admin_bp.route('/inscriptions/<int:id>/confirmer', methods=['POST'])
@login_required
def registration_confirm(id):
    from app.utils.mail import send_confirmation_email_admin
    reg = Registration.query.get_or_404(id)
    reg.status = 'confirmed'
    db.session.commit()
    # Envoyer email de confirmation
    ok = send_confirmation_email_admin(reg)
    if ok:
        flash(f'✅ Inscription confirmée. Email envoyé à {reg.email}.', 'success')
    else:
        flash(f'✅ Inscription confirmée mais erreur envoi email à {reg.email}.', 'error')
    return redirect(url_for('admin.registrations'))

@admin_bp.route('/inscriptions/<int:id>/renvoyer-email', methods=['POST'])
@login_required
def registration_resend(id):
    from app.utils.mail import send_confirmation_email_admin
    reg = Registration.query.get_or_404(id)
    ok = send_confirmation_email_admin(reg)
    if ok:
        flash(f'📧 Email de confirmation renvoyé à {reg.email}.', 'success')
    else:
        flash(f'❌ Erreur lors de l\'envoi de l\'email à {reg.email}.', 'error')
    return redirect(url_for('admin.registrations'))
