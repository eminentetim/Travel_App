from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(user_email, booking_details):
    subject = "Booking Confirmation"
    message = f"Hello, your booking has been confirmed!\n\nDetails:\n{booking_details}"
    from_email = "noreply@travelapp.com"
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)

@shared_task
def send_payment_confirmation(user_email, payment_details):
    subject = "Payment Confirmation"
    message = f"Hello, your payment has been confirmed!\n\nDetails:\n{payment_details}"
    from_email = "noreply@travelapp.com"
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)
