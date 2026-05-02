from django.urls import path

from . import views

urlpatterns = [
    path("", views.browse, name="browse"),
    path("new/", views.create_listing, name="create_listing"),
    path("ai-price/", views.ai_price_suggestion, name="ai_price_suggestion"),
    path("<slug:slug>/", views.listing_detail, name="listing_detail"),
]
