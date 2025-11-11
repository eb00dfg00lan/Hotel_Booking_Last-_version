from django.contrib import admin
from .models import Hotel, Room, Booking

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'partner', 'created_at')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'hotel', 'price', 'capacity')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'check_in', 'check_out', 'status', 'created_at')
