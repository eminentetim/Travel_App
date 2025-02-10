from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    listing = serializers.StringRelatedField(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing', write_only=True
    )
    total_price_display = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'user', 'listing', 'listing_id', 'check_in', 'check_out',
                  'number_of_guests', 'total_price', 'total_price_display', 'created_at']
        read_only_fields = ['id', 'user', 'listing', 'total_price', 'created_at']

    def get_total_price_display(self, obj):
        return f"${obj.total_price}"

    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        listing = validated_data.pop('listing')
        check_in = validated_data.get('check_in')
        check_out = validated_data.get('check_out')
        number_of_guests = validated_data.get('number_of_guests')

        # Calculate total price
        duration = (check_out - check_in).days
        total_price = listing.price_per_night * duration * number_of_guests

        booking = Booking.objects.create(
            user=user,
            listing=listing,
            check_in=check_in,
            check_out=check_out,
            number_of_guests=number_of_guests,
            total_price=total_price
        )
        return booking


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    listing = serializers.StringRelatedField(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing', write_only=True
    )

    class Meta:
        model = Review
        fields = ['id', 'user', 'listing', 'listing_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'listing', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        listing = validated_data.pop('listing')
        rating = validated_data.get('rating')
        comment = validated_data.get('comment')

        review = Review.objects.create(
            user=user,
            listing=listing,
            rating=rating,
            comment=comment
        )
        return review