from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Application, Scholarship, User, Review

# Optional: use SystemLog if you already added it (admin part)
try:
    from app.models import SystemLog
except Exception:
    SystemLog = None

committee_bp = Blueprint("committee", __name__)


def committee_only():
    return current_user.is_authenticated and current_user.role == "committee"


def log_event(level: str, action: str, message: str, user_id=None):
    if SystemLog is None:
        return
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


# =========================
# COMMITTEE DASHBOARD
# =========================
@committee_bp.route("/dashboard")
@login_required
def dashboard():
    if not committee_only():
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    total_apps = Application.query.count()
    pending_apps = Application.query.filter_by(status="Pending").count()
    accepted_apps = Application.query.filter_by(status="Accepted").count()
    rejected_apps = Application.query.filter_by(status="Rejected").count()

    return render_template(
        "committee/dashboard.html",
        total_apps=total_apps,
        pending_apps=pending_apps,
        accepted_apps=accepted_apps,
        rejected_apps=rejected_apps
    )


# =========================
# SEE ALL APPLICATIONS
# =========================
@committee_bp.route("/applications")
@login_required
def applications():
    if not committee_only():
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    status_filter = request.args.get("status", "").strip()

    q = Application.query.order_by(Application.id.desc())
    if status_filter:
        q = q.filter(Application.status == status_filter)

    applications_list = q.all()

    return render_template(
        "committee/applications.html",
        applications=applications_list,
        selected_status=status_filter
    )


# =========================
# OPEN AN APPLICATION (DETAIL)
# =========================
@committee_bp.route("/applications/<int:application_id>")
@login_required
def application_detail(application_id):
    if not committee_only():
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    app_obj = Application.query.get_or_404(application_id)

    student = User.query.get(app_obj.student_id)
    scholarship = Scholarship.query.get(app_obj.scholarship_id)

    reviews = Review.query.filter_by(application_id=app_obj.id).order_by(Review.id.desc()).all()

    # documents stored as comma-separated paths
    doc_links = []
    if app_obj.documents:
        paths = [p.strip() for p in app_obj.documents.split(",") if p.strip()]
        for p in paths:
            p2 = p.replace("\\", "/")
            if p2.startswith("app/"):
                p2 = p2[len("app/"):]
            if not p2.startswith("/"):
                p2 = "/" + p2
            doc_links.append(p2)

    scores = [r.score for r in reviews if r.score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    return render_template(
        "committee/application_detail.html",
        application=app_obj,
        student=student,
        scholarship=scholarship,
        reviews=reviews,
        doc_links=doc_links,
        avg_score=avg_score
    )


# =========================
# ACCEPT / REJECT (NOTIFY)
# =========================
@committee_bp.route("/applications/<int:application_id>/decision", methods=["POST"])
@login_required
def make_decision(application_id):
    if not committee_only():
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    app_obj = Application.query.get_or_404(application_id)

    decision = request.form.get("decision", "").strip()
    if decision not in ["Accepted", "Rejected"]:
        flash("Invalid decision.", "danger")
        return redirect(url_for("committee.application_detail", application_id=application_id))

    app_obj.status = decision
    db.session.commit()

    flash(f"Decision submitted: {decision}. Notification sent to student (in-app).", "success")

    log_event(
        "info",
        "COMMITTEE_DECISION",
        f"Committee set application #{app_obj.id} to {decision}",
        user_id=current_user.id
    )

    return redirect(url_for("committee.application_detail", application_id=application_id))
