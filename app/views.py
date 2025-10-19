from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Driver, Customer, RideRequest, Review
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Avg
from django.urls import reverse
from django.http import JsonResponse




def about_us(request, user_type, user_id):
    if user_type == 'customer':
        user = get_object_or_404(Customer, id=user_id)
    else:
        user = get_object_or_404(Driver, id=user_id)

    context = {
        'user': user,
        'user_type': user_type
    }
    return render(request, 'about_us.html', context)




def customer_dashboard(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    # Get selected city from query parameters
    selected_city = request.GET.get('city', '')

    # Get all drivers with status available/busy
    drivers = Driver.objects.filter(status__in=['available', 'busy'])
    
    # Filter drivers by city if selected
    if selected_city:
        drivers = drivers.filter(city=selected_city)

    # Add avg_rating attribute to each driver
    for driver in drivers:
        avg = Review.objects.filter(driver=driver).aggregate(Avg('rating'))['rating__avg']
        driver.avg_rating = round(avg or 0, 1)

    # Show all rides of the customer
    ride_requests = RideRequest.objects.filter(customer=customer).order_by('-created_at')

    # Exclude rides that already have a review
    reviewed_rides_ids = Review.objects.filter(customer=customer).values_list('ride_id', flat=True)
    ride_requests = ride_requests.exclude(id__in=reviewed_rides_ids)

    # Only accepted rides for past rides section
    past_rides = ride_requests.filter(status='accepted')

    # Get distinct list of cities for dropdown
    cities = Driver.objects.values_list('city', flat=True).distinct()

    context = {
        'user': customer,
        'drivers': drivers,
        'ride_requests': ride_requests,
        'past_rides': past_rides,
        'rides': RideRequest.objects.all(),
        'cities': cities,
        'selected_city': selected_city,
    }
    
    return render(request, 'customer_dashboard.html', context)






# Driver dashboard
def driver_dashboard(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    ride_requests = RideRequest.objects.filter(driver=driver, status="pending")
    context = {
        'driver': driver,
        'ride_requests': ride_requests
    }
    return render(request, 'driver_dashboard.html', context)

def driver_pending_requests_api(request, driver_id):
    """
    Returns JSON of all pending ride requests for a given driver.
    """
    driver = get_object_or_404(Driver, id=driver_id)
    ride_requests = RideRequest.objects.filter(driver=driver, status="pending")
    
    data = []
    for r in ride_requests:
        data.append({
            "id": r.id,
            "customer": f"{r.customer.first_name} {r.customer.last_name}",
            "pickup": r.pickup_location,
            "dropoff": r.dropoff_location,
        })
    
    return JsonResponse({"requests": data})

# Request ride page (customer chooses driver)
# def request_ride(request, driver_id):
#     driver = get_object_or_404(Driver, id=driver_id)
#     customer_id = request.session.get('user_id')
#     customer = get_object_or_404(Customer, id=customer_id)
#     context = {
#         'driver': driver,
#         'customer': customer
#     }
#     return render(request, 'request_page.html', context)


def request_ride(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    customer_id = request.session.get('user_id')
    customer = get_object_or_404(Customer, id=customer_id)

    selected_city = request.GET.get('city', '')
    if selected_city and driver.city != selected_city:
        return HttpResponse("Driver not available in selected city", status=400)

    context = {
        'driver': driver,
        'customer': customer,
        'selected_city': selected_city,  # pass to template
    }
    return render(request, 'request_page.html', context)


# Create ride request (submit)
def create_request(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    customer_id = request.session.get('user_id')
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        pickup = request.POST.get('pickup')
        dropoff = request.POST.get('dropoff')
        payment_method = request.POST.get('payment')
        selected_city = request.POST.get('city', '')

        # Create RideRequest with pending status
        RideRequest.objects.create(
            customer=customer,
            driver=driver,
            pickup_location=pickup,
            dropoff_location=dropoff,
            status='pending',
            payment_method=payment_method
        )
        messages.success(request, 'Ride request submitted successfully!')
        selected_city = request.POST.get('city', '')  # get from form hidden input
        return redirect(f"{reverse('customer_dashboard', args=[customer.id])}?city={selected_city}")

        # return redirect('customer_dashboard', customer_id=customer.id)

    return render(request, 'request_page.html', {'driver': driver, 'customer': customer})




def ride_status_api(request, customer_id):
    ride_requests = RideRequest.objects.filter(customer_id=customer_id).order_by('-created_at')
    data = []

    for ride in ride_requests:
        has_review = Review.objects.filter(ride=ride).exists()
        data.append({
            "ride_id": ride.id,
            "driver_name": f"{ride.driver.first_name} {ride.driver.last_name}" if ride.driver else "N/A",
            "status": ride.status,
            "can_rate": ride.status == 'accepted' and not has_review,
            "created_at": ride.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return JsonResponse({"rides": data})




@require_POST
def accept_request(request, request_id):
    ride_request = RideRequest.objects.get(id=request_id)
    driver = ride_request.driver

    # Prevent accepting if driver is already busy
    if driver.status == "busy":
        messages.warning(request, "You already have an active ride!")
        return redirect("driver_dashboard", driver_id=driver.id)

    # Accept the selected ride
    ride_request.status = "accepted"
    driver.status = "busy"
    driver.save()
    ride_request.save()
    messages.success(request, "You accepted the ride.")

    # Automatically reject all other pending requests for this driver
    other_requests = RideRequest.objects.filter(driver=driver, status="pending").exclude(id=ride_request.id)
    for req in other_requests:
        req.status = "rejected"
        req.save()

    return redirect("driver_dashboard", driver_id=driver.id)



# Reject ride request
@require_POST
def reject_request(request, request_id):
    ride_request = get_object_or_404(RideRequest, id=request_id)
    ride_request.status = "rejected"
    ride_request.save()

    messages.warning(request, "You rejected the ride.")
    return redirect('driver_dashboard', driver_id=ride_request.driver.id)

# Set driver status manually
def set_driver_status(request, driver_id, status):
    driver = get_object_or_404(Driver, id=driver_id)
    if status.lower() in ['available', 'busy', 'unavailable']:
        driver.status = status.lower()
        driver.save()
        messages.success(request, f"Driver status updated to {status.capitalize()}")
    return redirect('driver_dashboard', driver_id=driver.id)


def review_page(request, ride_id):
    ride = get_object_or_404(RideRequest, id=ride_id, status='accepted')
    driver = ride.driver
    customer = ride.customer

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        Review.objects.create(
            ride=ride,
            customer=customer,
            driver=driver,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Thank you for your review!")
        return redirect('customer_dashboard', customer_id=customer.id)

    context = {
        'ride': ride,
        'driver': driver,
        'customer': customer
    }
    return render(request, 'review_page.html', context)


def driver_comments(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    customer_id = request.session.get('user_id')
    # Get all reviews for this driver
    reviews = Review.objects.filter(driver=driver).order_by('-created_at')
    context = {
        'driver': driver,
        'reviews': reviews,
        'user': customer_id
    }
    return render(request, 'comments_list.html', context)
