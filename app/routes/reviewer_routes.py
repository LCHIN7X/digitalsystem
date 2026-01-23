from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Application, Review

reviewer_bp = Blueprint(
    'reviewer',
    __name__,
    template_folder='templates/reviewer'
)

# =========================
# DASHBOARD
# =========================
@reviewer_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'reviewer':
        abort(403)

    assigned_q = (
        Application.query
        .join(Review, Review.application_id == Application.id)
        .filter(Review.reviewer_id == current_user.id)
    )

    total = assigned_q.distinct().count()

    pending = (
        assigned_q
        .filter(Application.status != "Reviewed")
        .distinct()
        .count()
    )

    reviewed = (
        assigned_q
        .filter(Application.status == "Reviewed")
        .distinct()
        .count()
    )

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

    query = (
        Application.query
        .join(Review, Review.application_id == Application.id)
        .filter(Review.reviewer_id == current_user.id)
        .distinct()
    )

    if sort == 'date':
        query = query.order_by(Application.submitted_at.desc())
    elif sort == 'status':
        query = query.order_by(Application.status)

    apps = query.all()

    return render_template(
        'reviewer/applications.html',
        apps=apps
    )


# =========================
# REVIEW FORM
# =========================
@reviewer_bp.route('/review/<int:app_id>', methods=['GET', 'POST'])
@login_required
def review(app_id):
    if current_user.role != 'reviewer':
        abort(403)

    app_obj = Application.query.get_or_404(app_id)

    review_row = Review.query.filter_by(
        application_id=app_obj.id,
        reviewer_id=current_user.id
    ).first()

    if not review_row:
        flash("This application is not assigned to you.", "danger")
        return redirect(url_for('reviewer.applications'))

    # prevent double review
    if review_row.decision or review_row.score is not None:
        flash("You already reviewed this application.", "info")
        return redirect(url_for('reviewer.view_review', app_id=app_obj.id))

    if request.method == 'POST':
        # score may come as string; store as int if possible
        score_val = request.form.get('score')
        try:
            review_row.score = int(score_val) if score_val is not None and score_val != "" else None
        except ValueError:
            review_row.score = None

        review_row.decision = request.form.get('decision')
        review_row.comment = request.form.get('comment')

        # Use DB time (no datetime import needed)
        review_row.reviewed_at = db.func.now()

        # keep backward compatibility
        if hasattr(review_row, "comments") and not review_row.comments:
            review_row.comments = review_row.comment

        app_obj.status = "Reviewed"

        db.session.commit()

        flash("Review submitted successfully.", "success")
        return redirect(url_for('reviewer.applications'))

    return render_template(
        'reviewer/review_form.html',
        app=app_obj
    )


# =========================
# VIEW REVIEW
# =========================
@reviewer_bp.route('/review/<int:app_id>/view')
@login_required
def view_review(app_id):
    if current_user.role != 'reviewer':
        abort(403)

    app_obj = Application.query.get_or_404(app_id)

    review_row = Review.query.filter_by(
        application_id=app_obj.id,
        reviewer_id=current_user.id
    ).first()

    if not review_row:
        flash("This application is not assigned to you.", "danger")
        return redirect(url_for('reviewer.applications'))

    return render_template(
        'reviewer/view_review.html',
        app=app_obj,
        review=review_row
    )


# =========================
# RANKING
# =========================
@reviewer_bp.route('/ranking')
@login_required
def ranking():
    if current_user.role != 'reviewer':
        abort(403)

    apps = (
        Application.query
        .join(Review, Review.application_id == Application.id)
        .filter(Review.reviewer_id == current_user.id)
        .order_by(Review.score.desc())
        .distinct()
        .all()
    )

    return render_template(
        'reviewer/ranking.html',
        apps=apps
    )
