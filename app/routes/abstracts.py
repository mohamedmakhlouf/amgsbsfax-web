# app/routes/abstracts.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Abstract, Event, db
from app.utils.cloudinary_helper import upload_file
from datetime import datetime

abstracts_bp = Blueprint('abstracts', __name__)


def _upload_doc(file_obj, folder):
    """Upload document vers Cloudinary, retourne (url, public_id)."""
    if file_obj and file_obj.filename:
        try:
            result = upload_file(file_obj, folder=folder, resource_type='raw')
            return result.get('secure_url'), result.get('public_id')
        except Exception:
            pass
    return None, None


@abstracts_bp.route('/')
def index():
    featured  = Abstract.query.filter_by(is_published=True, is_featured=True)\
                               .order_by(Abstract.award).all()
    abstracts = Abstract.query.filter_by(is_published=True)\
                               .order_by(Abstract.submitted_at.desc()).all()
    events    = Event.query.filter_by(is_published=True)\
                            .order_by(Event.date_start.desc()).all()
    return render_template('abstracts/index.html',
                           featured=featured,
                           abstracts=abstracts,
                           events=events)


@abstracts_bp.route('/<int:abstract_id>')
def detail(abstract_id):
    abstract = Abstract.query.get_or_404(abstract_id)
    return render_template('abstracts/detail.html', abstract=abstract)


@abstracts_bp.route('/soumettre', methods=['POST'])
def submit():
    try:
        # Upload fichiers
        pptx_url, pptx_pid = _upload_doc(request.files.get('pptx_file'), 'amgsbsfax/abstracts/pptx')
        pdf_url,  pdf_pid  = _upload_doc(request.files.get('pdf_file'),  'amgsbsfax/abstracts/pdf')

        ab = Abstract(
            event_id          = request.form.get('event_id') or None,
            author_name       = request.form.get('author_name', '').strip(),
            author_email      = request.form.get('author_email', '').strip(),
            author_institution= request.form.get('author_institution', '').strip(),
            title_fr          = request.form.get('title_fr', '').strip(),
            title_ar          = request.form.get('title_ar', '').strip(),
            content_fr        = request.form.get('content_fr', '').strip(),
            content_ar        = request.form.get('content_ar', '').strip(),
            presentation_type = request.form.get('presentation_type', 'oral'),
            pptx_url          = pptx_url,
            pptx_public_id    = pptx_pid,
            pdf_url           = pdf_url,
            pdf_public_id     = pdf_pid,
            is_published      = False,   # en attente de validation admin
            submitted_at      = datetime.utcnow(),
        )
        db.session.add(ab)
        db.session.commit()
        flash('Votre travail a été soumis avec succès ! Vous serez notifié par email après examen.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la soumission : {str(e)}', 'error')

    return redirect(url_for('abstracts.index') + '#tab-submit')