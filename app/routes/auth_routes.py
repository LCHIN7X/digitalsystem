from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required,current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db
from app.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        your_id = request.form.get("your_id")
        role = request.form.get("role")  # <- get selected role
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords do not match.", "error")
            return render_template("register.html", current_user=current_user)

        hashed_password = generate_password_hash(password1, method="scrypt")

        new_user = User(
            email=email,
            username=username,
            your_id=your_id,
            password=hashed_password,
            role=role  # <- save role in database
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account successfully created!", "success")
            return redirect(url_for("auth.login"))
        except IntegrityError:
            db.session.rollback()
            flash("Email or student ID already exists", "error")
    return render_template('auth/register.html', current_user=current_user)


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)

            # Handle "next" redirect after login
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Otherwise redirect based on role
            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'reviewer':
                return redirect(url_for('reviewer.dashboard'))
            elif user.role == 'committee':
                return redirect(url_for('committee.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))

        flash("Invalid credentials", "danger")

    return render_template('auth/login.html')



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('auth.login'))

