from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Application, Review

reviewer_bp = Blueprint('reviewer', __name__, template_folder='templates/reviewer')

@reviewer_bp.route('/dashboard')
@login_required
def dashboard():
    reviews = Application.query.join(Review, Application.id==Review.application_id)\
                .filter(Review.reviewer_id==current_user.id).all()
    return render_template('dashboard.html', applications=reviews)

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
