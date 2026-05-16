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
# ১. জিওফেন্স সিরিয়ালাইজার
class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = '__all__'

# ২. ট্রিপ হিস্ট্রি সিরিয়ালাইজার (অ্যানালিটিক্স এর জন্য)
class TripsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trips
        fields = '__all__'

# ১. Active Mapping Serializer
# এটি দেখাবে কোন বাসের সাথে কোন ডিভাইসটি বর্তমানে যুক্ত (Active) আছে।
class ActiveMappingSerializer(serializers.ModelSerializer):
    asset_name = serializers.ReadOnlyField(source='asset.name')
    device_imei = serializers.ReadOnlyField(source='device.imei')

    class Meta:
        model = Active_Mapping
        fields = '__all__'
# একটি বাস কোন কোন জিওফেন্স এরিয়ার আন্ডারে আছে তা ম্যাপ করার জন্য।
class AssetGeofenceMapSerializer(serializers.ModelSerializer):
    asset_reg = serializers.ReadOnlyField(source='asset.reg_number')
    geofence_name = serializers.ReadOnlyField(source='geofence.name')

    class Meta:
        model = Asset_Geofence_Map
        fields = '__all__'

# হার্ডওয়্যার থেকে আসা হাজার হাজার লোকেশন ডেটা প্রসেস করার জন্য।
class GPSLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPS_Logs
        fields = '__all__'
        # ডেটাবেস পারফরম্যান্সের জন্য এগুলো রিড-অনলি রাখা ভালো যদি কেবল ডিসপ্লের জন্য হয়
        read_only_fields = ['timestamp']

# ডিভাইসের ইন্টারভ্যাল, রিস্টার্ট লগ বা মেটাডেটা ট্র্যাক করার জন্য।
class DeviceSettingsLogSerializer(serializers.ModelSerializer):
    device_imei = serializers.ReadOnlyField(source='device.imei')

    class Meta:
        model = Device_Settings_Log
        fields = '__all__'