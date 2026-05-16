from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import string
import random


def generate_unique_code():
    length = 6
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Asset.objects.filter(join_code=code).exists():
            return code
        
# --- User & Security Section ---
class Company(models.Model):
    company_id = models.AutoField(primary_key=True) # Primary Key
    name = models.CharField(max_length=100)
    plan = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # System Admin চাইলে বন্ধ করে দিতে পারবে
    contact_email = models.EmailField(unique=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True) # Primary Key
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True,blank=True) # Foreign Key
    # Note: PasswordHash এবং Email Django-র AbstractUser এ ডিফল্ট থাকে।
    # System Admin যাতে রোল অনুযায়ী ইউজার ম্যানেজ করতে পারে
    ROLE_CHOICES = [
        ('system_admin', 'System Admin'), # পুরো সিস্টেমের মালিক
        ('company_admin', 'Company Admin'), # ভার্সিটির ভেন্ডর/অ্যাডমিন
        ('user', 'User'),
        ('driver','Driver') # সাধারণ ইউজার
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True)

class Driver(models.Model):
    driver_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


# --- Asset & Configuration Section ---
class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True) # Primary Key
    company = models.ForeignKey(Company, on_delete=models.CASCADE) # Foreign Key
    name = models.CharField(max_length=100) # Bus Name
    current_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    # ইউনিক জয়েন কোড (Classroom Code এর মতো)
    join_code = models.CharField(max_length=10, unique=True, editable=False)
    license_plate = models.CharField(max_length=20)
    category = models.CharField(max_length=50) # e.g., University Bus
    status = models.CharField(max_length=20) # Active/Inactive
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = generate_unique_code()
        super().save(*args, **kwargs)

class Asset_Geofence_Map(models.Model):
    # এটি মূলত Asset এবং Geofence এর মধ্যে সংযোগকারী টেবিল
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)
    geofence = models.ForeignKey('Geofence', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Active') #

    class Meta:
        unique_together = ('asset', 'geofence') # একই ম্যাপ বারবার হবে না

class Geofence(models.Model):
    fence_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    geometry_data = models.TextField() # Coordinates for geofence area
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

# --- Device & Raw Data Section ---
class Active_Mapping(models.Model):
    asset = models.OneToOneField('Asset', on_delete=models.CASCADE) # ১টি বাসে ১টিই সক্রিয় ম্যাপিং
    device = models.OneToOneField('Device', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Online')

    def __str__(self):
        return f"{self.asset.name} assigned to {self.device.imei}"

class Device(models.Model):
    device_id = models.AutoField(primary_key=True) # Primary Key
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    asset = models.OneToOneField(Asset, on_delete=models.SET_NULL, null=True, related_name='device') # 1:1 Mapping
    imei = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50) # e.g., ESP32 + Neo-6M
    protocol = models.CharField(max_length=20, default='HTTP/MQTT')
    sim_no = models.CharField(max_length=20)
    firmware = models.CharField(max_length=20)
    battery_voltage = models.FloatField(default=12.0) # বাসের ব্যাটারি ভোল্টেজ (১২.৬ হলে ফুল চার্জ)
    is_engine_on = models.BooleanField(default=False) # ভোল্টেজ ১৪ এর উপরে গেলে ইঞ্জিন অন বোঝা যায়
    last_online = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 
    last_heartbeat = models.DateTimeField(null=True, blank=True) # সর্বশেষ কখন ডেটা পাঠিয়েছিল
    
    def get_status(self):
        # যদি ৫ মিনিটের বেশি সময় ডেটা না আসে তবে অফলাইন দেখাবে
        import datetime
        from django.utils import timezone
        if self.last_heartbeat and (timezone.now() - self.last_heartbeat).seconds > 60:
            return "Disabled"
        return "Active"

class GPS_Logs(models.Model):
    log_id = models.BigAutoField(primary_key=True) # High-volume data
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs') # Foreign Key
    timestamp = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.FloatField()
    heading = models.FloatField()
    altitude = models.FloatField()

class Last_Known_Location(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, primary_key=True)
    timestamp = models.DateTimeField()
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.FloatField()
    
    # নতুন ফিল্ড: ব্যাকআপ ট্র্যাকিং চেনার জন্য
    TRACKING_SOURCES = (
        ('IOT', 'Hardware Device'),
        ('MOB', 'Driver Mobile'),
    )
    source = models.CharField(max_length=3, choices=TRACKING_SOURCES, default='IOT')

    def __str__(self):
        return f"{self.device.imei} at {self.lat}, {self.long} via {self.get_source_display()}"

class Device_Settings_Log(models.Model):
    log_id = models.BigAutoField(primary_key=True) # High-volume ডেটার জন্য BigAutoField
    device = models.ForeignKey('Device', on_delete=models.CASCADE, related_name='settings_logs') #
    parameter = models.CharField(max_length=100) # যেমন: 'Sampling_Rate', 'WiFi_SSID', 'Transmission_Interval'
    value = models.CharField(max_length=255) # প্যারামিটারের মান
    timestamp = models.DateTimeField(auto_now_add=True) # কখন পরিবর্তন বা লগ জেনারেট হয়েছে

    def __str__(self):
        return f"{self.device.imei} - {self.parameter}: {self.value}"

# .....station and Route ......
class Station(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
     
    def __str__(self):
        return self.name 
    
class BusRoute(models.Model):
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    sequence = models.IntegerField() # স্টেশন এর সিরিয়াল (১, ২, ৩...) 
     

# --- Business Logic & Intelligence Section ---
class Trips(models.Model):
    trip_id = models.AutoField(primary_key=True) # Primary Key
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE) # Foreign Key
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    distance = models.FloatField()
    avg_speed = models.FloatField()
    status = models.CharField(max_length=20, default='ongoing') # 'ongoing' or 'completed'

class UserBusSubscription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bus_subscriptions')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # --- আপনার কাঙ্ক্ষিত নতুন ফিল্ডগুলো ---
    my_station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True)
    # নোটিফিকেশন একবার পাঠানোর পর যেন বারবার না যায় তার জন্য ফ্ল্যাগ
    notified_prev_station = models.BooleanField(default=False) 
    notified_my_station = models.BooleanField(default=False)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'asset')

    def __str__(self):
        return f"{self.user.username} -> {self.asset.name} ({self.status})"

class Alerts(models.Model):
    ALERT_TYPES = (
        ('OS', 'Over Speed'),
        ('SOS', 'Emergency / SOS Button'),
        ('DD', 'Device Disabled / Offline'),
        ('GF', 'Geofence Violation'),
    )

    alert_id = models.AutoField(primary_key=True)
    # Asset এবং Device দুটির সাথেই কানেকশন রাখা ভালো
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='alerts')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_alerts')
    
    alert_type = models.CharField(max_length=3, choices=ALERT_TYPES)
    value = models.CharField(max_length=100, help_text="গতি বা অন্য কোনো ভ্যালু")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # ইমার্জেন্সি লোকেশন স্টোরেজ
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # রেজোলিউশন স্ট্যাটাস
    is_resolved = models.BooleanField(default=False) 
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.asset.reg_number}"
  
