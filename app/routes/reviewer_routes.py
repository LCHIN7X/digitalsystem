from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Application, Review

reviewer_bp = Blueprint('reviewer', __name__, template_folder='templates/reviewer')

# =========================
# DASHBOARD
# =========================

@reviewer_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'reviewer':
        abort(403)

    total = Application.query.filter_by(reviewer_id=current_user.id).count()
    pending = Application.query.filter_by(reviewer_id=current_user.id, status="Assigned").count()
    reviewed = Application.query.filter_by(reviewer_id=current_user.id, status="Reviewed").count()

    return render_template(
        'reviewer/dashboard.html',
        total=total,
        pending=pending,
        reviewed=reviewed
    )


# =========================
# VIEW ASSIGNED APPLICATIONS
# =========================
@reviewer_bp.route('/applications')
@login_required
def applications():
    if current_user.role != 'reviewer':
        abort(403)

    sort = request.args.get('sort')

    query = Application.query.filter_by(reviewer_id=current_user.id)

    if sort == 'cgpa':
        query = query.order_by(Application.submitted_at.desc())
    elif sort == 'date':
        query = query.order_by(Application.submitted_at.desc())
    elif sort == 'status':
        query = query.order_by(Application.status)

    apps = query.all()

    return render_template('reviewer/applications.html', apps=apps)


# =========================
# REVIEW FORM
# =========================
@reviewer_bp.route('/review/<int:app_id>', methods=['GET', 'POST'])
@login_required
def review(app_id):
    if current_user.role != 'reviewer':
        abort(403)

    app = Application.query.get_or_404(app_id)

    # prevent double review
    if Review.query.filter_by(application_id=app.id, reviewer_id=current_user.id).first():
        return redirect(url_for('reviewer.applications'))

    if request.method == 'POST':
        score = request.form['score']
        decision = request.form['decision']
        comment = request.form['comment']

        review = Review(
            application_id=app.id,
            reviewer_id=current_user.id,
            score=score,
            decision=decision,
            comment=comment
        )

        app.status = "Reviewed"

        db.session.add(review)
        db.session.commit()

        return redirect(url_for('reviewer.applications'))

    return render_template('reviewer/review_form.html', app=app)

@reviewer_bp.route('/ranking')
@login_required
def ranking():
    if current_user.role != 'reviewer':
        abort(403)

    apps = Application.query \
        .join(Review) \
        .filter(Application.reviewer_id == current_user.id) \
        .order_by(Review.score.desc()) \
        .all()

    return render_template('reviewer/ranking.html', apps=apps)

