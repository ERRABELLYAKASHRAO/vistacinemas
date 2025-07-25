from django.core.management.base import BaseCommand
from booking.models import Showtime

class Command(BaseCommand):
    help = 'Delete all existing showtimes'

    def handle(self, *args, **kwargs):
        count, _ = Showtime.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} showtimes."))
