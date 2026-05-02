from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from listings.models import Category, Listing
from users.models import Campus

User = get_user_model()


class ListingTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="CPP", slug="cpp", email_domain="cpp.edu")
        self.cat = Category.objects.create(name="Electronics", slug="electronics")
        self.user = User.objects.create_user(email="a@cpp.edu", password="pw12345!")
        self.listing = Listing.objects.create(
            owner=self.user,
            campus=self.campus,
            category=self.cat,
            title="Test Camera",
            description="desc",
            price_per_day=Decimal("10.00"),
        )

    def test_slug_generated(self):
        self.assertTrue(self.listing.slug.startswith("test-camera"))

    def test_browse_page(self):
        r = self.client.get(reverse("browse"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Test Camera")

    def test_detail_page(self):
        r = self.client.get(self.listing.get_absolute_url())
        self.assertEqual(r.status_code, 200)
