from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Reset auto-increment sequence for tickets'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='tickets_ticket';")
        self.stdout.write(self.style.SUCCESS('Successfully reset auto-increment sequence for tickets_ticket.'))
