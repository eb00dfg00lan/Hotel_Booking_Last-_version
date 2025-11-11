from django import forms
from .models import Booking, Hotel, Room
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests']

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'description']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hotel', 'title', 'price', 'capacity']

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
