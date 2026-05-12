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
class ReceiveGPSData(APIView):
    def post(self, request):
        imei = request.data.get('imei')
        try:
            device = Device.objects.get(imei=imei)
            lat = request.data.get('lat')
            lng = request.data.get('lng')
            speed = request.data.get('speed', 0)
            voltage = request.data.get('battery_voltage', 12.0)
            is_sos = request.data.get('sos', False)

            # ১. ডিভাইসের স্ট্যাটাস আপডেট (Battery & Engine)
            device.battery_voltage = voltage
            device.is_engine_on = True if speed > 5 else False
            device.save()

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

            # ৪. SOS অ্যালার্ট ডিটেকশন
            if is_sos:
                Alerts.objects.create(
                    asset=device.asset,
                    type="SOS",
                    value="Emergency Button Pressed!",
                    is_emergency=True,
                    latitude=lat,
                    longitude=lng
                )

            return Response({"status": "Updated Successfully"}, status=status.HTTP_200_OK)

        except Device.DoesNotExist:
            return Response({"error": "IMEI not recognized"}, status=status.HTTP_404_NOT_FOUND)

# ৩. ম্যাপের জন্য সব বাসের লেটেস্ট লোকেশন এপিআই
class LiveBusTracking(APIView):
    def get(self, request):
        locations = Last_Known_Location.objects.all()
        serializer = LastLocationSerializer(locations, many=True)
        return Response(serializer.data)