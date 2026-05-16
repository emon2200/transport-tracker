# Register your models here.
from django.contrib import admin
from .models import *

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'is_active', 'created_at')
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'company', 'is_staff')
    list_filter = ('role', 'company')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'join_code', 'license_plate', 'current_driver', 'company')
    readonly_fields = ('join_code',) # এটি অটো জেনারেট হয় তাই রিড-অনলি

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'company')

@admin.register(UserBusSubscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'asset', 'status', 'requested_at')
    list_filter = ('status',)
    actions = ['approve_subscriptions']

    def approve_subscriptions(self, request, queryset):
        queryset.update(status='approved')
    approve_subscriptions.short_description = "Selected রিকোয়েস্টগুলো Approve করুন"

@admin.register(Alerts)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('device', 'alert_type', 'is_resolved','resolved_at', 'timestamp','latitude','longitude',)
    list_filter = ('alert_type', 'is_resolved')
    search_fields = ('device__imei',)

# বাকি মডেলগুলোকেও এভাবে রেজিস্টার করে দিন
admin.site.register(Device)
admin.site.register(Station)
admin.site.register(BusRoute)
admin.site.register(Last_Known_Location)
admin.site.register(Geofence)