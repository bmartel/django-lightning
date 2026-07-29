import pytest
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

from app.routes.article import register_article_routes


@pytest.fixture
def client():
    api = BoltAPI()
    register_article_routes(api)
    return TestClient(api)


def test_list_articles(client):
    resp = client.get("/api/articles")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
