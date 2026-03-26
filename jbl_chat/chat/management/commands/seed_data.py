from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from chat.models import Message


class Command(BaseCommand):
    help = "Seeds the database with dummy users and messages"

    def handle(self, *args, **options):
        # Create users
        users_data = [
            ("alice", "alice@example.com", "password123"),
            ("bob", "bob@example.com", "password123"),
            ("charlie", "charlie@example.com", "password123"),
            ("diana", "diana@example.com", "password123"),
        ]

        created_users = []
        for username, email, password in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"Created user: {username}")
            else:
                self.stdout.write(f"User already exists: {username}")
            created_users.append(user)

        alice, bob, charlie, diana = created_users

        # Create some sample messages
        sample_messages = [
            (alice, bob, "Hey Bob, how are you?", "read"),
            (bob, alice, "Hi Alice! I'm doing great, thanks!", "read"),
            (alice, bob, "Want to grab lunch later?", "delivered"),
            (bob, alice, "Sure, sounds good!", "sent"),
            (alice, charlie, "Charlie, did you finish the report?", "read"),
            (charlie, alice, "Almost done, will send it by EOD.", "sent"),
            (diana, alice, "Alice, we need to discuss the project.", "sent"),
            (bob, charlie, "Hey Charlie!", "sent"),
        ]

        if Message.objects.count() == 0:
            for sender, receiver, content, status in sample_messages:
                Message.objects.create(
                    sender=sender,
                    receiver=receiver,
                    content=content,
                    status=status,
                )
            self.stdout.write("Created sample messages")
        else:
            self.stdout.write("Messages already exist, skipping")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
