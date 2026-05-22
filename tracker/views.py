from rest_framework import viewsets, status,generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# ১. জেনারেল ম্যানেজমেন্ট ভিউসেট (Admin/Manager এর জন্য)
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

# ২. ESP32 থেকে ডাটা রিসিভ করার মূল এপিআই (Smart Logic)
# tracker/views.py এর ভেতর পরিবর্তন করুন:

class ReceiveGPSData(APIView):
    def post(self, request):
        imei = request.data.get('imei')
        try:
            device = Device.objects.get(imei=imei)
            
            # এই নামগুলো পরিবর্তন করুন (ESP32 থেকে পাঠানো নামের সাথে মিলিয়ে)
            lat = request.data.get('latitude')   # আগে ছিল 'lat'
            lng = request.data.get('longitude')  # আগে ছিল 'lng'
            
            speed = request.data.get('speed', 0)
            voltage = request.data.get('battery_voltage', 12.0)
            is_sos = request.data.get('is_emergency', False) # ESP32 এ পাঠিয়েছিলেন 'is_emergency'

            # ২. হিস্ট্রি লগ সেভ করা
            GPS_Logs.objects.create(
                device=device,
                timestamp=timezone.now(),
                latitude=lat,
                longitude=lng,
                speed=speed,
                heading=request.data.get('heading', 0),
                altitude=request.data.get('altitude', 0)
            )

            # ৩. লেটেস্ট লোকেশন আপডেট
            Last_Known_Location.objects.update_or_create(
                device=device,
                defaults={'lat': lat, 'long': lng, 'speed': speed, 'timestamp': timezone.now()}
            )

            # ... বাকি কোড আগের মতোই থাকবে ...
            return Response({"status": "Updated Successfully"}, status=status.HTTP_200_OK)

        except Device.DoesNotExist:
            return Response({"error": "IMEI not recognized"}, status=status.HTTP_404_NOT_FOUND)

# ৩. ম্যাপের জন্য সব বাসের লেটেস্ট লোকেশন এপিআই
class LiveBusTracking(APIView):
    def get(self, request):
        locations = Last_Known_Location.objects.all()
        serializer = LastLocationSerializer(locations, many=True)
        return Response(serializer.data)
# ১. এক্টিভ ম্যাপিং (বাস এবং ডিভাইসের বর্তমান সংযোগ চেক করা)
class ActiveMappingViewSet(viewsets.ModelViewSet):
    queryset = Active_Mapping.objects.all()
    
    def list(self, request):
        # কেবল একটিভ থাকা কানেকশনগুলো দেখাবে
        active_list = self.queryset.filter(status='Active')
        serializer = serializers.Serializer(active_list, many=True)
        return Response(serializer.data)

# ২. ডিভাইস সেটিংস লগ (হার্ডওয়্যার প্যারামিটার পরিবর্তন ট্র্যাক করা)
class DeviceSettingsLogAPI(APIView):
    def post(self, request):
        # ESP32 যদি তার ইন্টারভ্যাল বা সেটিংস চেঞ্জ করে তবে এখানে লগ হবে
        imei = request.data.get('imei')
        parameter = request.data.get('parameter')
        value = request.data.get('value')
        
        device = Device.objects.get(imei=imei)
        log = Device_Settings_Log.objects.create(
            device=device,
            parameter=parameter,
            value=value
        )
        return Response({"status": "Log recorded"}, status=status.HTTP_201_CREATED)

# ৩. ট্রিপস এবং অ্যানালিটিক্স ভিউ
class TripsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trips.objects.all()
    serializer_class = TripsSerializer
    # এখানে কেবল নির্দিষ্ট বাসের ট্রিপ ফিল্টার করা যাবে
    def get_queryset(self):
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            return self.queryset.filter(asset_id=asset_id)
        return self.queryset
# ১. জিওফেন্স ম্যানেজমেন্ট (অ্যাডমিন এরিয়া তৈরি বা ডিলিট করতে পারবে)
class GeofenceViewSet(viewsets.ModelViewSet):
    queryset = Geofence.objects.all()
    serializer_class = GeofenceSerializer

# ২. অ্যাসেট ও জিওফেন্স ম্যাপিং (কোন বাস কোন জোনে আছে তা দেখার জন্য)
class AssetGeofenceMapViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Asset_Geofence_Map.objects.all()
    serializer_class = AssetGeofenceMapSerializer

# ৩. বাস রুট (বাসের নির্দিষ্ট রুট ম্যাপ বা স্টপেজ দেখার জন্য)
class BusRouteViewSet(viewsets.ModelViewSet):
    queryset = BusRoute.objects.all()
    serializer_class = BusRouteSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

# ৪. ইউজার বাস সাবস্ক্রিপশন (যাত্রীরা কোন বাসের আপডেট চায়)
class UserBusSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserBusSubscription.objects.all()
    serializer_class = UserBusSubscriptionSerializer
    
    # টিপস: এখানে ফিল্টার যোগ করা যায় যাতে একজন ইউজার শুধু নিজের সাবস্ক্রিপশন দেখে
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return UserBusSubscription.objects.filter(user=user)
        return UserBusSubscription.objects.none()
    


# ১. কাস্টম লগইন ভিউ
class CustomLoginView(TokenObtainPairView):
    serializer_class = RoleBasedTokenObtainPairSerializer

# ২. রেজিস্ট্রেশন ভিউ
class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

# ৩. লগআউট ভিউ (টোকেন ব্ল্যাকলিস্ট করার জন্য)
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or already logged out."}, status=status.HTTP_400_BAD_REQUEST)