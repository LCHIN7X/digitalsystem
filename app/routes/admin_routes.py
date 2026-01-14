from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import db, Scholarship, User, Application, Review
from app.forms import ScholarshipForm, RegistrationForm, AssignReviewersForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# =========================
# ADMIN LOGIN (USERNAME)
# =========================
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if not user or user.role != 'admin':
            flash("Admin account not found.", "danger")
            return redirect(url_for('admin.admin_login'))

        if not check_password_hash(user.password, password):
            flash("Incorrect password.", "danger")
            return redirect(url_for('admin.admin_login'))

        login_user(user)
        flash("Welcome Admin!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html')


# =========================
# ADMIN DASHBOARD
# =========================
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))

    total_apps = Application.query.count()
    total_scholarships = Scholarship.query.count()

    return render_template(
        'admin/dashboard.html',
        total_apps=total_apps,
        total_scholarships=total_scholarships
    )


# =========================
# CREATE SCHOLARSHIP
# =========================
@admin_bp.route('/create_scholarship', methods=['GET', 'POST'])
@login_required
def create_scholarship():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))

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


# =========================
# MANAGE USERS
# =========================
@admin_bp.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))

    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)
