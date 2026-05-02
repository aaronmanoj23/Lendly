from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.models import Campus

from .ai import suggest_daily_price
from .forms import ListingForm
from .models import Category, Listing, ListingImage


def home(request):
    featured = Listing.objects.filter(status=Listing.Status.ACTIVE)[:8]
    categories = Category.objects.all()[:12]
    campuses = Campus.objects.all()
    return render(
        request,
        "home.html",
        {"featured": featured, "categories": categories, "campuses": campuses},
    )


def browse(request):
    qs = Listing.objects.filter(status=Listing.Status.ACTIVE).select_related(
        "owner", "campus", "category"
    )

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(title__icontains=q)

    category = request.GET.get("category")
    if category:
        qs = qs.filter(category__slug=category)

    campus = request.GET.get("campus")
    if campus:
        qs = qs.filter(campus__slug=campus)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        try:
            qs = qs.filter(price_per_day__gte=Decimal(min_price))
        except Exception:
            pass
    if max_price:
        try:
            qs = qs.filter(price_per_day__lte=Decimal(max_price))
        except Exception:
            pass

    sort = request.GET.get("sort", "-created_at")
    allowed_sorts = {"-created_at", "price_per_day", "-price_per_day", "title"}
    if sort not in allowed_sorts:
        sort = "-created_at"
    qs = qs.order_by(sort)

    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "listings/browse.html",
        {
            "page": page,
            "categories": Category.objects.all(),
            "campuses": Campus.objects.all(),
            "q": q,
            "selected_category": category,
            "selected_campus": campus,
            "sort": sort,
        },
    )


def listing_detail(request, slug):
    listing = get_object_or_404(
        Listing.objects.select_related("owner", "campus", "category"),
        slug=slug,
    )
    return render(request, "listings/listing_detail.html", {"listing": listing})


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            for f in request.FILES.getlist("images"):
                ListingImage.objects.create(listing=listing, image=f)
            return redirect(listing.get_absolute_url())
    else:
        form = ListingForm(initial={"campus": request.user.campus})
    return render(request, "listings/create_listing.html", {"form": form})


@login_required
@require_POST
def ai_price_suggestion(request):
    f = request.FILES.get("image")
    if not f:
        return JsonResponse({"error": "image required"}, status=400)
    price = suggest_daily_price(f.read())
    if price is None:
        return JsonResponse({"error": "could not determine price"}, status=502)
    return JsonResponse({"suggested_price": str(price)})
