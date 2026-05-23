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

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
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

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

User = get_user_model()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, min_length=6, required=True)

class RoleBasedTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    # ফ্রন্টএন্ড (Flutter) থেকে রোল ইনপুট নেওয়ার জন্য ফিল্ড যোগ করা হলো
    role = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        # ফ্লাটার থেকে পাঠানো রোলটি আলাদা করে রাখা হলো
        input_role = attrs.get('role')
        
        # ১. প্রথমে ইমেইল এবং পাসওয়ার্ড ঠিক আছে কি না জ্যাঙ্গো চেক করবে
        # পাসওয়ার্ড ভুল হলে এটি নিজে থেকেই Authentication Error দেবে
        data = super().validate(attrs)
        
        # ২. পাসওয়ার্ড সঠিক হলে এবার ডাটাবেসের রোলের সাথে ইনপুট রোল ম্যাচ করানো হবে
        db_role = self.user.role
        
        if db_role != input_role:
            raise AuthenticationFailed({
                "detail": f"আপনি এই ইমেইল দিয়ে '{input_role}' হিসেবে লগইন করতে পারবেন না। আপনার সঠিক রোল হলো '{db_role}'।"
            })
            
        # ৩. ইমেইল, পাসওয়ার্ড এবং রোল—সব ম্যাচ করলে রেসপন্সে ডেটা পাঠানো হবে
        data['user_id'] = self.user.user_id
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['company_id'] = self.user.company.id if self.user.company else None
        
        return data    

# ২. রেজিস্ট্রেশন সিরিয়ালাইজার
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'role', 'phone_number', 'company')
    def create(self, validated_data):
        email = validated_data['email']
        
        # ইমেইলের ভেতরের ভ্যালুটাকেই আমরা জ্যাঙ্গোর ব্যাকগ্রাউন্ড username হিসেবে পাস করে দিচ্ছি
        user = User.objects.create_user(
            username=email,  # এই লাইনটি ডাটাবেসের NOT NULL এরর ফিক্স করবে
            email=email,
            password=validated_data['password'],
            role=validated_data.get('role', 'user'),
            phone_number=validated_data.get('phone_number', ''),
            company=validated_data.get('company', None)
        )
        return user    