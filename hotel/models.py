from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    partner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hotels')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.hotel.name} — {self.title}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking #{self.id} — {self.room} ({self.check_in} → {self.check_out})"
