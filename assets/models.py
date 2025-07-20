from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('asset_incharge', 'Asset Incharge'),
        ('user', 'User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Asset(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]
    
    CATEGORY_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('monitor', 'Monitor'),
        ('printer', 'Printer'),
        ('mobile', 'Mobile Phone'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
    ]
    
    serial_number = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    model_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    company = models.CharField(max_length=100)
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.serial_number} - {self.display_name}"
    
    class Meta:
        ordering = ['-created_at']

class AssetAssignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_made')
    assigned_date = models.DateTimeField(default=timezone.now)
    returned_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.asset.serial_number} assigned to {self.assigned_to.username}"
    
    class Meta:
        ordering = ['-assigned_date']
