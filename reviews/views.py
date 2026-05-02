from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking

from .forms import ReviewForm
from .models import Review


@login_required
def create_review(request, booking_id):
    booking = get_object_or_404(
        Booking, pk=booking_id, renter=request.user, status=Booking.Status.COMPLETED
    )
    if hasattr(booking, "review"):
        return redirect("listing_detail", slug=booking.listing.slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.author = request.user
            review.save()
            return redirect("listing_detail", slug=booking.listing.slug)
    else:
        form = ReviewForm()
    return render(request, "reviews/create_review.html", {"form": form, "booking": booking})
