"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker.views import * # 'your_app_name' এর জায়গায় আপনার অ্যাপের নাম লিখুন
from rest_framework_simplejwt.views import TokenRefreshView

# ১. Router সেটআপ (যেগুলো ViewSet ব্যবহার করে তৈরি)
router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'stations', StationViewSet)
router.register(r'active-mappings', ActiveMappingViewSet, basename='active-mapping')
router.register(r'trips', TripsViewSet, basename='trips')
router.register(r'geofences', GeofenceViewSet, basename='geofences')
router.register(r'geofences', GeofenceViewSet)
router.register(r'asset-geofence-maps', AssetGeofenceMapViewSet)
router.register(r'bus-routes', BusRouteViewSet)
router.register(r'subscriptions', UserBusSubscriptionViewSet)
router.register(r'device', DeviceViewSet)

urlpatterns = [
    # অ্যাডমিন প্যানেল
    path('admin/', admin.site.urls),

    # সব ViewSet এর এপিআই (যেমন: /api/assets/)
    path('api/', include(router.urls)),

    # স্পেশাল এপিআই (যেগুলো APIView দিয়ে তৈরি)
    path('api/gps-update/', ReceiveGPSData.as_view(), name='gps-update'),
    path('api/live-map/', LiveBusTracking.as_view(), name='live-map'),
    path('api/device-settings-log/', DeviceSettingsLogAPI.as_view()),
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/auth/login/', CustomLoginView.as_view(), name='auth_login'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   
]