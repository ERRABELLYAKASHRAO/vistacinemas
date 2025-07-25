from django.contrib import admin
from .models import Movie, Seat, Booking, Showtime, ShowSeat
from datetime import timedelta, time

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'screen_number', 'show_time', 'price')

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new or not Showtime.objects.filter(movie=obj).exists():
            start_date = obj.show_time.date()
            screen_number = obj.screen_number

            show_slots = [
                time(6, 0), time(9, 0), time(12, 0),
                time(15, 0), time(18, 0), time(21, 0)
            ]

            for i in range(7):  # Next 7 days from admin's chosen start date
                show_date = start_date + timedelta(days=i)
                for slot in show_slots:
                    st, created = Showtime.objects.get_or_create(
                        movie=obj,
                        date=show_date,
                        time=slot,
                        screen_number=screen_number
                    )

                    # Create ShowSeat objects only if not already created
                    seats = Seat.objects.filter(screen_number=screen_number)
                    for seat in seats:
                        ShowSeat.objects.get_or_create(showtime=st, seat=seat)

# Register other models normally
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(Showtime)
admin.site.register(ShowSeat)
