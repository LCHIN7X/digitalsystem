from flask import Flask
from app.models import User, Scholarship, Application

from app.extensions import db, login_manager

from app.routes.auth_routes import auth_bp
from app.routes.student_routes import student_bp
from app.routes.reviewer_routes import reviewer_bp
from app.routes.committee_routes import committee_bp
from app.routes.admin_routes import admin_bp


def create_app():
    
    app = Flask(__name__, template_folder='app/templates')
    app.config['SECRET_KEY'] = 'digital-system'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scholarship.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    db.init_app(app)
    login_manager.init_app(app)
   

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

  
    app.register_blueprint(auth_bp, url_prefix='/auth')

    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(reviewer_bp, url_prefix='/reviewer')
    app.register_blueprint(committee_bp, url_prefix='/committee')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ----------------------
    # Create database tables
    # ----------------------
    with app.app_context():
        db.create_all()

    # ----------------------
    # Home route
    # ----------------------
    @app.route('/')
    def home():
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == 'student':
                return '<script>window.location.href="/student/dashboard"</script>'
            elif current_user.role == 'reviewer':
                return '<script>window.location.href="/reviewer/dashboard"</script>'
            elif current_user.role == 'committee':
                return '<script>window.location.href="/committee/dashboard"</script>'
            elif current_user.role == 'admin':
                return '<script>window.location.href="/admin/dashboard"</script>'
        return '<script>window.location.href="/auth/login"</script>'

    return app

# ----------------------
# Run the app
# ----------------------
if __name__ == "__main__":
    app = create_app()  # create the app first
    with app.app_context():
        from app.models import Scholarship
        from datetime import datetime
        from app.extensions import db

        # --------------------------
        # Seed scholarships with JSON eligibility
        # --------------------------
        s1 = Scholarship(
            title="MMU PRESIDENT’S Scholarship",
            description="Awarded to high-achieving and well-rounded students with outstanding academic results.",
            application_deadline=datetime(2026, 3, 31),
            eligibility_criteria={
                "min_cgpa": 3.5,
                "max_income": 5000,
                "excluded_programmes": ["Law"]
            }
        )

        s2 = Scholarship(
            title="MMU Excellence Scholarship",
            description="Merit-based scholarship for excellent academic achievers.",
            application_deadline=datetime(2026, 4, 15),
            eligibility_criteria={
                "min_cgpa": 3.75,
                "max_income": 10000,
                "excluded_programmes": []
            }
        )

        s3 = Scholarship(
            title="B40 Assistance Scholarship",
            description="Financial aid for students from B40 households.",
            application_deadline=datetime(2026, 5, 15),
            eligibility_criteria={
                "min_cgpa": 3.0,
                "max_income": 4000,
                "excluded_programmes": []
            }
        )

        s4 = Scholarship(
            title="Sports Excellence Scholarship",
            description="For students representing state or national sports teams.",
            application_deadline=datetime(2026, 6, 30),
            eligibility_criteria={
                "min_cgpa": 3.0,
                "max_income": 10000,
                "required_criteria": ["State/National athlete", "Letter from Sports Authority", "Active participation required"],
                "excluded_programmes": []
            }
        )

        s5 = Scholarship(
            title="Leadership Scholarship",
            description="For students with strong leadership and extracurricular involvement.",
            application_deadline=datetime(2026, 7, 15),
            eligibility_criteria={
                "min_cgpa": 3.2,
                "max_income": 10000,
                "required_criteria": ["Student leadership position", "Recommendation letter required", "Active campus involvement"],
                "excluded_programmes": []
            }
        )

        s6 = Scholarship(
            title="Need-Based Financial Aid",
            description="Financial support for students facing economic hardship.",
            application_deadline=datetime(2026, 8, 31),
            eligibility_criteria={
                "min_cgpa": 2.75,
                "max_income": 4000,
                "required_criteria": ["Proof of financial difficulty", "Subject to annual review"],
                "excluded_programmes": []
            }
        )

        # Clear existing scholarships and add new ones
        Scholarship.query.delete()
        db.session.add_all([s1, s2, s3, s4, s5, s6])
        db.session.commit()

    app.run(debug=True)

 

