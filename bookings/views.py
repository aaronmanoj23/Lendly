from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from listings.models import Listing

from .forms import BookingForm
from .models import Booking


@login_required
@require_POST
def request_booking(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.owner == request.user:
        return JsonResponse({"error": "You cannot book your own listing."}, status=400)

    form = BookingForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": form.errors}, status=400)

    booking = form.save(commit=False)
    booking.listing = listing
    booking.renter = request.user
    booking.save()
    return JsonResponse(
        {
            "ok": True,
            "booking_id": booking.pk,
            "total": str(booking.total_amount),
            "status": booking.status,
        }
    )


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user not in (booking.renter, booking.listing.owner):
        return redirect("dashboard")
    return render(request, "bookings/booking_detail.html", {"booking": booking})


@login_required
@require_POST
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, listing__owner=request.user)
    if booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.APPROVED
        booking.save(update_fields=["status", "updated_at"])
    return redirect("booking_detail", pk=pk)


@login_required
@require_POST
def deny_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, listing__owner=request.user)
    if booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.DENIED
        booking.save(update_fields=["status", "updated_at"])
    return redirect("booking_detail", pk=pk)


@login_required
@require_POST
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, renter=request.user)
    if booking.status in (Booking.Status.PENDING, Booking.Status.APPROVED):
        booking.status = Booking.Status.CANCELED
        booking.save(update_fields=["status", "updated_at"])
    return redirect("booking_detail", pk=pk)
