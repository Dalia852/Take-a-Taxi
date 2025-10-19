from django.contrib import admin
from .models import Customer, Driver

# ---------------------------
# Customer Admin
# ---------------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone', 
        'city', 'id_number', 'default_pickup_address', 
        'default_payment_method', 'created_at', 'updated_at'
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'id_number', 'city')
    list_filter = ('city', 'default_payment_method', 'created_at')


# ---------------------------
# Driver Admin
# ---------------------------
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone', 
        'city', 'id_number', 'license_number', 
        'car_model', 'car_model_year', 'status', 
        'created_at', 'updated_at'
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'id_number', 'license_number', 'car_model')
    list_filter = ('city', 'status', 'car_model_year', 'created_at')
