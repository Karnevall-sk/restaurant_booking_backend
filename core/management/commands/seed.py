from django.core.management.base import BaseCommand
from core.seeds.seed_all import seed_all


class Command(BaseCommand):
    help = "Seed database with initial data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        seed_all()

        self.stdout.write(self.style.SUCCESS("Done!"))