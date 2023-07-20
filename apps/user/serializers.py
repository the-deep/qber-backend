from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from utils.hcaptcha import CaptchaSerializerMixin
from utils.common import get_client_ip, get_device_type
from main.emails import send_password_reset, send_password_changed_notification
from main.token import TokenManager

from .validators import CustomMaximumLengthValidator
from .models import User


class RegisterSerializer(CaptchaSerializerMixin, serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'captcha',
        )

    def validate_email(self, email):
        email = email.lower()
        existing_users_qs = User.objects.filter(email=email)
        if existing_users_qs.exists():
            raise serializers.ValidationError('User with that email already exists!!')
        return email

    # Only this method is used for Register
    def create(self, validated_data: dict):
        validated_data.pop('captcha')
        user = super().create(validated_data)
        transaction.on_commit(
            lambda: send_password_reset(
                user=user,
                welcome=True,
            )
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, password):
        # this will now only handle max-length in the login
        CustomMaximumLengthValidator().validate(password=password)
        return password

    def validate(self, data):
        # NOTE: authenticate only works for active users
        authenticate_user = authenticate(
            email=data['email'].lower(),
            password=data['password'],
        )
        # User doesn't exists in the system.
        if authenticate_user is None:
            raise serializers.ValidationError('No active account found with the given credentials')
        return {'user': authenticate_user}


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, password):
        user = self.context['request'].user
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid Old Password')
        return password

    def validate_new_password(self, password):
        validate_password(password)
        return password

    def save(self):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save(update_fields=('password',))
        client_ip = get_client_ip(self.context['request'])
        device_type = get_device_type(self.context['request'])
        transaction.on_commit(
            lambda: send_password_changed_notification(
                user=user,
                client_ip=client_ip,
                device_type=device_type
            )
        )


class PasswordResetTriggerSerializer(CaptchaSerializerMixin, serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data['email'].lower()
        existing_users_qs = User.objects.filter(email=email)
        if not existing_users_qs.exists():
            raise serializers.ValidationError("User with that email doesn't exists!!")
        return {
            **data,
            'user': existing_users_qs.first(),
        }

    def save(self):
        user = self.validated_data['user']
        client_ip = get_client_ip(self.context['request'])
        device_type = get_device_type(self.context['request'])
        transaction.on_commit(
            lambda: send_password_reset(
                user=user,
                client_ip=client_ip,
                device_type=device_type
            )
        )


class PasswordResetConfirmSerializer(CaptchaSerializerMixin, serializers.Serializer):
    uuid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uuid']))
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            user = None

        token_generator = TokenManager.password_reset_token_generator
        if user is not None and token_generator.check_token(user, data['token']):
            return {
                **data,
                'user': user,
            }
        raise serializers.ValidationError('Invalid or expired token')

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save(update_fields=('password',))
        client_ip = get_client_ip(self.context['request'])
        device_type = get_device_type(self.context['request'])
        transaction.on_commit(
            lambda: send_password_changed_notification(
                user=user,
                client_ip=client_ip,
                device_type=device_type
            )
        )


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email_opt_outs',
        )
