from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .decorators import require_roles
from .utils import init_db_if_needed
from .forms import BookingForm, RegisterForm, HotelForm
from .models import Hotel

init_db_if_needed()

def topbar_context(request):
    return {
        'current_page': request.session.get('page', 'welcome'),
        'role': request.session.get('role', 'guest'),
        'user_session': request.session.get('user'),
        'django_user': request.user if request.user.is_authenticated else None,
    }

def set_page(request, page):
    request.session['page'] = page
    mapping = {
        'welcome': 'hotel:welcome',
        'login': 'hotel:login',
        'register': 'hotel:register',
        'search': 'hotel:search',
        'booking_guest': 'hotel:booking_guest',
        'booking_partner': 'hotel:booking_partner',
        'my_hotels': 'hotel:my_hotels',
        'booking': 'hotel:booking',
        'add_hotel': 'hotel:add_hotel',
        'admin': 'hotel:admin_page',
    }
    return redirect(mapping.get(page, 'hotel:welcome'))

def welcome_view(request):
    request.session['page'] = 'welcome'
    ctx = topbar_context(request)
    return render(request, 'hotel/welcome.html', ctx)

def login_view(request):
    request.session['page'] = 'login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'guest')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session['role'] = role
            request.session['user'] = username
            return redirect('hotel:welcome')
        else:
            request.session['user'] = username
            request.session['role'] = role
            return redirect('hotel:welcome')
    return render(request, 'hotel/login.html', topbar_context(request))

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('hotel:welcome')

def register_view(request):
    request.session['page'] = 'register'
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['role'] = 'guest'
            request.session['user'] = user.username
            return redirect('hotel:welcome')
    else:
        form = RegisterForm()
    ctx = topbar_context(request)
    ctx['form'] = form
    return render(request, 'hotel/register.html', ctx)

def search_view(request):
    request.session['page'] = 'search'
    q = request.GET.get('q', '')
    hotels = Hotel.objects.all()
    if q:
        hotels = hotels.filter(name__icontains=q)
    ctx = topbar_context(request)
    ctx['hotels'] = hotels
    return render(request, 'hotel/search.html', ctx)

def booking_view(request):
    request.session['page'] = 'Booking'
    ctx = topbar_context(request)
    return render(request, 'hotel/booking.html', ctx)

def booking_guest_view(request):
    request.session['page'] = 'booking_guest'
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            if request.user.is_authenticated:
                b.user = request.user
            b.save()
            return redirect('hotel:welcome')
    else:
        form = BookingForm()
    ctx = topbar_context(request)
    ctx['form'] = form
    return render(request, 'hotel/booking_guest.html', ctx)

@require_roles('partner', 'admin')
def booking_partner_view(request):
    request.session['page'] = 'booking_partner'
    if request.user.is_authenticated:
        hotels = Hotel.objects.filter(partner=request.user)
    else:
        hotels = Hotel.objects.none()
    ctx = topbar_context(request)
    ctx['hotels'] = hotels
    return render(request, 'hotel/booking_partner.html', ctx)

@require_roles('admin')
def admin_view(request):
    request.session['page'] = 'admin'
    ctx = topbar_context(request)
    return render(request, 'hotel/admin.html', ctx)

@require_roles('partner', 'admin')
def my_hotels_view(request):
    request.session['page'] = 'my_hotels'
    if request.user.is_authenticated:
        hotels = Hotel.objects.filter(partner=request.user)
    else:
        hotels = Hotel.objects.none()
    ctx = topbar_context(request)
    ctx['hotels'] = hotels
    return render(request, 'hotel/my_hotels.html', ctx)

@require_roles('partner', 'admin')
def add_hotel_view(request):
    request.session['page'] = 'add_hotel'
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            h = form.save(commit=False)
            if request.user.is_authenticated:
                h.partner = request.user
            h.save()
            return redirect('hotel:my_hotels')
    else:
        form = HotelForm()
    ctx = topbar_context(request)
    ctx['form'] = form
    return render(request, 'hotel/add_hotel.html', ctx)
