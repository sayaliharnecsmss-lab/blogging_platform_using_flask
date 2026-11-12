import os
from pathlib import Path

import click
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import select

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

DEFAULT_CATEGORIES = (
    "Technology",
    "Education",
    "Lifestyle",
    "Travel",
    "Food",
    "Health",
    "Other",
)


def create_app(test_config=None):
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
        instance_relative_config=True,
    )
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-this-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///blog.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from blog import models
    from blog.auth import auth_bp
    from blog.posts import posts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    def add_default_categories():
        db.create_all()
        for name in DEFAULT_CATEGORIES:
            category = db.session.scalar(
                select(models.Category).where(models.Category.name == name)
            )
            if category is None:
                db.session.add(models.Category(name=name))
        db.session.commit()

    @app.cli.command("init-db")
    def init_db_command():
        """Create the database tables and built-in categories."""
        add_default_categories()
        click.echo("Database and default categories are ready.")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        """Create a local demo account and sample posts for learning."""
        from werkzeug.security import generate_password_hash

        add_default_categories()
        email = "demo@example.com"
        user = db.session.scalar(
            select(models.User).where(models.User.email == email)
        )
        if user is None:
            user = models.User(
                name="Demo Writer",
                email=email,
                password_hash=generate_password_hash("Demo1234!"),
            )
            db.session.add(user)
            db.session.flush()

        if not user.posts:
            technology = db.session.scalar(
                select(models.Category).where(models.Category.name == "Technology")
            )
            education = db.session.scalar(
                select(models.Category).where(models.Category.name == "Education")
            )
            db.session.add_all(
                [
                    models.Post(
                        title="Welcome to the blog",
                        body=(
                            "This is your first sample post. Explore the dashboard "
                            "to edit it, write a new story, or leave a comment."
                        ),
                        author=user,
                        category=technology,
                    ),
                    models.Post(
                        title="Learning one step at a time",
                        body=(
                            "A good project is built by trying small ideas, "
                            "testing them, and improving them."
                        ),
                        author=user,
                        category=education,
                    ),
                ]
            )
        db.session.commit()
        click.echo("Demo account ready: demo@example.com / Demo1234!")
        click.echo("Use this account only for local learning.")

    with app.app_context():
        add_default_categories()

    return app
