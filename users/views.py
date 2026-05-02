from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from bookings.models import Booking
from listings.models import Listing
from messaging.models import Conversation
from payments.models import Payment

from .forms import ProfileForm


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "users/profile.html", {"form": form})


@login_required
def dashboard(request):
    my_listings = Listing.objects.filter(owner=request.user).order_by("-created_at")
    my_rentals = Booking.objects.filter(renter=request.user).order_by("-created_at")
    incoming = Booking.objects.filter(listing__owner=request.user).order_by("-created_at")
    earnings = (
        Payment.objects.filter(
            booking__listing__owner=request.user, status="succeeded"
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    convos = Conversation.objects.filter(participants=request.user).order_by("-updated_at")[:5]
    return render(
        request,
        "users/dashboard.html",
        {
            "my_listings": my_listings,
            "my_rentals": my_rentals,
            "incoming": incoming,
            "earnings": earnings,
            "convos": convos,
        },
    )
