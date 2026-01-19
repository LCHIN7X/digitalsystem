from flask import render_template, redirect, url_for, flash, request, Blueprint, Response
from flask_login import login_required, login_user, current_user
from werkzeug.security import check_password_hash
from sqlalchemy import func

import csv
import io

from app.models import db, Scholarship, User, Application, Review, SystemLog
from app.forms import (
    ScholarshipForm,
    RegistrationForm,
    AssignReviewersForm,
    ApplicationStatusForm
)

# IMPORTANT:
# In your run.py you already register the blueprint with url_prefix="/admin"
# so we should NOT put url_prefix here (otherwise it becomes /admin/admin/...)
admin_bp = Blueprint('admin', __name__)


# =========================
# HELPER: LOG EVENTS
# =========================
def log_event(level: str, action: str, message: str, user_id=None):
    try:
        db.session.add(SystemLog(
            level=level,
            action=action,
            message=message,
            user_id=user_id
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        # don't crash if logging fails


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

        log_event(
            "info",
            "CREATE_SCHOLARSHIP",
            f"Admin created scholarship: {scholarship.title} (ID {scholarship.id})",
            user_id=current_user.id
        )

        flash("Scholarship created successfully!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_scholarship.html', form=form)


# =========================
# MANAGE USERS (VIEW ONLY)
# =========================
@admin_bp.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))

    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


# =========================
# MANAGE APPLICATION STAGES
# =========================
@admin_bp.route('/applications')
@login_required
def manage_applications():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))

    applications = Application.query.order_by(Application.id.desc()).all()

    forms = {}
    for a in applications:
        f = ApplicationStatusForm()
        f.status.data = a.status if hasattr(a, "status") and a.status else "Submitted"
        forms[a.id] = f

    return render_template(
        'admin/manage_applications.html',
        applications=applications,
        forms=forms
    )


@admin_bp.route('/applications/<int:application_id>/status', methods=['POST'])
@login_required
def update_application_status(application_id):
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('auth.login'))

    app_obj = Application.query.get_or_404(application_id)
    form = ApplicationStatusForm()

    if form.validate_on_submit():
        app_obj.status = form.status.data
        db.session.commit()

        log_event(
            "info",
            "UPDATE_STATUS",
            f"Admin updated application #{app_obj.id} status to: {app_obj.status}",
            user_id=current_user.id
        )

        flash("Application status updated.", "success")
    else:
        flash("Failed to update status.", "danger")

    return redirect(url_for('admin.manage_applications'))


# =========================
# ASSIGN REVIEWERS
# =========================
@admin_bp.route("/assign_reviewers/<int:application_id>", methods=["GET", "POST"])
@login_required
def assign_reviewers(application_id):
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    application = Application.query.get_or_404(application_id)

    reviewers = User.query.filter_by(role="reviewer").all()

    form = AssignReviewersForm()
    form.reviewers.choices = [(r.id, r.username) for r in reviewers]

    if form.validate_on_submit():
        selected_ids = form.reviewers.data

        added = 0
        for reviewer_id in selected_ids:
            exists = Review.query.filter_by(
                application_id=application.id,
                reviewer_id=reviewer_id
            ).first()
            if not exists:
                db.session.add(Review(application_id=application.id, reviewer_id=reviewer_id))
                added += 1

        db.session.commit()

        log_event(
            "info",
            "ASSIGN_REVIEWERS",
            f"Admin assigned {added} reviewer(s) for application #{application.id}",
            user_id=current_user.id
        )

        flash(f"Reviewers assigned successfully! Added {added}.", "success")
        return redirect(url_for("admin.manage_applications"))

    existing_reviews = Review.query.filter_by(application_id=application.id).all()
    assigned_reviewer_ids = {r.reviewer_id for r in existing_reviews}

    return render_template(
        "admin/assign_reviewers.html",
        application=application,
        form=form,
        reviewers=reviewers,
        assigned_reviewer_ids=assigned_reviewer_ids
    )


# =========================
# ADMIN REPORTS
# =========================
@admin_bp.route("/reports")
@login_required
def reports():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    total_users = User.query.count()
    total_scholarships = Scholarship.query.count()
    total_apps = Application.query.count()

    status_rows = (
        db.session.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    status_counts = {status or "Unknown": count for status, count in status_rows}

    role_rows = (
        db.session.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )
    role_counts = {role or "Unknown": count for role, count in role_rows}

    return render_template(
        "admin/reports.html",
        total_users=total_users,
        total_scholarships=total_scholarships,
        total_apps=total_apps,
        status_counts=status_counts,
        role_counts=role_counts
    )


@admin_bp.route("/reports/export_csv")
@login_required
def export_reports_csv():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Report Type", "Key", "Value"])
    writer.writerow(["Totals", "Total Users", User.query.count()])
    writer.writerow(["Totals", "Total Scholarships", Scholarship.query.count()])
    writer.writerow(["Totals", "Total Applications", Application.query.count()])

    status_rows = (
        db.session.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    for status, count in status_rows:
        writer.writerow(["Applications by Status", status or "Unknown", count])

    role_rows = (
        db.session.query(User.role, func.count(User.id))
        .group_by(User.role)
        .all()
    )
    for role, count in role_rows:
        writer.writerow(["Users by Role", role or "Unknown", count])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=admin_report.csv"}
    )


# =========================
# ADMIN SYSTEM LOGS
# =========================
@admin_bp.route("/logs")
@login_required
def system_logs():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    level = request.args.get("level", "").strip()
    action = request.args.get("action", "").strip()

    q = SystemLog.query.order_by(SystemLog.id.desc())
    if level:
        q = q.filter(SystemLog.level == level)
    if action:
        q = q.filter(SystemLog.action == action)

    logs = q.limit(200).all()

    levels = [r[0] for r in db.session.query(SystemLog.level).distinct().all()]
    actions = [r[0] for r in db.session.query(SystemLog.action).distinct().all()]

    return render_template(
        "admin/logs.html",
        logs=logs,
        levels=levels,
        actions=actions,
        selected_level=level,
        selected_action=action
    )


@admin_bp.route("/logs/clear", methods=["POST"])
@login_required
def clear_logs():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    SystemLog.query.delete()
    db.session.commit()

    log_event("warning", "CLEAR_LOGS", "Admin cleared all system logs.", user_id=current_user.id)

    flash("System logs cleared.", "success")
    return redirect(url_for("admin.system_logs"))
