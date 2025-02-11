# listings/views.py

from rest_framework import viewsets, permissions
from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer

import os
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from .models import Booking, Listing, Payment
from .serializers import BookingSerializer, ListingSerializer
from .tasks import send_booking_confirmation_email, send_payment_confirmation
from django.http import JsonResponse
from .services.chapa import initiate_payment, verify_payment  # Importing the Chapa functions
from rest_framework.decorators import api_view


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Listings API endpoint
@api_view(['GET'])
def get_listings(request):
    listings = Listing.objects.all()
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_booking(request):
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save()
        
      # Triggering the email notification for successful booking
        send_booking_confirmation_email.delay(booking.user_email)
        return Response({"message": "Booking created!", "booking_id": booking.id})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def initiate_booking_payment(request):
    """
    Initiates a payment request to Chapa and returns the checkout URL.
    """
    booking_id = request.data.get("booking_id")
    amount = request.data.get("amount")
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Initiating payment using the function from chapa.py
    checkout_url = initiate_payment(booking, amount)
    
    if checkout_url:
        payment = Payment.objects.create(booking=booking, transaction_id=f"booking_{booking_id}", status="Pending", amount=amount)
        return Response({"message": "Payment initiated", "checkout_url": checkout_url})
    
    return Response({"error": "Failed to initiate payment"}, status=400)


@api_view(['GET'])
def verify_payment_view(request, transaction_id):
    """
    Verifies a payment transaction with Chapa and updates payment status.
    """
    if not transaction_id:
        return Response({"error": "Transaction reference missing"}, status=400)

    # Verifying payment using the function from chapa.py
    payment_status = verify_payment(transaction_id)

    if payment_status:
        payment = Payment.objects.get(transaction_id=transaction_id)
        payment.status = "Completed"
        payment.save()

        # Triggering the email notification for successful payment
        send_payment_confirmation.delay(payment.booking.user_email)
        return Response({"message": "Payment successful"})

    return Response({"error": "Payment failed"}, status=400)