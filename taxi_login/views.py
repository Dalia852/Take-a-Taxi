from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer, Driver

# ---------------------------
# Customer Registration
# ---------------------------
def register_customer(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        id_number = request.POST['id_number']
        city = request.POST['city']
        password = request.POST['password']
        default_pickup_address = request.POST['default_pickup_address']
        default_payment_method = request.POST['default_payment_method']

        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register_customer.html')

        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            id_number=id_number,
            city=city,
            default_pickup_address=default_pickup_address,
            default_payment_method=default_payment_method
        )
        customer.set_password(password)
        customer.save()

        messages.success(request, 'Customer registered successfully. You can now log in.')
        return redirect('user_login')

    return render(request, 'register_customer.html')


# ---------------------------
# Driver Registration
# ---------------------------
def register_driver(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        id_number = request.POST['id_number']
        city = request.POST['city']
        password = request.POST['password']
        license_number = request.POST['license_number']
        car_model = request.POST['car_model']
        car_model_year = request.POST['car_model_year']

        if Driver.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register_driver.html')

        driver = Driver(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            id_number=id_number,
            city=city,
            license_number=license_number,
            car_model=car_model,
            car_model_year=car_model_year
        )
        driver.set_password(password)
        driver.save()

        messages.success(request, 'Driver registered successfully. You can now log in.')
        return redirect('user_login')

    return render(request, 'register_driver.html')


# ---------------------------
# Login for Customer and Driver
# ---------------------------
def user_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user_type = request.POST.get('user_type', 'customer')

        user = None
        if user_type == 'customer':
            try:
                user = Customer.objects.get(email=email)
                if not user.check_password(password):
                    user = None
            except Customer.DoesNotExist:
                user = None
        else:
            try:
                user = Driver.objects.get(email=email)
                if not user.check_password(password):
                    user = None
            except Driver.DoesNotExist:
                user = None

        if user:
            request.session['user_id'] = user.id
            request.session['user_type'] = user_type
            if user_type == 'customer':
                return redirect('customer_dashboard', user.id)
            else:
                return redirect('driver_dashboard', user.id)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')


# ---------------------------
# Logout
# ---------------------------
def user_logout(request):
    request.session.flush()
    return redirect('user_login')
