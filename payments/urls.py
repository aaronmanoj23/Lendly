from django.urls import path

from . import views

urlpatterns = [
    path("checkout/<int:booking_id>/", views.checkout, name="checkout"),
    path(
        "checkout/<int:booking_id>/session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("success/<int:booking_id>/", views.payment_success, name="payment_success"),
    path("cancel/<int:booking_id>/", views.payment_cancel, name="payment_cancel"),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
]
