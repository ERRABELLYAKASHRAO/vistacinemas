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


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    screen_number = models.IntegerField()

    def __str__(self):
        return f"{self.movie.title} - {self.date} {self.time}"


class Seat(models.Model):
    SEAT_TYPES = (
        ('VIP', 'VIP'),
        ('Premium', 'Premium'),
        ('Gold', 'Gold'),
    )

    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPES)
    screen_number = models.IntegerField(null=True, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.seat_number} ({self.seat_type})"


class Booking(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    booking_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} booked {self.movie.title} at {self.showtime.time}"


class ShowSeat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('showtime', 'seat')  # Ensure seat is unique per showtime

    def __str__(self):
        return f"{self.seat.seat_number} - {self.showtime} - {'Booked' if self.is_booked else 'Available'}"
