from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import openpyxl # For Excel export

from .models import Asset, UserProfile, AssetAssignment
from .forms import AssetForm, AssetAssignmentForm

# Helper functions for role-based access
def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'admin'

def is_asset_incharge(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'asset_incharge'

def is_admin_or_incharge(user):
    return is_admin(user) or is_asset_incharge(user)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.') # Added success message
    return redirect('login')

@login_required
def dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Get asset statistics based on user role
    if is_admin_or_incharge(request.user):
        total_assets = Asset.objects.count()
        assigned_assets = Asset.objects.filter(status='assigned').count()
        available_assets = Asset.objects.filter(status='available').count()
        maintenance_assets = Asset.objects.filter(status='maintenance').count()
        recent_assignments = AssetAssignment.objects.filter(returned_date__isnull=True).order_by('-assigned_date')[:5]
    else:  # regular user
        total_assets = Asset.objects.filter(assigned_user=request.user).count()
        assigned_assets = total_assets
        available_assets = 0
        maintenance_assets = 0
        recent_assignments = AssetAssignment.objects.filter(assigned_to=request.user, returned_date__isnull=True).order_by('-assigned_date')[:5]
    
    context = {
        'user_profile': user_profile,
        'total_assets': total_assets,
        'assigned_assets': assigned_assets,
        'available_assets': available_assets,
        'maintenance_assets': maintenance_assets,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'assets/dashboard.html', context)

@login_required
def asset_list(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Filter assets based on user role
    if is_admin_or_incharge(request.user):
        assets = Asset.objects.all()
    else:
        assets = Asset.objects.filter(assigned_user=request.user)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        assets = assets.filter(
            Q(serial_number__icontains=search_query) |
            Q(display_name__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(assigned_user__username__icontains=search_query) # Search by assigned user
        )
    
    # Filter functionality
    status_filter = request.GET.get('status')
    if status_filter:
        assets = assets.filter(status=status_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        assets = assets.filter(model_category=category_filter)
    
    # Determine if export button should be shown
    # It's shown if user is admin/incharge AND any filter/search is active
    show_export_button = is_admin_or_incharge(request.user)

    context = {
        'assets': assets,
        'user_profile': user_profile,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': Asset.STATUS_CHOICES,
        'category_choices': Asset.CATEGORY_CHOICES,
        'show_export_button': show_export_button, # Pass flag to template
    }
    return render(request, 'assets/asset_list.html', context)

@login_required
def asset_detail(request, serial_number):
    asset = get_object_or_404(Asset, serial_number=serial_number)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Check permissions for viewing
    if user_profile.role == 'user' and asset.assigned_user != request.user:
        messages.error(request, 'You do not have permission to view this asset.')
        return redirect('asset_list')
    
    assignments = AssetAssignment.objects.filter(asset=asset).order_by('-assigned_date')
    
    context = {
        'asset': asset,
        'user_profile': user_profile,
        'assignments': assignments,
    }
    return render(request, 'assets/asset_detail.html', context)

@login_required
@user_passes_test(is_admin) # Only Admin can create
def asset_create(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, user_role=user_profile.role, is_new_asset=True)
        if form.is_valid():
            # If status was disabled for Admin (new asset), ensure it's 'available'
            if 'status' in form.fields and form.fields['status'].widget.attrs.get('disabled'):
                form.instance.status = 'available' 
            form.save()
            messages.success(request, 'Asset created successfully.')
            return redirect('asset_list')
    else:
        form = AssetForm(user_role=user_profile.role, is_new_asset=True)
    
    return render(request, 'assets/asset_form.html', {'form': form, 'title': 'Create Asset'})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_asset_incharge(u)) # Admin or Incharge can access edit form
def asset_edit(request, serial_number):
    asset = get_object_or_404(Asset, serial_number=serial_number)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Specific permission check for editing
    if user_profile.role == 'user': # Should be caught by @user_passes_test, but as a fallback
        messages.error(request, 'You do not have permission to edit assets.')
        return redirect('asset_detail', serial_number=serial_number)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset, user_role=user_profile.role, is_new_asset=False)
        
        # IMPORTANT: If the serial_number field is disabled (which it is for existing assets
        # when edited by an Asset Incharge), it will not be in request.POST.
        # To prevent IntegrityError, we must remove it from the form's fields
        # before validation and saving. This ensures form.save() doesn't try to update it.
        if 'serial_number' in form.fields and form.fields['serial_number'].widget.attrs.get('disabled'):
            del form.fields['serial_number']
        
        print(f"DEBUG: asset_edit POST request for {serial_number}")
        print(f"DEBUG: request.POST data: {request.POST}")
        
        if form.is_valid():
            print(f"DEBUG: Form is valid. Cleaned data: {form.cleaned_data}")
            
            updated_asset = form.save(commit=False) # Save without committing first
            # The serial_number on updated_asset will correctly retain its original value
            # because it was not included in the form's data for update.

            # Handle status change to 'retired' (this logic is correct and should remain)
            new_status = form.cleaned_data.get('status')
            if new_status == 'retired':
                if updated_asset.assigned_user:
                    updated_asset.assigned_user = None
                    messages.info(request, f"Asset {updated_asset.serial_number} was unassigned as its status changed to Retired.")
                
                active_assignments = AssetAssignment.objects.filter(asset=updated_asset, returned_date__isnull=True)
                for assignment in active_assignments:
                    assignment.returned_date = timezone.now()
                    assignment.notes += "\n(Automatically returned due to asset retirement)"
                    assignment.save()
                    messages.info(request, f"Active assignment for {updated_asset.serial_number} was closed due to asset retirement.")

            updated_asset.save() # Now save the instance
            messages.success(request, 'Asset updated successfully.')
            
            # Verify asset still exists after save
            try:
                test_asset = Asset.objects.get(serial_number=serial_number)
                print(f"DEBUG: Asset {test_asset.serial_number} still exists with status {test_asset.status}")
            except Asset.DoesNotExist:
                print(f"ERROR: Asset {serial_number} DOES NOT EXIST after save!")
            
            return redirect('asset_detail', serial_number=updated_asset.serial_number)
        else:
            print(f"DEBUG: Form is NOT valid. Errors: {form.errors}")
            messages.error(request, 'Error updating asset. Please check the form.')
    else:
        form = AssetForm(instance=asset, user_role=user_profile.role, is_new_asset=False)
    
    return render(request, 'assets/asset_form.html', {'form': form, 'title': 'Edit Asset', 'asset': asset})

@login_required
@user_passes_test(is_admin) # Only Admin can delete
def asset_delete(request, serial_number):
    asset = get_object_or_404(Asset, serial_number=serial_number)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset deleted successfully.')
        return redirect('asset_list')
    
    return render(request, 'assets/asset_confirm_delete.html', {'asset': asset})

@login_required
@user_passes_test(is_asset_incharge) # Only Asset Incharge can assign
def assign_asset(request, serial_number):
    asset = get_object_or_404(Asset, serial_number=serial_number)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = AssetAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.asset = asset
            assignment.assigned_by = request.user
            assignment.save()
            
            # Update asset status and assigned user
            asset.assigned_user = assignment.assigned_to
            asset.status = 'assigned'
            asset.save()
            
            messages.success(request, f'Asset assigned to {assignment.assigned_to.username} successfully.')
            return redirect('asset_detail', serial_number=serial_number)
    else:
        form = AssetAssignmentForm()
    
    return render(request, 'assets/assign_asset.html', {'form': form, 'asset': asset})

@login_required
@user_passes_test(is_asset_incharge) # Only Asset Incharge can return
def return_asset(request, serial_number):
    asset = get_object_or_404(Asset, serial_number=serial_number)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Find the active assignment
    assignment = AssetAssignment.objects.filter(asset=asset, returned_date__isnull=True).first()
    
    if assignment:
        assignment.returned_date = timezone.now()
        assignment.save()
        
        # Update asset status
        asset.assigned_user = None
        asset.status = 'available'
        asset.save()
        
        messages.success(request, 'Asset returned successfully.')
    else:
        messages.error(request, 'No active assignment found for this asset.')
    
    return redirect('asset_detail', serial_number=serial_number)

@login_required
@user_passes_test(is_admin_or_incharge) # Only Admin or Asset Incharge can export
def export_assets_excel(request):
    # Get filters from request.GET
    search_query = request.GET.get('search', '') # Default to empty string
    status_filter = request.GET.get('status', '') # Default to empty string
    category_filter = request.GET.get('category', '') # Default to empty string

    print(f"DEBUG: export_assets_excel - Received search_query: '{search_query}'")
    print(f"DEBUG: export_assets_excel - Received status_filter: '{status_filter}'")
    print(f"DEBUG: export_assets_excel - Received category_filter: '{category_filter}'")

    # Get filters from request.GET and handle 'None' string values
    search_query = request.GET.get('search', '')
    if search_query == 'None':
        search_query = ''

    status_filter = request.GET.get('status', '')
    if status_filter == 'None':
        status_filter = ''

    category_filter = request.GET.get('category', '')
    if category_filter == 'None':
        category_filter = ''

    print(f"DEBUG: export_assets_excel - Processed search_query: '{search_query}'")
    print(f"DEBUG: export_assets_excel - Processed status_filter: '{status_filter}'")
    print(f"DEBUG: export_assets_excel - Processed category_filter: '{category_filter}'")

    assets = Asset.objects.all().order_by('serial_number')

    if search_query:
        assets = assets.filter(
            Q(serial_number__icontains=search_query) |
            Q(display_name__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(assigned_user__username__icontains=search_query)
        )
    if status_filter:
        assets = assets.filter(status=status_filter)
    if category_filter:
        assets = assets.filter(model_category=category_filter)

    print(f"DEBUG: export_assets_excel - Number of assets found for export: {assets.count()}")
    print(f"DEBUG: export_assets_excel - Final Query SQL: {assets.query}") # Print the generated SQL query

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="asset_report.xlsx"'

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Asset Report"

    # Add headers
    headers = [
        "Serial Number", "Display Name", "Department", "Model Category",
        "Status", "Company", "Assigned User", "Employee ID", "Assigned Date", "Returned Date"
    ]
    sheet.append(headers)

    # Add data
    for asset in assets:
        assigned_user_name = asset.assigned_user.get_full_name() if asset.assigned_user else "N/A"
        assigned_user_emp_id = asset.assigned_user.userprofile.employee_id if asset.assigned_user and hasattr(asset.assigned_user, 'userprofile') else "N/A"
        
        # Get latest assignment details
        latest_assignment = AssetAssignment.objects.filter(asset=asset).order_by('-assigned_date').first()
        assigned_date = latest_assignment.assigned_date.strftime('%Y-%m-%d %H:%M') if latest_assignment else "N/A"
        returned_date = latest_assignment.returned_date.strftime('%Y-%m-%d %H:%M') if latest_assignment and latest_assignment.returned_date else "N/A"

        row_data = [
            asset.serial_number, asset.display_name, asset.department,
            asset.get_model_category_display(), asset.get_status_display(),
            asset.company, assigned_user_name, assigned_user_emp_id,
            assigned_date, returned_date
        ]
        sheet.append(row_data)

    workbook.save(response)
    return response

from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        return HttpResponse("✅ Admin user created.")
    return HttpResponse("⚠️ Admin user already exists.")
