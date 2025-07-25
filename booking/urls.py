from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/select_showtime/', views.select_showtime, name='select_showtime'),
    path('movie/<int:movie_id>/show/<int:showtime_id>/select_seats/', views.select_seats, name='select_seats'),
    path('movie/<int:movie_id>/payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
]
