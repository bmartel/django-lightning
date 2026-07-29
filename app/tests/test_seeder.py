import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()


@pytest.mark.django_db
def test_seed_db_command():
    initial_count = User.objects.count()
    call_command("seed_db", users=10)
    new_count = User.objects.count()
    assert new_count == initial_count + 10

    # Sequential seeding run adds another 10 unique synthetic records
    call_command("seed_db", users=10)
    assert User.objects.count() == new_count + 10

