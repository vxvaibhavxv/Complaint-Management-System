import random
from faker import Faker
from core.models import User, Complaint, Tag, ComplaintTag
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "A command-line utility to generate fake data for the database"

    def handle(self, *args, **kwargs):
        fake = Faker(["en_IN"])
        Faker.seed(0)
        users = User.objects.filter(isAdmin = False).filter(isSuperuser = False).filter(isManager = False)
        count = random.randint(100, 200)

        for i in range(count):
            user = random.choice(users)
            complaint = Complaint.objects.create(
                title = fake.sentence(),
                complaint = fake.paragraph(nb_sentences = random.randint(3, 50)),
                author = user
            )

            for _ in range(random.randint(2, 30)):
                tagObject = Tag.objects.create(name = fake.word().lower())
                ComplaintTag.objects.create(
                    complaint = complaint,
                    tag = tagObject
                )

            self.stdout.write(self.style.SUCCESS(f"Operation Status --> {((i + 1) / count) * 100}%"))

        self.stdout.write(self.style.SUCCESS(f"Done! Number of complaints created --> {count}"))


