from flask import render_template, redirect, url_for, flash, request,Blueprint
from flask_login import login_required
from app.models import db, Scholarship,User,Application,Review
from app.forms import ScholarshipForm

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_apps = Application.query.count()
    total_scholarships = Scholarship.query.count()
    return render_template('dashboard.html', total_apps=total_apps, total_scholarships=total_scholarships)


@admin_bp.route('/create_scholarship', methods=['GET', 'POST'])
@login_required
def create_scholarship():
    form = ScholarshipForm()
    if form.validate_on_submit():
        scholarship = Scholarship(
            title=form.title.data,
            description=form.description.data,
            eligibility_criteria=form.eligibility_criteria.data,
            documents_required=form.documents_required.data,
            application_deadline=form.application_deadline.data
        )
        db.session.add(scholarship)
        db.session.commit()
        flash("Scholarship created successfully!", "success")
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_scholarship.html', form=form)

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET','POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = RegistrationForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        user.role = form.role.data
        db.session.commit()
        flash("User updated!", "success")
        return redirect(url_for('admin.manage_users'))
    return render_template('auth/register.html', form=form)

@admin_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted!", "info")
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/assign_reviewers/<int:application_id>', methods=['GET', 'POST'])
@login_required
def assign_reviewers(application_id):
    application = Application.query.get_or_404(application_id)
    
    # Get all users with reviewer role
    reviewers = User.query.filter_by(role='reviewer').all()
    form = AssignReviewersForm()
    form.reviewers.choices = [(r.id, r.username) for r in reviewers]

    if form.validate_on_submit():
        selected_reviewers = form.reviewers.data  # list of reviewer IDs
        for reviewer_id in selected_reviewers:
            # Check if already assigned
            existing_review = Review.query.filter_by(application_id=application.id, reviewer_id=reviewer_id).first()
            if not existing_review:
                review = Review(application_id=application.id, reviewer_id=reviewer_id)
                db.session.add(review)
        db.session.commit()
        flash("Reviewers assigned successfully!", "success")
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/assign_reviewers.html', application=application, form=form)
