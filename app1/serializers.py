from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'mobile', 'ssn', 'updated_at']
from rest_framework import serializers
from .models import BeneficiaryProfile

from rest_framework import serializers
from .models import BeneficiaryProfile

class BeneficiaryProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryProfile
        fields = '__all__'
