
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone',
            'role',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    # The client cannot choose the account role.
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'phone',
            'role',
            'password',
        ]

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.pop('role', User.Role.CUSTOMER)

        if role not in (User.Role.CUSTOMER, User.Role.ARTISAN):
            raise serializers.ValidationError(
                {
                    'role': (
                        'This account type cannot be created '
                        'through public registration.'
                    )
                }
            )

        user = User(**validated_data, role=role)
        user.set_password(password)
        user.save()

        if user.role == User.Role.ARTISAN:
            from apps.marketplace.models import ArtisanProfile

            ArtisanProfile.objects.create(
                user=user,
                display_name=user.get_full_name() or user.email,
                skill='Update your skill',
                location='Warri'
            )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data['email'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError(
                'Email or password is incorrect.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This account is inactive.'
            )

        data['user'] = user
        return data
