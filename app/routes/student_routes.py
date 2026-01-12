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
    return render_template('student/scholarships.html', scholarships=scholarships)

@student_bp.route('/apply/<int:scholarship_id>', methods=['GET','POST'])
@login_required
def apply(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)

    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if request.method == 'POST':
        # 1️⃣ Save uploaded files
        files_to_save = []

        # Passport photo
        photo = request.files.get('photo')
        if photo:
            photo_path = os.path.join('app/static/uploads', photo.filename)
            photo.save(photo_path)
            files_to_save.append(photo_path)

        # Academic document
        academic_doc = request.files.get('academic_doc')
        if academic_doc:
            doc_path = os.path.join('app/static/uploads', academic_doc.filename)
            academic_doc.save(doc_path)
            files_to_save.append(doc_path)

        # 2️⃣ Collect all form fields into a dictionary
        application_data = {
            "full_name": request.form.get('full_name'),
            "address": request.form.get('address'),
            "ic_number": request.form.get('ic_number'),
            "dob": request.form.get('dob'),
            "age": request.form.get('age'),
            "intake": request.form.get('intake'),
            "programme": request.form.get('programme'),
            "course": request.form.get('course'),
            "nationality": request.form.get('nationality'),
            "race": request.form.get('race'),
            "sex": request.form.get('sex'),
            "contact": request.form.get('contact'),
            "home_contact": request.form.get('home_contact'),
            "household_income": request.form.get('household_income'),
            "email": request.form.get('email'),
            "family_name": request.form.getlist('family_name[]'),
            "relationship": request.form.getlist('relationship[]'),
            "family_age": request.form.getlist('family_age[]'),
            "occupation": request.form.getlist('occupation[]'),
            "family_income": request.form.getlist('family_income[]'),
            "school_name": request.form.get('school_name'),
            "qualification": request.form.get('qualification'),
            "activity_type": request.form.getlist('activity_type[]'),
            "level": request.form.getlist('level[]'),
            "year": request.form.getlist('year[]'),
            "achievement": request.form.getlist('achievement[]'),
            "statement": request.form.get('statement')
        }

        # 3️⃣ Save to database
        new_application = Application(
            student_id=current_user.id,
            scholarship_id=scholarship.id,
            documents=",".join(files_to_save),
            status="Pending"
        )

        # Optional: Save all form data as JSON inside documents or another column
        # You can add a new column `form_data = db.Column(db.JSON)` to Application model
        # new_application.form_data = application_data

        db.session.add(new_application)
        db.session.commit()

        flash("Your application has been submitted!", "success")
        return redirect(url_for('student.dashboard'))

    # GET request: show form
    return render_template('student/apply.html', scholarship=scholarship)


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
