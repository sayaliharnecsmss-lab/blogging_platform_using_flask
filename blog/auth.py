from urllib.parse import urljoin, urlsplit

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import select

from blog import db
from blog.models import User

auth_bp = Blueprint("auth", __name__)


def is_safe_redirect_target(target):
    if not target:
        return False
    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(urljoin(request.host_url, target))
    return test_url.scheme in {"http", "https"} and ref_url.netloc == test_url.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("posts.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or len(name) > 80:
            flash("Please enter a name of 1–80 characters.", "danger")
        else:
            try:
                email = validate_email(
                    email, check_deliverability=False
                ).normalized
            except EmailNotValidError:
                flash("Please enter a valid email address.", "danger")
            else:
                if db.session.scalar(select(User).where(User.email == email)):
                    flash("An account with that email already exists.", "danger")
                elif len(password) < 8:
                    flash("Your password must be at least 8 characters.", "danger")
                elif password != confirm:
                    flash("The passwords do not match.", "danger")
                else:
                    user = User(name=name, email=email)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                    login_user(user)
                    flash("Welcome! Your account has been created.", "success")
                    return redirect(url_for("posts.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("posts.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.session.scalar(select(User).where(User.email == email))
        if user is None or not user.check_password(password):
            flash("Email or password is incorrect.", "danger")
        else:
            login_user(user)
            flash("You are now signed in.", "success")
            destination = request.args.get("next")
            if destination and is_safe_redirect_target(destination):
                return redirect(destination)
            return redirect(url_for("posts.dashboard"))

    return render_template("login.html")


@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been signed out.", "info")
    return redirect(url_for("posts.index"))
