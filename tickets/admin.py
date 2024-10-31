from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Ticket, DataCenter, CustomUser, NewInventory, EOLTracking, HeatTracking, HistoryLog, Notification, TechnicianProfile
from django.utils.html import format_html
from django.db.models import Count

# Define inline class to display tickets for each technician
class TechnicianTicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    fields = ('title', 'status', 'priority', 'center', 'assigned_date')

# Customize CustomUserAdmin to show technicians and their ticket details
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),  # Add the role field to the user form in admin
    )
    
    # Add fields to the user creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'role'),
        }),
    )

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'ticket_count', 'view_tickets']
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role',)  # Filter users by role to quickly find technicians

    # Inline tickets for technicians
    inlines = [TechnicianTicketInline]

    def ticket_count(self, obj):
        # Return the number of tickets assigned to the user (technician)
        return obj.ticket_set.count()
    ticket_count.short_description = 'Number of Tickets'

    def view_tickets(self, obj):
        # Create a link to the tickets page filtered by the technician
        return format_html('<a href="/admin/tickets/ticket/?assignee__id={}">View Tickets</a>', obj.id)
    view_tickets.short_description = 'View Tickets'

    def get_queryset(self, request):
        # Override queryset to include all users (technicians and admins)
        qs = super().get_queryset(request)
        return qs.annotate(ticket_count=Count('ticket'))

# Customize TicketAdmin to show technician details and product details
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'center', 'assignee', 'assigned_date', 'product_name', 'product_id')
    search_fields = ('title', 'center__name', 'assignee__username')
    list_filter = ('status', 'priority', 'center')

    def product_name(self, obj):
        # Display the product name from the related NewInventory model
        return obj.product.product_name if obj.product else '-'
    product_name.short_description = 'Product Name'

    def product_id(self, obj):
        # Display the product ID from the related NewInventory model
        return obj.product.product_id if obj.product else '-'
    product_id.short_description = 'Product ID'

# Register the customized TicketAdmin
admin.site.register(Ticket, TicketAdmin)

# Register the remaining models
admin.site.register(DataCenter)
admin.site.register(NewInventory)
admin.site.register(EOLTracking)
admin.site.register(HeatTracking)
admin.site.register(HistoryLog)
admin.site.register(Notification)

# Register the TechnicianProfile model
admin.site.register(TechnicianProfile)
