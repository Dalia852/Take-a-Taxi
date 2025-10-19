from django.urls import path
from . import views

urlpatterns = [
    path('about/<str:user_type>/<int:user_id>/', views.about_us, name='about_us'),

    path('customer/<int:customer_id>/', views.customer_dashboard, name='customer_dashboard'),
    path('request/<int:driver_id>/', views.request_ride, name='request_ride'),
    path('create/<int:driver_id>/', views.create_request, name='create_request'),


    path('api/customer/<int:customer_id>/rides/', views.ride_status_api, name='ride_status_api'),
    path('api/driver/<int:driver_id>/requests/', views.driver_pending_requests_api, name='driver_pending_requests_api'),



    path('driver/<int:driver_id>/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/<int:driver_id>/set_status/<str:status>/', views.set_driver_status, name='set_driver_status'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('driver/<int:driver_id>/comments/', views.driver_comments, name='driver_comments'),
    path('review/<int:ride_id>/', views.review_page, name='review_page')

]
