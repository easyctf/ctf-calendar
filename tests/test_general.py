from flask import url_for

from models import User

ADMIN = dict(
    email="admin@easyctf.com",
    username="admin",
    password="password"
)

USER = dict(
    email="team@easyctf.com",
    username="user",
    password="password"
)


class TestGeneral():
    def test_sanity(self, app, client, db):
        assert "sanity level" > 0

    # BASE

    def test_404(self, client):
        response = client.get("/404")
        assert response.status_code == 404

    def test_index(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_about(self, client):
        response = client.get("/about")
        assert response.status_code == 200

    # USER

    def test_user_login_page(self, client):
        response = client.get("/login")
        assert response.status_code == 200

    def test_user_login_form(self, client, db):
        admin_user = User(admin=True, **ADMIN)
        db.session.add(admin_user)
        db.session.commit()
        response = client.post("/login", data=dict(identifier=ADMIN["username"], password=ADMIN["password"]))
        assert response.status_code == 302
        assert response.headers["LOCATION"] == url_for("users.profile", _external=True)

    def test_user_register_page(self, client):
        response = client.get("/register")
        assert response.status_code == 200

    def test_user_register_form(self, client):
        response = client.post("/register", data=USER)
        assert response.status_code == 302
        assert response.headers["LOCATION"] == url_for("users.profile", _external=True)

    def test_user_logout(self, client):
        response = client.get("/logout")
        assert response.status_code == 302
        assert response.headers["LOCATION"] == url_for("base.index", _external=True)
