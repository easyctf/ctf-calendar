from flask import url_for

from test_general import USER


class TestEvents:
    def test_events_create_page(self, client, db):
        response = client.post("/register", data=USER)
        print response.data
        response = client.get(url_for("events.create"))
        assert response.status_code == 200
