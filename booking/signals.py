from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movie, Seat

@receiver(post_save, sender=Movie)
def create_seats_for_movie(sender, instance, created, **kwargs):
    if created:
        seat_types = [
            ("Gold", 50),
            ("Premium", 30),
            ("VIP", 20)
        ]
        for seat_type, count in seat_types:
            for i in range(1, count + 1):
                Seat.objects.create(
                    movie=instance,
                    seat_number=f"{seat_type[0]}{i}",
                    seat_type=seat_type
                )