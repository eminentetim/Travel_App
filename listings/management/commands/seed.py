from django.core.management.base import BaseCommand
from listings.models import Listing, Booking, Review
from django.contrib.auth.models import User
from faker import Faker
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Seed the database with sample data for Listings, Bookings, and Reviews'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Optional: Clear existing data
        Listing.objects.all().delete()
        Booking.objects.all().delete()
        Review.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()  # Delete non-admin users

        # Predefined locations
        locations = ['Paris', 'New York', 'Tokyo', 'Sydney', 'Cape Town', 'Rome', 'Barcelona', 'Dubai', 'Singapore', 'London']

        # Create 10 sample users
        users = []
        for _ in range(10):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='password123'
            )
            users.append(user)
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))

        # Create 20 sample listings
        listings = []
        for _ in range(20):
            title = fake.sentence(nb_words=4)
            description = fake.paragraph(nb_sentences=5)
            location = random.choice(locations)
            price_per_night = round(random.uniform(50, 500), 2)
            available_from = fake.date_between(start_date='today', end_date='+30d')
            available_to = available_from + timedelta(days=random.randint(5, 30))

            listing = Listing.objects.create(
                title=title,
                description=description,
                location=location,
                price_per_night=price_per_night,
                available_from=available_from,
                available_to=available_to
            )
            listings.append(listing)
            self.stdout.write(self.style.SUCCESS(f'Created listing: {listing.title}'))

        # Create 50 sample bookings
        for _ in range(30):
            user = random.choice(users)
            listing = random.choice(listings)
            check_in = fake.date_between(start_date=listing.available_from, end_date=listing.available_to)
            check_out = check_in + timedelta(days=random.randint(1, 7))
            number_of_guests = random.randint(1, 6)
            total_price = listing.price_per_night * (check_out - check_in).days

            booking = Booking.objects.create(
                user=user,
                listing=listing,
                check_in=check_in,
                check_out=check_out,
                number_of_guests=number_of_guests,
                total_price=total_price
            )
            self.stdout.write(self.style.SUCCESS(f'Created booking: {booking.user.username} -> {booking.listing.title}'))

        # Create 100 sample reviews
        for _ in range(50):
            user = random.choice(users)
            listing = random.choice(listings)

            # Ensure each user only leaves one review per listing
            if not Review.objects.filter(user=user, listing=listing).exists():
                rating = random.randint(1, 5)
                comment = fake.paragraph(nb_sentences=2)

                review = Review.objects.create(
                    user=user,
                    listing=listing,
                    rating=rating,
                    comment=comment
                )
                self.stdout.write(self.style.SUCCESS(f'Created review: {review.user.username} -> {review.listing.title} ({review.rating}/5)'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipped duplicate review: {user.username} -> {listing.title}'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully.'))