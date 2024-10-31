from django.db import models
from django.conf import settings  # Use AUTH_USER_MODEL for user references
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid  # Import for generating unique IDs
# from .models import NewInventory
from django.utils import timezone



# Custom user model extending AbstractUser
class CustomUser(AbstractUser):
    role_choices = [('admin', 'Admin'), ('technician', 'Technician')]
    role = models.CharField(max_length=50, choices=role_choices)
    
    # Make email unique and required
    email = models.EmailField(unique=True)

    # Set email as the USERNAME_FIELD for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Keep 'username' as a required field for admin purposes

    def __str__(self):
        return self.email  # Return email instead of username for display


class TechnicianProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role_choices = [('admin', 'Admin'), ('technician', 'Technician')]
    role = models.CharField(max_length=50, choices=role_choices, default='technician')
    status_choices = [('active', 'Active'), ('inactive', 'Inactive')]
    status = models.CharField(max_length=50, choices=status_choices, default='active')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.role})"


class Ticket(models.Model):
    ticket_type_choices = [('EOL', 'EOL Tracking'), ('Heat', 'Heat Tracking')]
    status_choices = [('open', 'Open'), ('in_progress', 'In Progress'), ('closed', 'Closed')]
    priority_choices = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    ticket_type = models.CharField(max_length=100, choices=ticket_type_choices, default='EOL')
    status = models.CharField(max_length=100, choices=status_choices)
    priority = models.CharField(max_length=100, choices=priority_choices, default='low')
    center = models.ForeignKey('DataCenter', on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    assigned_date = models.DateTimeField(null=True, blank=True)
    product = models.ForeignKey('NewInventory', null=True, blank=True, on_delete=models.SET_NULL)  # Link to NewInventory
    


    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket_type} Ticket - {self.status}"

    def __str__(self):
        return f"{self.ticket_type} Ticket - {self.status}"

    def delete(self, *args, **kwargs):
        super(Ticket, self).delete(*args, **kwargs)
        print(f"Ticket {self.title} has been deleted.")



    def assign_to_technician(self):
        # Get the technician with the fewest open tickets
        least_busy_technician = CustomUser.objects.filter(
            role='technician'
        ).annotate(
            open_ticket_count=Count('ticket', filter=models.Q(ticket__status='open'))
        ).order_by('open_ticket_count').first()

        # Assign the ticket to the least busy technician if one exists
        if least_busy_technician:
            self.assignee = least_busy_technician
            self.assigned_date = timezone.now()  # Set the assigned_date to the current date and time
            print(f"[DEBUG] Assigned technician: {least_busy_technician.username}")
        else:
            print("[DEBUG] No technician available for assignment.")


        # OLD debuging save
    # def save(self, *args, **kwargs):
    #     # Save the ticket to generate a primary key if it hasn't been saved before
    #     if not self.pk:
    #         super(Ticket, self).save(*args, **kwargs)

    #     # Automatically assign to the least busy technician if not assigned
    #     if not self.assignee:
    #         self.assign_to_technician()

    #     # Log which technician is assigned
    #     if self.assignee:
    #         print(f"Ticket {self.title} assigned to {self.assignee.username}")

    #     # Save the ticket again with the assignee now set
    #     super(Ticket, self).save(*args, **kwargs)

# # New - Old Debugging Save
#     def save(self, *args, **kwargs):
#         # Debug statement to check initial product state
#         if self.product:
#             print(f"Product before saving: {self.product.product_name} - {self.product.product_id}")
#         else:
#             print("No product assigned before saving.")

#         # Save the ticket to generate a primary key if it hasn't been saved before
#         if not self.pk:
#             super(Ticket, self).save(*args, **kwargs)

#         # Automatically assign to the least busy technician if not assigned
#         if not self.assignee:
#             self.assign_to_technician()

#         # Log which technician is assigned
#         if self.assignee:
#             print(f"Ticket {self.title} assigned to {self.assignee.username}")

