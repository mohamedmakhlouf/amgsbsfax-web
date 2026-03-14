@register_bp.route('/confirmation/<int:reg_id>')
def confirmation(reg_id):
    registration = Registration.query.get_or_404(reg_id)
    return render_template('register/confirmation.html', registration=registration)
