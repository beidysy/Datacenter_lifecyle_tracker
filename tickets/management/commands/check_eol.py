# from django.core.management.base import BaseCommand
# from datetime import timedelta, date
# from tickets.models import NewInventory, Ticket
# from django.db.models import Max
# from django.db.utils import IntegrityError

# class Command(BaseCommand):
#     help = 'Check for items close to EOL and generate tickets'

#     def handle(self, *args, **kwargs):
#         # Today's date
#         today = date.today()
#         self.stdout.write(self.style.NOTICE(f'Today is {today}'))

#         # Threshold for 5 days before EOL
#         threshold = today + timedelta(days=5)
#         self.stdout.write(self.style.NOTICE(f'Checking for items with EOL before {threshold}'))

#         # Get items where the EOL date is within the next 5 days
#         items_near_eol = NewInventory.objects.filter(eol__lte=threshold, eol__gt=today)

#         if not items_near_eol.exists():
#             self.stdout.write(self.style.WARNING('No items near EOL found'))
#         else:
#             self.stdout.write(self.style.SUCCESS(f'Found {items_near_eol.count()} items near EOL'))

#         for item in items_near_eol:
#             self.stdout.write(self.style.NOTICE(f"Checking item: {item.product_name}, Center: {item.center}, EOL: {item.eol}"))

#             # Ensure we filter existing tickets properly to avoid creating duplicates
#             existing_tickets = Ticket.objects.filter(
#                 ticket_type='EOL',
#                 center=item.center,
#                 title__icontains=item.product_name,  # This ensures the ticket matches the item
#                 status='open',  # Filter only open tickets
#                 priority='high'
#             )

#             # Print details of existing tickets
#             self.stdout.write(self.style.WARNING(f"Found {existing_tickets.count()} existing tickets for {item.product_name}"))

#             if not existing_tickets.exists():
#                 try:
#                     Ticket.objects.create(
#                         id=self.generate_unique_id(),  # Ensure a unique ID is provided
#                         ticket_type='EOL',
#                         status='open',
#                         priority='high',
#                         center=item.center,
#                         title=f"{item.product_name} nearing EOL on {item.eol}"  # Unique title for each item
#                     )
#                     self.stdout.write(self.style.SUCCESS(f'Ticket created for {item.product_name} nearing EOL'))
#                 except IntegrityError as e:
#                     self.stdout.write(self.style.ERROR(f"Failed to create ticket for {item.product_name}: {str(e)}"))
#             else:
#                 self.stdout.write(self.style.WARNING(f'Ticket already exists for {item.product_name}'))

#     def generate_unique_id(self):
#         """
#         Generates a unique ID for a new ticket by finding the maximum ID in the table
#         and incrementing it by 1. If no records exist, it returns 1 as the first ID.
#         """
#         max_id = Ticket.objects.all().aggregate(Max('id'))['id__max']
#         return max_id + 1 if max_id else 1



from django.core.management.base import BaseCommand
from datetime import timedelta, date
from tickets.models import NewInventory, Ticket
from django.db.models import Max
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Check for items close to EOL and generate tickets'

    def handle(self, *args, **kwargs):
        # Today's date
        today = date.today()
        self.stdout.write(self.style.NOTICE(f'Today is {today}'))

        # Threshold for 5 days before EOL
        threshold = today + timedelta(days=30)
        self.stdout.write(self.style.NOTICE(f'Checking for items with EOL before {threshold}'))

        # Get items where the EOL date is within the next 5 days
        items_near_eol = NewInventory.objects.filter(eol__lte=threshold, eol__gt=today)

        if not items_near_eol.exists():
            self.stdout.write(self.style.WARNING('No items near EOL found'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found {items_near_eol.count()} items near EOL'))

        for item in items_near_eol:
            self.stdout.write(self.style.NOTICE(f"Checking item: {item.product_name}, Center: {item.center}, EOL: {item.eol}"))

            # Ensure we filter existing tickets properly to avoid creating duplicates
            existing_tickets = Ticket.objects.filter(
                ticket_type='EOL',
                center=item.center,
                title__icontains=item.product_name,
                status='open',
                priority='high'
            )

            if not existing_tickets.exists():
                try:
                    Ticket.objects.create(
                        id=self.generate_unique_id(),
                        ticket_type='EOL',
                        status='open',
                        priority='high',
                        center=item.center,
                        title=f"{item.product_name} nearing EOL on {item.eol}"
                    )
                    self.stdout.write(self.style.SUCCESS(f'Ticket created for {item.product_name} nearing EOL'))
                except IntegrityError as e:
                    self.stdout.write(self.style.ERROR(f"Failed to create ticket for {item.product_name}: {str(e)}"))
            else:
                self.stdout.write(self.style.WARNING(f'Ticket already exists for {item.product_name}'))

    def generate_unique_id(self):
        max_id = Ticket.objects.all().aggregate(Max('id'))['id__max']
        return max_id + 1 if max_id else 1
# Hello