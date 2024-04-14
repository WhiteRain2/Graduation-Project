from django.core.management.base import BaseCommand
from demo.ml_utils.calculation import calculate_and_save_similarities


class Command(BaseCommand):
    help = 'Calculates and stores student and course similarities in the database.'

    def handle(self, *args, **options):
        calculate_and_save_similarities()
        self.stdout.write(self.style.SUCCESS('Successfully calculated and saved similarities.'))