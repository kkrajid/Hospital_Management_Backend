from .models import User
from rest_framework import serializers
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'role', 'phone']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'default': 'Patient'},
        }

    # def validate_phone(self, phone):
    #     phone_pattern = re.compile(r'^\+\d{1,3}\d{3,14}$')
    #     if not phone_pattern.match(phone):
    #         raise serializers.ValidationError("Invalid phone number format. Please use a valid format.")
    #     return phone
    
    # def validate_password(self, password):
    #     password_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+{}\[\]:;<>,.?~\\-]{8,}$')
    #     if not password_pattern.match(password):
    #         raise serializers.ValidationError("Invalid password format. Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit.")
    #     return password

    def create(self, validated_data):
        if 'email' not in validated_data:
            raise serializers.ValidationError("Email is required.")
        if 'password' not in validated_data:
            raise serializers.ValidationError("Password is required.")

        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance
