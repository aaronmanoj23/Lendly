from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from listings.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include("allauth.urls")),
    path("users/", include("users.urls")),
    path("listings/", include("listings.urls")),
    path("bookings/", include("bookings.urls")),
    path("messages/", include("messaging.urls")),
    path("reviews/", include("reviews.urls")),
    path("payments/", include("payments.urls")),
    path("dashboard/", include("users.dashboard_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
