from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from listings.models import Category, Listing
from users.models import Campus

User = get_user_model()


class Command(BaseCommand):
    help = "Seed Lendly with sample campuses, categories, users, and listings."

    def handle(self, *args, **options):
        campuses = [
            ("Cal Poly Pomona", "cpp", "cpp.edu", "Pomona", "CA"),
            ("UC Berkeley", "ucb", "berkeley.edu", "Berkeley", "CA"),
            ("Stanford", "stanford", "stanford.edu", "Stanford", "CA"),
        ]
        for name, slug, domain, city, state in campuses:
            Campus.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "email_domain": domain, "city": city, "state": state},
            )

        cats = ["Electronics", "Textbooks", "Bikes", "Tools", "Cameras", "Gaming", "Sports"]
        for name in cats:
            Category.objects.get_or_create(name=name)

        cpp = Campus.objects.get(slug="cpp")
        owner, created = User.objects.get_or_create(
            email="demo@cpp.edu",
            defaults={"full_name": "Demo Student", "campus": cpp, "is_email_verified": True},
        )
        if created:
            owner.set_password("demopass123")
            owner.save()

        sample = [
            ("Canon EOS R6 Camera", "Electronics", "like_new", "25.00"),
            ("Calculus: Early Transcendentals", "Textbooks", "good", "2.00"),
            ("Trek Mountain Bike", "Bikes", "good", "12.00"),
            ("DeWalt Drill Kit", "Tools", "like_new", "8.00"),
            ("PS5 Console", "Gaming", "like_new", "15.00"),
            ("Tennis Racket", "Sports", "good", "5.00"),
        ]
        for title, cat_name, condition, price in sample:
            cat = Category.objects.get(name=cat_name)
            Listing.objects.get_or_create(
                title=title,
                defaults={
                    "owner": owner,
                    "campus": cpp,
                    "category": cat,
                    "description": f"Sample listing for {title}.",
                    "condition": condition,
                    "price_per_day": Decimal(price),
                },
            )

        self.stdout.write(self.style.SUCCESS("Seeded Lendly with sample data."))
        self.stdout.write("Login: demo@cpp.edu / demopass123")
