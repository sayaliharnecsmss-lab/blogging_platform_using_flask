from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, select

from blog import db
from blog.models import Category, Comment, Post, User

posts_bp = Blueprint("posts", __name__)


def get_post_or_404(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    return post


def post_form_data():
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    category_id = request.form.get("category_id", type=int)
    category = db.session.get(Category, category_id) if category_id else None
    return title, body, category


@posts_bp.get("/")
def index():
    statement = select(Post).order_by(Post.created_at.desc())
    category_id = request.args.get("category", type=int)
    query = request.args.get("q", "").strip()

    if category_id:
        statement = statement.where(Post.category_id == category_id)
    if query:
        search = f"%{query}%"
        statement = statement.join(Post.author).where(
            or_(Post.title.ilike(search), Post.body.ilike(search), User.name.ilike(search))
        )

    posts = db.session.scalars(statement).all()
    categories = db.session.scalars(select(Category).order_by(Category.name)).all()
    return render_template(
        "index.html",
        posts=posts,
        categories=categories,
        selected_category=category_id,
        query=query,
    )


@posts_bp.get("/dashboard")
@login_required
def dashboard():
    posts = db.session.scalars(
        select(Post)
        .where(Post.author_id == current_user.id)
        .order_by(Post.created_at.desc())
    ).all()
    return render_template("dashboard.html", posts=posts)


@posts_bp.route("/posts/new", methods=["GET", "POST"])
@login_required
def create_post():
    categories = db.session.scalars(select(Category).order_by(Category.name)).all()
    if request.method == "POST":
        title, body, category = post_form_data()
        if not title or len(title) > 160:
            flash("Please enter a title of 1–160 characters.", "danger")
        elif not body:
            flash("Please write some content for your post.", "danger")
        elif category is None:
            flash("Please select a category.", "danger")
        else:
            post = Post(title=title, body=body, author=current_user, category=category)
            db.session.add(post)
            db.session.commit()
            flash("Your post has been published.", "success")
            return redirect(url_for("posts.dashboard"))

    return render_template("post_form.html", post=None, categories=categories)


@posts_bp.get("/posts/<int:post_id>")
def detail(post_id):
    return render_template("post_detail.html", post=get_post_or_404(post_id))


@posts_bp.post("/posts/<int:post_id>/comments")
@login_required
def add_comment(post_id):
    post = get_post_or_404(post_id)
    body = request.form.get("body", "").strip()
    if not body or len(body) > 1000:
        flash("A comment must be between 1 and 1000 characters.", "danger")
    else:
        db.session.add(Comment(body=body, author=current_user, post=post))
        db.session.commit()
        flash("Your comment has been added.", "success")
    return redirect(url_for("posts.detail", post_id=post.id) + "#comments")


@posts_bp.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = get_post_or_404(post_id)
    if post.author_id != current_user.id:
        abort(403)

    categories = db.session.scalars(select(Category).order_by(Category.name)).all()
    if request.method == "POST":
        title, body, category = post_form_data()
        if not title or len(title) > 160:
            flash("Please enter a title of 1–160 characters.", "danger")
        elif not body:
            flash("Please write some content for your post.", "danger")
        elif category is None:
            flash("Please select a category.", "danger")
        else:
            post.title = title
            post.body = body
            post.category = category
            db.session.commit()
            flash("Your changes have been saved.", "success")
            return redirect(url_for("posts.detail", post_id=post.id))

    return render_template("post_form.html", post=post, categories=categories)


@posts_bp.post("/posts/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    post = get_post_or_404(post_id)
    if post.author_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted.", "info")
    return redirect(url_for("posts.dashboard"))
