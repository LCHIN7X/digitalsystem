from flask import Flask
from app.extensions import db, login_manager

# Import blueprints
from app.routes.auth_routes import auth_bp
# You can import other blueprints when ready:
# from app.routes.student_routes import student_bp
# from app.routes.reviewer_routes import reviewer_bp
# from app.routes.committee_routes import committee_bp
# from app.routes.admin_routes import admin_bp

def create_app():
    # Create Flask app
    app = Flask(__name__, template_folder='app/templates')
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scholarship.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # ----------------------
    # User loader for Flask-Login
    # ----------------------
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User  # import inside function to avoid circular imports
        return db.session.get(User, int(user_id))

    # ----------------------
    # Register blueprints
    # ----------------------
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # Uncomment and register other blueprints when ready
    # app.register_blueprint(student_bp, url_prefix='/student')
    # app.register_blueprint(reviewer_bp, url_prefix='/reviewer')
    # app.register_blueprint(committee_bp, url_prefix='/committee')
    # app.register_blueprint(admin_bp, url_prefix='/admin')

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
    app = create_app()
    app.run(debug=True)
