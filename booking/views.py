from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Movie, Seat, Booking
from django.contrib.auth.models import User
from django.conf import settings
import razorpay
import qrcode
from io import BytesIO
import base64
from decimal import Decimal

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'booking/movie_list.html', {'movies': movies})


@csrf_exempt
def select_seats(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    seats = Seat.objects.filter(movie=movie)

    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('selected_seats')
        if not selected_seat_ids:
            return render(request, 'booking/select_seats.html', {
                'movie': movie,
                'seats': seats,
                'error': "Please select at least one seat."
            })
        return redirect('payment', movie_id=movie.id)  # use hidden input to carry selected_seat_ids

    return render(request, 'booking/select_seats.html', {'movie': movie, 'seats': seats})

@csrf_exempt
def payment(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('selected_seats')
        if not selected_seat_ids:
            return redirect('select_seats', movie_id=movie.id)

        seats = Seat.objects.filter(id__in=selected_seat_ids)

        # ✅ Correct price calculation
        seat_prices = {'VIP': 300, 'Premium': 200, 'Gold': 100}
        total_price = sum([seat_prices.get(seat.seat_type, 0) for seat in seats])
        total_paise = int(total_price * 100)

        # 🔐 Create Razorpay order
        razorpay_order = razorpay_client.order.create(dict(
            amount=total_paise,
            currency='INR',
            payment_capture='1'
        ))

        # 💾 Temporarily save booking
        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            movie=movie,
            total_price=total_price,
            razorpay_order_id=razorpay_order['id']
        )
        booking.seats.set(seats)

        return render(request, 'booking/payment.html', {
            'movie': movie,
            'seats': seats,
            'total_price': total_price,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'booking': booking
        })

    return redirect('payment', movie_id=movie.id)


@csrf_exempt
def payment_success(request):
    print("🔁 payment_success called")

    razorpay_order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')

    if not razorpay_order_id:
        print("❌ Missing order_id")
        return redirect('payment_failed')

    try:
        booking = Booking.objects.get(razorpay_order_id=razorpay_order_id)
    except Booking.DoesNotExist:
        print(f"❌ Booking not found for order_id: {razorpay_order_id}")
        return redirect('payment_failed')

    # Success log
    print(f"✅ Payment successful for Order: {razorpay_order_id} | Payment ID: {payment_id}")

    movie = booking.movie
    selected_seats = booking.seats.all()
    total_price = booking.total_price

    qr_data = f"Movie: {movie.title}\nSeats: {', '.join(seat.seat_number for seat in selected_seats)}\nAmount: ₹{total_price}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'booking/payment_success.html', {
        'booking': booking,
        'movie': movie,
        'seats': selected_seats,
        'qr_code': qr_base64
    })


@csrf_exempt
def payment_failed(request):
    return render(request, 'booking/payment_failed.html', {
        'error': 'Session expired or invalid transaction. Please try booking again.'
    })


@csrf_exempt
def book_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    seats = Seat.objects.filter(movie=movie, is_booked=False)
    return render(request, 'booking/book_movie.html', {'movie': movie, 'seats': seats})



