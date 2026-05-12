from rest_framework import serializers
from .models import *

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class AssetSerializer(serializers.ModelSerializer):
    # ড্রাইভারের নাম সরাসরি দেখার জন্য Nested Serializer
    current_driver_info = DriverSerializer(source='current_driver', read_only=True)
    class Meta:
        model = Asset
        fields = '__all__'

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'

class BusRouteSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    class Meta:
        model = BusRoute
        fields = '__all__'

class LastLocationSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='device.asset.name', read_only=True)
    class Meta:
        model = Last_Known_Location
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerts
        fields = '__all__'

class UserBusSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusSubscription
        fields = '__all__'