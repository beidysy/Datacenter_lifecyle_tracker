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
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import auth views for login and logout
from tickets import views  # Your ticket views
from tickets.views import technicians_with_tickets  # Import technicians_with_tickets view

urlpatterns = [
    path('admin/', admin.site.urls),
    # Ticket URLs
    path('tickets/', views.tickets_list, name='tickets_list'),
    path('tickets/<int:id>/', views.ticket_detail, name='ticket_detail'),  # Detail view URL
    path('tickets/<int:id>/edit/', views.ticket_edit, name='ticket_edit'),  # Edit view
    path('tickets/<int:id>/delete/', views.ticket_delete, name='ticket_delete'),  # Delete view

    # Technicians and assigned tickets
    path('technicians/', technicians_with_tickets, name='technicians_with_tickets'),

    # Authentication (Login and Logout)
    path('login/', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='tickets/logout.html'), name='logout'),
]
