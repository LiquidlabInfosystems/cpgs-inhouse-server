# Developed By Tecktrio At Liquidlab Infosystems
# Project: Serializer
# Version: 1.0
# Date: 2025-03-08
# Description: Serializers for all the database models

from rest_framework import serializers
from cpgsapp.models import Account, NetworkSettings

class NetworkSettingsSerializer(serializers.ModelSerializer):
     class Meta:
        model = NetworkSettings
        fields = "__all__"

class SpaceInfoSerializer(serializers.ModelSerializer):
     class Meta:
        model = NetworkSettings
        fields = "__all__"

class AccountSerializer(serializers.ModelSerializer):
     class Meta:
        model = Account
        fields = "__all__"


