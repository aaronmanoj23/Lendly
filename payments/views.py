import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from bookings.models import Booking

from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(
        Booking, pk=booking_id, renter=request.user, status=Booking.Status.APPROVED
    )
    return render(
        request,
        "payments/checkout.html",
        {"booking": booking, "stripe_public_key": settings.STRIPE_PUBLIC_KEY},
    )


@login_required
@require_POST
def create_checkout_session(request, booking_id):
    booking = get_object_or_404(
        Booking, pk=booking_id, renter=request.user, status=Booking.Status.APPROVED
    )
    success_url = request.build_absolute_uri(
        reverse("payment_success", args=[booking.pk])
    )
    cancel_url = request.build_absolute_uri(
        reverse("payment_cancel", args=[booking.pk])
    )
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": booking.listing.title},
                        "unit_amount": int(booking.total_amount * 100),
                    },
                    "quantity": 1,
                }
            ],
            metadata={"booking_id": booking.pk},
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    Payment.objects.update_or_create(
        booking=booking,
        defaults={
            "stripe_session_id": session.id,
            "amount": booking.total_amount,
            "status": Payment.Status.PENDING,
        },
    )
    return JsonResponse({"id": session.id, "url": session.url})


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, renter=request.user)
    return render(request, "payments/success.html", {"booking": booking})


@login_required
def payment_cancel(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, renter=request.user)
    return render(request, "payments/cancel.html", {"booking": booking})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        booking_id = session.get("metadata", {}).get("booking_id")
        if booking_id:
            try:
                booking = Booking.objects.get(pk=booking_id)
                booking.status = Booking.Status.PAID
                booking.save(update_fields=["status", "updated_at"])
                Payment.objects.filter(booking=booking).update(
                    status=Payment.Status.SUCCEEDED,
                    stripe_payment_intent=session.get("payment_intent", ""),
                )
            except Booking.DoesNotExist:
                pass
    elif event["type"] in ("payment_intent.payment_failed",):
        intent = event["data"]["object"]
        Payment.objects.filter(stripe_payment_intent=intent["id"]).update(
            status=Payment.Status.FAILED
        )

    return HttpResponse(status=200)
