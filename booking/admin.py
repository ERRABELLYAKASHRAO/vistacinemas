from django.contrib import admin
from .models import Movie, Seat, Booking

admin.site.register(Movie)
admin.site.register(Seat)
admin.site.register(Booking)

class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'show_time', 'price']


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'screen_number')
