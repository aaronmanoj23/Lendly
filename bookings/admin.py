from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "renter", "start_date", "end_date", "status", "total_amount")
    list_filter = ("status",)
    search_fields = ("listing__title", "renter__email")
    date_hierarchy = "created_at"
