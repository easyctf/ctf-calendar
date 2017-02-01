from flask import url_for

import filters
from models import User

ADMIN = dict(
    email="admin@easyctf.com",
    identifier="admin",
    username="admin",
    password="password"
)
admin_user = User(admin=True, email=ADMIN["email"], username=ADMIN["username"], password=ADMIN["password"])

USER = dict(
    email="team@easyctf.com",
    identifier="user",
    username="user",
    password="password"
)
regular_user = User(email=USER["email"], username=USER["username"], password=USER["password"])


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

    # FILTERS?

    def test_formatted_duration(self):
        assert filters.formatted_duration(0.1, "second") == "<1 s"
        assert filters.formatted_duration(10, "day") == "1 w 3 d"
        assert filters.formatted_duration(100, "hour") == "4 d 4 h"

    # USER

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

    def test_user_login_page(self, client):
        response = client.get("/login")
        assert response.status_code == 200

    def test_user_login_form(self, client, db):
        response = client.post("/login", data=USER)
        assert response.status_code == 302
        assert response.headers["LOCATION"] == url_for("users.profile", _external=True)
