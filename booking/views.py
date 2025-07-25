from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Movie, Seat, Booking, Showtime, ShowSeat
from django.contrib.auth.models import User
from django.conf import settings
import razorpay
import qrcode
from io import BytesIO
import base64
from collections import defaultdict
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
import json


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'booking/movie_list.html', {'movies': movies})

def select_showtime(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    today = now().date()
    dates = [today + timedelta(days=i) for i in range(7)]

    selected_date_str = request.GET.get("date")
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date() if selected_date_str else today
    except ValueError:
        selected_date = today

    showtimes = Showtime.objects.filter(movie=movie, date=selected_date).order_by('screen_number', 'time')

    showtimes_by_screen = defaultdict(list)
    seen = defaultdict(set)
    for show in showtimes:
        if show.time not in seen[show.screen_number]:
            showtimes_by_screen[show.screen_number].append(show)
            seen[show.screen_number].add(show.time)

    return render(request, 'booking/select_showtime.html', {
        'movie': movie,
        'dates': dates,
        'selected_date': selected_date,
        'showtimes_by_screen': dict(showtimes_by_screen),
    })
@csrf_exempt
def select_seats(request, movie_id, showtime_id):
    movie = get_object_or_404(Movie, id=movie_id)
    showtime = get_object_or_404(Showtime, id=showtime_id)

    if showtime.movie.id != movie.id:
        return render(request, '404.html', status=404)

    seats = Seat.objects.filter(screen_number=showtime.screen_number)
    booked_seat_ids = ShowSeat.objects.filter(showtime=showtime, is_booked=True).values_list('seat_id', flat=True)

    seat_prices = {
        "VIP": 300,
        "Premium": 200,
        "Gold": 100
    }

    seat_categories = ['VIP', 'Premium', 'Gold']  # Make sure this is always available

    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('selected_seats')

        if not selected_seat_ids:
            return render(request, 'booking/select_seats.html', {
                'movie': movie,
                'showtime': showtime,
                'seats': seats,
                'booked_seat_ids': booked_seat_ids,
                'seat_prices_json': mark_safe(json.dumps(seat_prices)),
                'seat_categories': seat_categories,
                'error': "Please select at least one seat."
            })

        request.session['selected_seat_ids'] = selected_seat_ids
        request.session['showtime_id'] = showtime.id

        return redirect('payment', movie_id=movie.id)

    return render(request, 'booking/select_seats.html', {
        'movie': movie,
        'showtime': showtime,
        'seats': seats,
        'booked_seat_ids': booked_seat_ids,
        'seat_prices_json': mark_safe(json.dumps(seat_prices)),
        'seat_categories': seat_categories,  # ✅ include this for template rendering
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Movie, Showtime, Seat, Booking
import razorpay

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@csrf_exempt
def payment(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    selected_seat_ids = request.session.get('selected_seat_ids')
    showtime_id = request.session.get('showtime_id')

    if not selected_seat_ids or not showtime_id:
        return redirect('select_showtime', movie_id=movie_id)

    showtime = get_object_or_404(Showtime, id=showtime_id)
    seats = Seat.objects.filter(id__in=selected_seat_ids)

    # You can update this dictionary based on your actual seat types
    seat_prices = {
        'VIP': 300,
        'Premium': 200,
        'Gold': 100
    }

    # Calculate total
    total_price = sum([seat_prices.get(seat.seat_type, 0) for seat in seats])
    total_paise = int(total_price * 100)

    # Create Razorpay order
    razorpay_order = razorpay_client.order.create(dict(
        amount=total_paise,
        currency='INR',
        payment_capture='1'
    ))

    # Create booking instance
    booking = Booking.objects.create(
        user=request.user if request.user.is_authenticated else None,
        movie=movie,
        showtime=showtime,
        total_price=total_price,
        razorpay_order_id=razorpay_order['id']
    )
    booking.seats.set(seats)

    return render(request, 'booking/payment.html', {
        'movie': movie,
        'showtime': showtime,
        'seats': seats,
        'total_price': total_price,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
        'booking': booking
    })

@csrf_exempt
def payment_success(request):
    razorpay_order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')

    if not razorpay_order_id:
        return redirect('payment_failed')

    try:
        booking = Booking.objects.get(razorpay_order_id=razorpay_order_id)
    except Booking.DoesNotExist:
        return redirect('payment_failed')

    selected_seats = booking.seats.all()
    showtime = booking.showtime

    # Mark seats booked in ShowSeat
    for seat in selected_seats:
        show_seat, created = ShowSeat.objects.get_or_create(showtime=showtime, seat=seat)
        show_seat.is_booked = True
        show_seat.save()

    qr_data = f"Movie: {booking.movie.title}\nTime: {showtime.time}\nSeats: {', '.join(seat.seat_number for seat in selected_seats)}\nAmount: ₹{booking.total_price}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'booking/payment_success.html', {
        'booking': booking,
        'movie': booking.movie,
        'seats': selected_seats,
        'qr_code': qr_base64
    })

@csrf_exempt
def payment_failed(request):
    return render(request, 'booking/payment_failed.html', {
        'error': 'Session expired or invalid transaction. Please try booking again.'
    })
