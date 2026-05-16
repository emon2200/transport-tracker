from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import * # আপনার সব ভিউ এখানে ইমপোর্ট করুন

# ১. Router তৈরি করা (ViewSet গুলোর জন্য)
router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'stations', StationViewSet)
router.register(r'device', DeviceViewSet)

# ২. URL প্যাটার্ন
urlpatterns = [
    # Router এর সব ইউআরএল একসাথে
    path('api/', include(router.urls)),
    
    # স্পেশাল এপিআই (যা ViewSet নয়)
    path('api/gps-update/', ReceiveGPSData.as_view(), name='gps-update'),
    path('api/live-map/', LiveBusTracking.as_view(), name='live-map'),
    path('api/device-settings-log/', DeviceSettingsLogAPI.as_view()),
]