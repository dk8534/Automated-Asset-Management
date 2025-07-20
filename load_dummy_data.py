#!/usr/bin/env python
"""
Script to load dummy data for the Asset Management System
Run this after migrations: python load_dummy_data.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_management.settings')
django.setup()

from django.contrib.auth.models import User
from assets.models import UserProfile, Asset, AssetAssignment
from django.utils import timezone

def create_users():
    """Create demo users with different roles"""
    
    # Admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@company.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Use update_or_create for UserProfile to handle idempotency for unique fields
    admin_profile, created = UserProfile.objects.update_or_create(
        user=admin_user, # Lookup by user
        defaults={
            'role': 'admin',
            'employee_id': 'EMP001', # This will be set/updated
            'department': 'IT Administration',
            'phone': '+1-555-0001'
        }
    )
    
    # Asset Incharge user
    incharge_user, created = User.objects.get_or_create(
        username='incharge',
        defaults={
            'first_name': 'Asset',
            'last_name': 'Manager',
            'email': 'incharge@company.com'
        }
    )
    if created:
        incharge_user.set_password('incharge123')
        incharge_user.save()
    
    incharge_profile, created = UserProfile.objects.update_or_create(
        user=incharge_user,
        defaults={
            'role': 'asset_incharge',
            'employee_id': 'EMP002',
            'department': 'IT Operations',
            'phone': '+1-555-0002'
        }
    )
    
    # Regular users
    users_data = [
        ('user1', 'John', 'Doe', 'john.doe@company.com', 'EMP003', 'Engineering', '+1-555-0003'),
        ('user2', 'Jane', 'Smith', 'jane.smith@company.com', 'EMP004', 'Marketing', '+1-555-0004'),
        ('user3', 'Bob', 'Johnson', 'bob.johnson@company.com', 'EMP005', 'Sales', '+1-555-0005'),
        ('user4', 'Alice', 'Brown', 'alice.brown@company.com', 'EMP006', 'HR', '+1-555-0006'),
        ('user5', 'Charlie', 'Wilson', 'charlie.wilson@company.com', 'EMP007', 'Finance', '+1-555-0007'),
    ]
    
    for username, first_name, last_name, email, emp_id, dept, phone in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
        )
        if created:
            user.set_password('user123')
            user.save()
        
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'role': 'user',
                'employee_id': emp_id,
                'department': dept,
                'phone': phone
            }
        )
    
    print("✅ Users created successfully!")

def create_assets():
    """Create dummy assets"""
    
    assets_data = [
        # Laptops
        ('LAP001', 'Dell Latitude 7420', 'Engineering', 'laptop', 'available', 'Dell Inc.'),
        ('LAP002', 'MacBook Pro 16"', 'Engineering', 'laptop', 'assigned', 'Apple Inc.'),
        ('LAP003', 'ThinkPad X1 Carbon', 'Marketing', 'laptop', 'assigned', 'Lenovo'),
        ('LAP004', 'HP EliteBook 840', 'Sales', 'laptop', 'available', 'HP Inc.'),
        ('LAP005', 'Surface Laptop 4', 'HR', 'laptop', 'assigned', 'Microsoft'),
        
        # Desktops
        ('DES001', 'Dell OptiPlex 7090', 'Finance', 'desktop', 'available', 'Dell Inc.'),
        ('DES002', 'HP ProDesk 600', 'Engineering', 'desktop', 'assigned', 'HP Inc.'),
        ('DES003', 'iMac 24"', 'Marketing', 'desktop', 'available', 'Apple Inc.'),
        
        # Monitors
        ('MON001', 'Dell UltraSharp U2720Q', 'Engineering', 'monitor', 'assigned', 'Dell Inc.'),
        ('MON002', 'LG 27UK850-W', 'Marketing', 'monitor', 'available', 'LG Electronics'),
        ('MON003', 'Samsung C27F390', 'Sales', 'monitor', 'available', 'Samsung'),
        ('MON004', 'ASUS ProArt PA278QV', 'Engineering', 'monitor', 'assigned', 'ASUS'),
        
        # Printers
        ('PRT001', 'HP LaserJet Pro M404n', 'Office', 'printer', 'available', 'HP Inc.'),
        ('PRT002', 'Canon PIXMA TR8620', 'Marketing', 'printer', 'available', 'Canon'),
        ('PRT003', 'Brother HL-L2350DW', 'Finance', 'printer', 'maintenance', 'Brother'),
        
        # Mobile Phones
        ('MOB001', 'iPhone 13 Pro', 'Sales', 'mobile', 'assigned', 'Apple Inc.'),
        ('MOB002', 'Samsung Galaxy S22', 'Marketing', 'mobile', 'assigned', 'Samsung'),
        ('MOB003', 'Google Pixel 6', 'Engineering', 'mobile', 'available', 'Google'),
        
        # Tablets
        ('TAB001', 'iPad Pro 12.9"', 'Marketing', 'tablet', 'assigned', 'Apple Inc.'),
        ('TAB002', 'Surface Pro 8', 'Sales', 'tablet', 'available', 'Microsoft'),
        
        # Other equipment
        ('OTH001', 'Logitech MX Master 3', 'Engineering', 'other', 'assigned', 'Logitech'),
        ('OTH002', 'Blue Yeti Microphone', 'Marketing', 'other', 'available', 'Blue Microphones'),
        ('OTH003', 'Webcam C920', 'HR', 'other', 'assigned', 'Logitech'),
    ]
    
    for serial, name, dept, category, status, company in assets_data:
        asset, created = Asset.objects.get_or_create(
            serial_number=serial,
            defaults={
                'display_name': name,
                'department': dept,
                'model_category': category,
                'status': status,
                'company': company
            }
        )
    
    print("✅ Assets created successfully!")

def create_assignments():
    """Create some asset assignments"""
    
    # Get users for assignments
    users = User.objects.filter(userprofile__role='user')
    incharge = User.objects.get(username='incharge')
    
    # Assign some assets
    assignments_data = [
        ('LAP002', 'user1'),  # MacBook Pro to John Doe
        ('LAP003', 'user2'),  # ThinkPad to Jane Smith
        ('LAP005', 'user4'),  # Surface Laptop to Alice Brown
        ('DES002', 'user3'),  # HP ProDesk to Bob Johnson
        ('MON001', 'user1'),  # Dell Monitor to John Doe
        ('MON004', 'user1'),  # ASUS Monitor to John Doe
        ('MOB001', 'user3'),  # iPhone to Bob Johnson
        ('MOB002', 'user2'),  # Samsung to Jane Smith
        ('TAB001', 'user2'),  # iPad to Jane Smith
        ('OTH001', 'user1'),  # Mouse to John Doe
        ('OTH003', 'user4'),  # Webcam to Alice Brown
    ]
    
    for asset_serial, username in assignments_data:
        try:
            asset = Asset.objects.get(serial_number=asset_serial)
            user = User.objects.get(username=username)
            
            # Create assignment record
            assignment, created = AssetAssignment.objects.get_or_create(
                asset=asset,
                assigned_to=user,
                returned_date__isnull=True,
                defaults={
                    'assigned_by': incharge,
                    'assigned_date': timezone.now(),
                    'notes': f'Initial assignment to {user.get_full_name()}'
                }
            )
            
            # Update asset
            if created:
                asset.assigned_user = user
                asset.status = 'assigned'
                asset.save()
                
        except (Asset.DoesNotExist, User.DoesNotExist):
            continue
    
    print("✅ Asset assignments created successfully!")

def main():
    """Main function to load all dummy data"""
    print("🚀 Loading dummy data for Asset Management System...")
    print("-" * 50)
    
    create_users()
    create_assets()
    create_assignments()
    
    print("-" * 50)
    print("✅ All dummy data loaded successfully!")
    print("\n📋 Demo Login Credentials:")
    print("Admin: admin / admin123")
    print("Asset Incharge: incharge / incharge123")
    print("Users: user1, user2, user3, user4, user5 / user123")

if __name__ == '__main__':
    main()
