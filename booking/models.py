from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    show_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='movie_images/', null=True, blank=True)
    location = models.CharField(max_length=100, default="Hyderabad")
    screen_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

class Seat(models.Model):
    SEAT_TYPES = (
        ('VIP', 'VIP'),
        ('Premium', 'Premium'),
        ('Gold', 'Gold'),
    )

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPES)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.movie.title} - {self.seat_number} ({self.seat_type})"


class Booking(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 

    def __str__(self):
      username = self.user.username if self.user else "Anonymous"
      return f"{username} booked {self.movie.title}"


from django.apps import AppConfig

class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'

    def ready(self):
        import booking.signals

