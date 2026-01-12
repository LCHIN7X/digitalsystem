from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Scholarship, Application
from app.extensions import db
import os

student_bp = Blueprint('student', __name__, template_folder='templates/student')

@student_bp.route('/dashboard')
@login_required
def dashboard():
    apps = Application.query.filter_by(student_id=current_user.id).all()
    return render_template('student/dashboard.html', applications=apps)

@student_bp.route('/scholarships')
@login_required
def scholarships():
    scholarships = Scholarship.query.all()
    return render_template('scholarships.html', scholarships=scholarships)

@student_bp.route('/apply/<int:scholarship_id>', methods=['GET','POST'])
@login_required
def apply(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    if request.method == 'POST':
        files = request.files.getlist('documents')
        saved_files = []
        for f in files:
            filepath = os.path.join('app/static/uploads', f.filename)
            f.save(filepath)
            saved_files.append(filepath)
        app_entry = Application(student_id=current_user.id, scholarship_id=scholarship.id, 
                                documents=",".join(saved_files))
        db.session.add(app_entry)
        db.session.commit()
        flash("Application submitted!", "success")
        return redirect(url_for('student.dashboard'))
    return render_template('apply.html', scholarship=scholarship)

@student_bp.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        bio = request.form.get('bio')

        # Update username and bio
        current_user.username = username
        current_user.bio = bio

        # Handle profile picture
        file = request.files.get('profile_pic')
        if file:
            filename = file.filename
            filepath = os.path.join('app/static/uploads', filename)
            file.save(filepath)
            current_user.profile_pic = filename

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html')

@student_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # 1. Check current password
        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect", "danger")
            return redirect(url_for('student.change_password'))

        # 2. Check new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match", "danger")
            return redirect(url_for('student.change_password'))

        # 3. Password eligibility check
        if len(new_password) < 8 or not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
            flash("Password must be at least 8 characters and contain letters and numbers", "danger")
            return redirect(url_for('student.change_password'))

        # 4. Update password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for('student.profile'))

    return render_template('student/change_password.html')


@student_bp.route('/eligibility/<int:scholarship_id>', methods=['GET','POST'])
@login_required
def eligibility(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    eligible = None

    if request.method == 'POST':
        # simple keyword match in profile
        criteria = scholarship.eligibility_criteria or ""
        if criteria.lower() in current_user.username.lower():
            eligible = True
        else:
            eligible = False

    return render_template('student/eligibility.html', scholarship=scholarship, eligible=eligible)
