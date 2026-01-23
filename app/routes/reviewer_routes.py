from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import distinct

from app.models import db, Application, Review

reviewer_bp = Blueprint(
    'reviewer',
    __name__,
    template_folder='templates/reviewer'
)

<<<<<<< HEAD
# =========================
# DASHBOARD
# =========================
=======
>>>>>>> 132a9ca1016390dc28d9dc8796cb3cc0b2fef3fa
@reviewer_bp.route('/dashboard')
@login_required
def dashboard():
    reviews = Application.query.join(Review, Application.id==Review.application_id)\
                .filter(Review.reviewer_id==current_user.id).all()
    return render_template('reviewer/dashboard.html', applications=reviews)

<<<<<<< HEAD
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
        review_row.score = request.form.get('score')
        review_row.decision = request.form.get('decision')
        review_row.comment = request.form.get('comment')
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
# VIEW REVIEW (OPTION B FIX)
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
=======
@reviewer_bp.route('/review/<int:application_id>', methods=['GET','POST'])
@login_required
def review_application(application_id):
    app_entry = Application.query.get_or_404(application_id)
    if request.method == 'POST':
        score = request.form['score']
        comments = request.form['comments']
        review = Review(application_id=application_id, reviewer_id=current_user.id, 
                        score=score, comments=comments)
        db.session.add(review)
        db.session.commit()
        flash("Review submitted!", "success")
        return redirect(url_for('reviewer.dashboard'))
    return render_template('review.html', application=app_entry)
>>>>>>> 132a9ca1016390dc28d9dc8796cb3cc0b2fef3fa
