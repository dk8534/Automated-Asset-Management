from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<str:serial_number>/', views.asset_detail, name='asset_detail'),
    path('assets/<str:serial_number>/edit/', views.asset_edit, name='asset_edit'),
    path('assets/<str:serial_number>/delete/', views.asset_delete, name='asset_delete'),
    path('assets/<str:serial_number>/assign/', views.assign_asset, name='assign_asset'),
    path('assets/<str:serial_number>/return/', views.return_asset, name='return_asset'),
    path('assets/export/excel/', views.export_assets_excel, name='export_assets_excel'), # New URL for Excel export
]
