from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms import ChangePasswordForm, ForgotPasswordForm, LoginForm, ProfileForm, RegisterForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard" if current_user.is_admin else "main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            session.permanent = True
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            if user.is_admin:
                return redirect(next_page or url_for("admin.dashboard"))
            return redirect(next_page or url_for("main.index"))
        flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("auth.login"))

        user = User(
            name=form.name.data.strip(),
            email=email,
            phone=form.phone.data,
            address=form.address.data,
            role="customer",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            flash(
                "If an account exists with that email, a password reset link has been sent.",
                "info",
            )
        else:
            flash(
                "If an account exists with that email, a password reset link has been sent.",
                "info",
            )
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", form=form)


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if request.method == "POST":
        submit_action = request.form.get("submit")
        if submit_action == "Update Profile" and profile_form.validate():
            email = profile_form.email.data.lower().strip()
            existing = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing:
                flash("Email is already in use.", "danger")
            else:
                current_user.name = profile_form.name.data.strip()
                current_user.email = email
                current_user.phone = profile_form.phone.data
                current_user.address = profile_form.address.data
                db.session.commit()
                flash("Profile updated successfully.", "success")
                return redirect(url_for("auth.profile"))
        elif submit_action == "Change Password" and password_form.validate():
            if not current_user.check_password(password_form.current_password.data):
                flash("Current password is incorrect.", "danger")
            else:
                current_user.set_password(password_form.new_password.data)
                db.session.commit()
                flash("Password changed successfully.", "success")
                return redirect(url_for("auth.profile"))

    return render_template("profile.html", profile_form=profile_form, password_form=password_form)
