from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from bookings.models import Booking
from listings.models import Category, Listing
from users.models import Campus

User = get_user_model()


class BookingTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="CPP", slug="cpp", email_domain="cpp.edu")
        self.cat = Category.objects.create(name="Bikes", slug="bikes")
        self.owner = User.objects.create_user(email="own@cpp.edu", password="pw12345!")
        self.renter = User.objects.create_user(email="rent@cpp.edu", password="pw12345!")
        self.listing = Listing.objects.create(
            owner=self.owner,
            campus=self.campus,
            category=self.cat,
            title="Bike",
            description="d",
            price_per_day=Decimal("10.00"),
            deposit=Decimal("5.00"),
        )

    def test_total_computation(self):
        start = date.today()
        end = start + timedelta(days=2)
        b = Booking.objects.create(
            listing=self.listing, renter=self.renter, start_date=start, end_date=end
        )
        # 3 days * 10 + 5 deposit = 35
        self.assertEqual(b.total_amount, Decimal("35.00"))
