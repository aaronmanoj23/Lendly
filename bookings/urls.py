from django.urls import path

from . import views

urlpatterns = [
    path("request/<int:listing_id>/", views.request_booking, name="request_booking"),
    path("<int:pk>/", views.booking_detail, name="booking_detail"),
    path("<int:pk>/approve/", views.approve_booking, name="approve_booking"),
    path("<int:pk>/deny/", views.deny_booking, name="deny_booking"),
    path("<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),
]
