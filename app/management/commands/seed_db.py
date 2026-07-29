"""Django Management Command to seed synthetic data for local development and stress testing.

Usage:
    uv run manage.py seed_db --users 100
"""

import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Seed synthetic users and sample data for development and stress testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=50,
            help="Number of synthetic users to seed (default: 50)",
        )

    def handle(self, *args, **options):
        count = options["users"]
        if count <= 0:
            self.stdout.write(self.style.WARNING("No users to seed."))
            return

        self.stdout.write(f"Seeding {count} synthetic users...")
        start_time = time.perf_counter()

        import uuid

        run_id = uuid.uuid4().hex[:6]
        existing_usernames = set(User.objects.values_list("username", flat=True))
        users_to_create = []

        for i in range(1, count + 1):
            username = f"seed_{run_id}_{i}"
            if username in existing_usernames:
                continue

            user = User(
                username=username,
                email=f"{username}@example.com",
                bio=f"Synthetic test user profile #{i}",
                avatar_url=f"https://api.dicebear.com/7.x/avatars/svg?seed={username}",
            )

            user.set_password("Password123!")
            users_to_create.append(user)

            if len(users_to_create) >= 500:
                User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                users_to_create.clear()

        if users_to_create:
            User.objects.bulk_create(users_to_create, ignore_conflicts=True)

        elapsed = time.perf_counter() - start_time
        total_now = User.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"  [OK] Successfully seeded users in {elapsed:.2f}s. "
                f"Total users in DB: {total_now}"
            )
        )
