from django.db import models
from django.conf import settings  # Use AUTH_USER_MODEL for user references
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver


# Custom user model extending AbstractUser
class CustomUser(AbstractUser):
    role_choices = [('admin', 'Admin'), ('technician', 'Technician')]
    role = models.CharField(max_length=50, choices=role_choices)

    def __str__(self):
        return self.username


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
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)  # Assign to CustomUser
    assigned_date = models.DateTimeField(null=True, blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True)

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

        # Log for debugging purposes
        if least_busy_technician:
            print(f"Assigning to {least_busy_technician.username}, Open Tickets: {least_busy_technician.open_ticket_count}")
        else:
            print("No technician found.")

        # Assign the ticket to the least busy technician if one exists
        if least_busy_technician:
            self.assignee = least_busy_technician
        else:
            print("Technician could not be assigned.")



    def save(self, *args, **kwargs):
        # Save the ticket to generate a primary key if it hasn't been saved before
        if not self.pk:
            super(Ticket, self).save(*args, **kwargs)

        # Automatically assign to the least busy technician if not assigned
        if not self.assignee:
            self.assign_to_technician()

        # Log which technician is assigned
        if self.assignee:
            print(f"Ticket {self.title} assigned to {self.assignee.username}")

        # Save the ticket again with the assignee now set
        super(Ticket, self).save(*args, **kwargs)


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
