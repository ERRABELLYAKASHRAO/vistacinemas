from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.select_seats, name='select_seats'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment/<int:movie_id>/', views.payment, name='payment'),
    path('book/<int:movie_id>/', views.book_movie, name='book_movie'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
]
