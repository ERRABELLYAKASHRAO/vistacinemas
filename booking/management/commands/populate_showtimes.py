from django.core.management.base import BaseCommand
from booking.models import Movie, Showtime
from datetime import timedelta, time as dtime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate showtimes every 3 hours from 6 AM to 9 PM for all movies for today + next 6 days'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        # Optional: Clear existing showtimes
        Showtime.objects.all().delete()

        # Showtimes every 3 hours: 6 AM, 9 AM, 12 PM, 3 PM, 6 PM, 9 PM
        show_times = [dtime(hour=h) for h in range(6, 22, 3)]

        for day_offset in range(7):  # 0 to 6 -> 7 days
            show_date = today + timedelta(days=day_offset)
            for movie in Movie.objects.all():
                for show_time in show_times:
                    Showtime.objects.create(
                        movie=movie,
                        date=show_date,
                        time=show_time,
                        screen_number=1
                    )

        self.stdout.write(self.style.SUCCESS("✅ Showtimes created for 7 days with 3-hour intervals."))