#         # Debug statement to check product state after assigning technician
#         if self.product:
#             print(f"Product after technician assignment: {self.product.product_name} - {self.product.product_id}")
#         else:
#             print("No product assigned after technician assignment.")

#         # Final save to ensure all fields are updated
#         super(Ticket, self).save(*args, **kwargs)

#         # Debug statement to confirm final save
#         if self.product:
#             print(f"Final save with product: {self.product.product_name} - {self.product.product_id}")
#         else:
#             print("No product assigned after final save.")

#     def save(self, *args, **kwargs):
#         # Check if product is already assigned
#         if not self.product:
#             # Fetch a default or specific product based on criteria
#             # For instance, get the first product with a specific status
#             default_product = NewInventory.objects.filter(product_status='active').first()
            
#             if default_product:
#                 print(f"Automatically assigning product {default_product.product_name} to the ticket.")
#                 self.product = default_product
#             else:
#                 print("Warning: No available product to assign automatically.")

#         # Save the ticket to generate a primary key if it hasn't been saved before
#         if not self.pk:
#             super(Ticket, self).save(*args, **kwargs)

#         # Automatically assign to the least busy technician if not assigned
#         if not self.assignee:
#             self.assign_to_technician()

#         # Final save to ensure all fields are updated
#         super(Ticket, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Only assign a product if it's not already assigned
        if not self.product:
            # Get the next available product with an 'active' status
            next_product = NewInventory.objects.filter(product_status='active').exclude(
                ticket__status='open'  # Adjust this if you have a way to track assigned products
            ).first()
            
            if next_product:
                print(f"Automatically assigning product {next_product.product_name} to the ticket.")
                self.product = next_product
            else:
                print("Warning: No available product to assign automatically.")

        # Automatically assign to the least busy technician if no assignee exists
        if not self.assignee:
            self.assign_to_technician()

        # Final save to ensure all fields are updated
        super(Ticket, self).save(*args, **kwargs)

        # Optionally, update the status of the assigned product to reflect it’s in use (if needed)
        if self.product:
            self.product.product_status = 'in_use'  # Assuming 'in_use' indicates it's assigned
            self.product.save()


class DataCenter(models.Model):
    center_name = models.CharField(max_length=100)
    center_location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.center_name


class NewInventory(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('switch', 'Switch'),
        ('router', 'Router'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]

    product_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50)
    product_spec = models.TextField(null=True, blank=True)
    eol = models.DateField()
    product_type = models.CharField(max_length=100, choices=PRODUCT_TYPE_CHOICES)
    product_status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    purchased_date = models.DateField(null=True, blank=True)
    center = models.ForeignKey('DataCenter', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=100, default=uuid.uuid4, unique=True)  # Automatically generate a unique Product ID

    def __str__(self):
        return self.product_name


class EOLTracking(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    old_product_name = models.CharField(max_length=100)
    old_serial_number = models.CharField(max_length=50)
    old_product_spec = models.TextField(null=True, blank=True)
    old_eol = models.DateField()
    new_product = models.ForeignKey('NewInventory', on_delete=models.CASCADE)

    def __str__(self):
        return f"EOL Tracking for {self.old_product_name}"


class HeatTracking(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50)
    product_spec = models.TextField(null=True, blank=True)
    recorded_temp = models.CharField(max_length=50)
    recorded_date = models.DateTimeField()
    resolution = models.TextField()

    def __str__(self):
        return f"Heat Tracking for {self.product_name}"


class HistoryLog(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    log_type = models.CharField(max_length=50)
    log_content = models.TextField()
    action_by = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)  # Reference to CustomUser

    def __str__(self):
        return f"Log for {self.ticket.id} by {self.action_by}"


class Notification(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Reference to CustomUser
    notification_type = models.CharField(max_length=50)
    notification_content = models.TextField()
    notification_status = models.CharField(max_length=50)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.ticket.id} - {self.notification_type}"
