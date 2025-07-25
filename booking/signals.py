from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movie, Showtime, Seat
from datetime import datetime, timedelta, time as time_obj
from django.utils.timezone import now

@receiver(post_save, sender=Movie)
def create_showtimes_for_new_movie(sender, instance, created, **kwargs):
    if created:
        today = now().date()

        # 3 screens
        screens = ['1', '2', '3']

        # Showtimes every 3 hours from 6 AM to 9 PM
        showtimes = [
            time_obj(6, 0),
            time_obj(9, 0),
            time_obj(12, 0),
            time_obj(15, 0),
            time_obj(18, 0),
            time_obj(21, 0),
        ]

        for i in range(7):  # For next 7 days
            date = today + timedelta(days=i)
            for screen in screens:
                for stime in showtimes:
                    show = Showtime.objects.create(
                        movie=instance,
                        date=date,
                        time=stime,
                        screen_number=screen
                    )
                    # Create 50 seats for each show
                    for seat_num in range(1, 51):
                        Seat.objects.create(
                            showtime=show,
                            seat_number=f"S{seat_num}",
                            is_booked=False
                        )
