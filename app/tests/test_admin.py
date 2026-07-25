import pytest
from django.test import Client as DjangoClient


@pytest.mark.django_db
def test_django_admin_login_page():
    client = DjangoClient()
    resp = client.get("/admin/login/")
    assert resp.status_code == 200
