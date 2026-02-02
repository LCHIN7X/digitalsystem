from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import func, case

from app.models import db, Application, Review, User, Scholarship, SystemLog

committee_bp = Blueprint("committee", __name__, template_folder="templates/committee")


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
# DASHBOARD
# =========================
@committee_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "committee":
        abort(403)

    total = Application.query.count()
    submitted = Application.query.filter(Application.status.in_(["Submitted", "Pending"])).count()
    reviewed = Application.query.filter_by(status="Reviewed").count()
    accepted = Application.query.filter_by(status="Accepted").count()
    rejected = Application.query.filter_by(status="Rejected").count()

    return render_template(
        "committee/dashboard.html",
        total=total,
        submitted=submitted,
        reviewed=reviewed,
        accepted=accepted,
        rejected=rejected
    )


# =========================
# LIST APPLICATIONS (FILTER / SORT / FAIL)
# =========================
@committee_bp.route("/applications")
@login_required
def applications():
    if current_user.role != "committee":
        abort(403)

    status = request.args.get("status", "").strip()      # e.g. Submitted/Reviewed/Accepted/Rejected
    sort = request.args.get("sort", "").strip()          # avg_score_desc / avg_score_asc
    fail_only = request.args.get("fail", "").strip()     # "1" = fail only

    # --- Subquery: avg_score + fail_count for each application ---
    avg_sq = (
        db.session.query(
            Review.application_id.label("app_id"),
            func.avg(Review.score).label("avg_score"),
            func.sum(case((Review.decision == "Fail", 1), else_=0)).label("fail_count")
        )
        .group_by(Review.application_id)
        .subquery()
    )

    # Query returns rows: (Application, avg_score, fail_count)
    q = (
        db.session.query(Application, avg_sq.c.avg_score, avg_sq.c.fail_count)
        .outerjoin(avg_sq, avg_sq.c.app_id == Application.id)
        .order_by(Application.id.desc())
    )

    # filter by status
    if status:
        q = q.filter(Application.status == status)

    # fail_only rule:
    # - fail if ANY reviewer decision == Fail OR avg_score < 3
    if fail_only == "1":
        q = q.filter(
            (func.coalesce(avg_sq.c.fail_count, 0) > 0) |
            (func.coalesce(avg_sq.c.avg_score, 0) < 3)
        )

    # sort by avg score
    if sort == "avg_score_desc":
        q = q.order_by(func.coalesce(avg_sq.c.avg_score, 0).desc())
    elif sort == "avg_score_asc":
        q = q.order_by(func.coalesce(avg_sq.c.avg_score, 0).asc())

    rows = q.all()

    return render_template(
        "committee/applications.html",
        rows=rows,
        status=status,
        sort=sort,
        fail_only=fail_only
    )


# =========================
# VIEW APPLICATION DETAIL + REVIEWS
# =========================
@committee_bp.route("/applications/<int:application_id>")
@login_required
def view_application(application_id):
    if current_user.role != "committee":
        abort(403)

    app_obj = Application.query.get_or_404(application_id)

    # reviews for this application
    reviews = Review.query.filter_by(application_id=app_obj.id).all()

    # average score
    avg_score = db.session.query(func.avg(Review.score)).filter(Review.application_id == app_obj.id).scalar()
    avg_score = float(avg_score) if avg_score is not None else 0.0

    # parse documents (comma-separated paths)
    docs = []
    if getattr(app_obj, "documents", None):
        docs = [d.strip() for d in app_obj.documents.split(",") if d.strip()]

    return render_template(
        "committee/application_detail.html",
        application=app_obj,
        reviews=reviews,
        avg_score=avg_score,
        documents=docs
    )


# =========================
# DECIDE ACCEPT / REJECT + "NOTIFY"
# =========================
@committee_bp.route("/applications/<int:application_id>/decision", methods=["POST"])
@login_required
def make_decision(application_id):
    if current_user.role != "committee":
        abort(403)

    app_obj = Application.query.get_or_404(application_id)

    # ✅ decision 可以来自：
    # 1) form hidden input: <input name="decision" value="Accepted">
    # 2) query string: /decision?decision=Accepted (也兼容)
    decision_raw = (
        request.form.get("decision")
        or request.args.get("decision")
        or ""
    ).strip().lower()

    # ✅ 兼容不同写法（避免 Invalid decision）
    mapping = {
        "accepted": "Accepted",
        "accept": "Accepted",
        "approved": "Accepted",
        "approve": "Accepted",

        "rejected": "Rejected",
        "reject": "Rejected",
    }

    if decision_raw not in mapping:
        flash("Invalid decision.", "danger")
        return redirect(url_for("committee.view_application", application_id=app_obj.id))

    decision = mapping[decision_raw]
    app_obj.status = decision
    db.session.commit()

    # Simulated notification (for assignment): flash + log
    flash(
        f"Application #{app_obj.id} marked as {decision}. Notification sent to student (simulated).",
        "success"
    )

    log_event(
        "info",
        "COMMITTEE_DECISION",
        f"Committee set application #{app_obj.id} to {decision}. (Notification simulated)",
        user_id=current_user.id
    )

    return redirect(url_for("committee.view_application", application_id=app_obj.id))
