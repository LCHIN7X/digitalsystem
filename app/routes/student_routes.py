from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Scholarship, Application
import os

student_bp = Blueprint('student', __name__, template_folder='templates/student')

@student_bp.route('/dashboard')
@login_required
def dashboard():
    apps = Application.query.filter_by(student_id=current_user.id).all()
    return render_template('dashboard.html', applications=apps)

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
