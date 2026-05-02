from django.contrib import admin

from .models import Category, Listing, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "campus", "category", "price_per_day", "status")
    list_filter = ("status", "category", "campus", "condition")
    search_fields = ("title", "description", "owner__email")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ListingImageInline]
