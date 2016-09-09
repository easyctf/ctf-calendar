class TestGeneral():
    def test_sanity(self):
        assert "sanity level" > 0

    def test_404(self, client):
        response = client.get("/404")
        assert response.status_code == 404
