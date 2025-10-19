from django.contrib import admin
from .models import RideRequest, Review

# RideRequest
@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('customer', 'driver', 'pickup_location', 'dropoff_location', 'status', 'created_at')
    search_fields = ('customer__first_name', 'customer__last_name',
                     'driver__first_name', 'driver__last_name',
                     'pickup_location', 'dropoff_location')
    list_filter = ('status',)


# Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('ride', 'customer', 'driver', 'rating', 'created_at')
    search_fields = ('customer__first_name', 'customer__last_name',
                     'driver__first_name', 'driver__last_name',
                     'ride__pickup_location')
    list_filter = ('rating',)

