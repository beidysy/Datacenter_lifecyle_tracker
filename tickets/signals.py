# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TechnicianProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_save_technician_profile(sender, instance, created, **kwargs):
    try:
        print(f"Signal triggered for user: {instance.username}, created: {created}")

        # Only create a TechnicianProfile if the user is a technician
        if instance.role == 'technician':
            if created:
                print(f"Creating profile for technician {instance.username}")
                TechnicianProfile.objects.create(user=instance)
            else:
                if hasattr(instance, 'technicianprofile'):
                    print(f"Saving profile for technician {instance.username}")
                    instance.technicianprofile.save()
        else:
            print(f"User {instance.username} is not a technician. No profile created.")
    except Exception as e:
        print(f"Error creating or saving technician profile: {e}")
