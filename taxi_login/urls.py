from django.urls import path
from . import views


urlpatterns = [
    # Login
    path('', views.user_login, name='user_login'),
    # Customer registration
    path('register/customer/', views.register_customer, name='register_customer'),
    # Driver registration
    path('register/driver/', views.register_driver, name='register_driver'),
    # Logout
    path('logout/', views.user_logout, name='user_logout')
]
