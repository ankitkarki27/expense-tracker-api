from rest_framework import serializers
from rest_framework.response import Response
from .models import ExpenseIncome
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.password_validation import validate_password
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
    }
    
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password','password2')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        
        username = attrs['username']
        email = attrs['email']
        
        if User.objects.filter(username__iexact=attrs['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    

class ExpenseIncomeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True) 
    total_amount = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p", read_only=True)

    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True)
    class Meta:
        model = ExpenseIncome
        fields = ('id', 'user', 'title', 'description', 'amount',
            'transaction_type', 'tax', 'tax_type', 'total_amount',
            'created_at', 'updated_at')
        read_only_fields = ('user','total_amount', 'created_at', 'updated_at')
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_tax(self, value):
        if value < 0:
            raise serializers.ValidationError("Tax cannot be negative.")
        return value

        
class ExpenseIncomeListSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True)
    
    class Meta:
        model = ExpenseIncome
        fields = [
            'id', 'title', 'amount', 
            'transaction_type', 'total_amount', 'created_at'
        ]

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        return token

