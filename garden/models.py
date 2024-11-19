from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Analytics(models.Model):
    ACTION_CHOICES = [
        ('SIGNUP', 'User Signup'),
        ('LOGIN', 'User Login'),
        ('PLOT_APPLICATION', 'Plot Application'),
        ('EVENT_SIGNUP', 'Event Signup'),
        ('CROP_RECORD', 'Crop Record Added'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analytics")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=now)
    details = models.JSONField(blank=True, null=True)  # Store additional info like plot ID or event ID

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

class GardenPlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending Approval'),
        ('occupied', 'Occupied'),
    ]
    plot_number = models.CharField(max_length=10, unique=True)
    size = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_gardener = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'Plot {self.plot_number} - {self.status}'


class VolunteerEvent(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    volunteers_needed = models.PositiveIntegerField()
    assigned_volunteers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title
    
class CropRecord(models.Model):
    gardener = models.ForeignKey(User, on_delete=models.CASCADE)
    plot = models.ForeignKey(GardenPlot, on_delete=models.CASCADE)
    crop_type = models.CharField(max_length=100)
    planting_date = models.DateField()
    expected_harvest_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.crop_type} in Plot {self.plot.plot_number}'
    

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username