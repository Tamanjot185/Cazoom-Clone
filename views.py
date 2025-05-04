from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Car, Booking
from .forms import BookingForm
import requests
from django.http import JsonResponse, HttpResponseNotAllowed



def home(request):
    return render(request, 'main/homepage.html')

def hyundai(request):
    return render(request, 'main/hyundai.html')  

def xuv(request):
    return render(request, 'main/xuv.html')  

def honda(request):
    return render(request, 'main/honda.html')  



def suv(request):
    return render(request, 'main/suv.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def book_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car
            booking.save()
            messages.success(request, 'booking successfull, proceeding to pay!')
            return redirect('initiate_payment', car_id=car.id)
    else:
        form = BookingForm()
    return render(request, 'registration/book_car.html', {'form': form, 'car': car})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'registration/my_bookings.html', {'bookings': bookings})


@login_required
def initiate_payment(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Get all bookings for the user and car
    bookings = Booking.objects.filter(car_id=car_id, user=request.user)

    if not bookings:
        # If no bookings found, handle this error
        return redirect('my_bookings')

    if request.method == 'POST':
        amount = car.price_per_hour

        for booking in bookings:
            user_id = booking.user.id

            response = requests.post('http://127.0.0.1:5000/pay', json={
                'amount': str(amount),
                'user_id': user_id
            })

            result = response.json()

            if result['status'] == 'success':
                messages.success(request, f'Payment successful for booking {booking.id}')
            else:
                messages.error(request, f'Payment failed for booking {booking.id}')

        return redirect('my_bookings')

    return render(request, 'registration/payment.html', {'car': car})

def error(request):
    return render(request, 'registration/error.html')
