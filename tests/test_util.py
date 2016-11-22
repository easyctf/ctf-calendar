from flask_login import login_user, logout_user
from werkzeug.exceptions import Forbidden

import util
from models import User
from test_general import USER, ADMIN, admin_user, regular_user


class TestUtil:
    def test_admin_required_pass(self, db):
        db.session.add(admin_user)
        db.session.commit()

        @util.admin_required
        def foo():
            return "bar"

        login_user(User.get_by_identifier(ADMIN["username"]))
        bar = foo()
        assert bar == "bar"

    def test_admin_required_fail(self, client, db):
        logout_user()
        db.session.add(regular_user)
        db.session.commit()

        @util.admin_required
        def foo():
            return "bar"

        bar = foo()
        assert hasattr(bar, "status_code") and bar.status_code == 302

        login_user(User.get_by_identifier(USER["username"]))
        try:
            foo()
        except Exception as e:
            assert type(e) is Forbidden

    def test_iso_format(self):
        formatted_time = util.isoformat(0)
        assert formatted_time == "1970-01-01T00:00:00Z"

    def test_generate_string(self):
        generated_string = util.generate_string()
        assert len(generated_string) == 32 and all([c in "0123456789abcdef" for c in generated_string])

    def test_verify_password(self):
        correct_password = "pa$$w0rd"
        hashed_password = util.hash_password(correct_password)
        assert util.verify_password(correct_password, hashed_password)
