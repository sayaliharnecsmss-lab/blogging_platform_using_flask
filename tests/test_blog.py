from blog import db
from blog.models import Category, Comment, Post, User


def create_post(client):
    with client.application.app_context():
        category_id = db.session.query(Category).filter_by(name="Technology").one().id
    response = client.post(
        "/posts/new",
        data={
            "title": "A first story",
            "body": "Hello, curious readers.",
            "category_id": category_id,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with client.application.app_context():
        return db.session.query(Post).filter_by(title="A first story").one().id


def test_registration_hashes_password_and_login_works(client):
    response = client.post(
        "/register",
        data={
            "name": "New Writer",
            "email": "new@example.com",
            "password": "SecretPass123",
            "confirm_password": "SecretPass123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome back" in response.data
    with client.application.app_context():
        user = db.session.query(User).filter_by(email="new@example.com").one()
        assert user.password_hash != "SecretPass123"
        assert user.check_password("SecretPass123")

    client.post("/logout", follow_redirects=True)
    response = client.post(
        "/login",
        data={"email": "new@example.com", "password": "SecretPass123"},
        follow_redirects=True,
    )
    assert b"You are now signed in." in response.data
    assert response.status_code == 200


def test_posts_can_be_created_searched_filtered_and_commented(client, registered_user):
    post_id = create_post(client)
    assert b"A first story" in client.get("/").data
    assert b"A first story" in client.get("/?q=curious").data

    with client.application.app_context():
        category_id = db.session.query(Category).filter_by(name="Technology").one().id
    assert b"A first story" in client.get(f"/?category={category_id}").data

    response = client.post(
        f"/posts/{post_id}/comments",
        data={"body": "A thoughtful note."},
        follow_redirects=True,
    )
    assert b"A thoughtful note." in response.data
    with client.application.app_context():
        assert db.session.query(Comment).count() == 1


def test_only_author_can_edit_or_delete_posts(client, registered_user):
    post_id = create_post(client)
    client.post("/logout")
    client.post(
        "/register",
        data={
            "name": "Another Writer",
            "email": "other@example.com",
            "password": "AnotherPass123",
            "confirm_password": "AnotherPass123",
        },
    )

    assert client.get(f"/posts/{post_id}/edit").status_code == 403
    assert client.post(f"/posts/{post_id}/delete").status_code == 403

    client.post("/logout")
    client.post(
        "/login",
        data={"email": registered_user["email"], "password": registered_user["password"]},
    )
    response = client.post(
        f"/posts/{post_id}/edit",
        data={
            "title": "Updated story",
            "body": "Updated content.",
            "category_id": "1",
        },
        follow_redirects=True,
    )
    assert b"Updated story" in response.data
    response = client.post(f"/posts/{post_id}/delete", follow_redirects=True)
    assert b"Updated story" not in response.data


def test_login_rejects_external_redirect(client, registered_user):
    client.post("/logout")
    response = client.post(
        "/login?next=https://example.com",
        data=registered_user,
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
