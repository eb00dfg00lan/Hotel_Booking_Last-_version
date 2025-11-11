from django.urls import path
from . import views

app_name = 'hotel'
urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('search/', views.search_view, name='search'),
    path('booking/', views.booking_view, name='booking'),
    path('booking/guest/', views.booking_guest_view, name='booking_guest'),
    path('booking/partner/', views.booking_partner_view, name='booking_partner'),
    path('my_hotels/', views.my_hotels_view, name='my_hotels'),
    path('add_hotel/', views.add_hotel_view, name='add_hotel'),
    path('admin_page/', views.admin_view, name='admin_page'),
    path('set_page/<str:page>/', views.set_page, name='set_page'),
]
