from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import *
from .serializers import *

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