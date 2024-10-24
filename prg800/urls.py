"""
URL configuration for prg800 project.

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
from django.urls import path
from django.contrib.auth import views as auth_views
from tickets import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirect after login based on user role
    path('dashboard/', views.redirect_dashboard, name='redirect_dashboard'),

    # Admin and Technician Dashboard URLs
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('technician_dashboard/', views.technician_dashboard, name='technician_dashboard'),

    # Ticket-related URLs
    path('', views.home, name='home'),  # Home page
    path('tickets/', views.tickets_list, name='tickets_list'),  # Ticket list
    path('tickets/<int:id>/', views.ticket_detail, name='ticket_detail'),  # Ticket detail view
    path('tickets/<int:id>/edit/', views.ticket_edit, name='ticket_edit'),  # Ticket edit view
    path('tickets/<int:id>/delete/', views.ticket_delete, name='ticket_delete'),  # Ticket delete view

    # Contact Admin URL
    path('contact_admin/', views.contact_admin, name='contact_admin'),

    # Technicians and assigned tickets
    path('technicians/', views.technicians_with_tickets, name='technicians_with_tickets'),

    # Authentication (Login and Logout)
    path('login/', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),  # Login page
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),  # Logout redirects to home

    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
