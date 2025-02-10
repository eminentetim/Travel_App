from django.urls import path
from . import views  # Import the views from the listings app

urlpatterns = [
    path('', views.index, name='listings_home'),  # Root endpoint for the listings app
]
