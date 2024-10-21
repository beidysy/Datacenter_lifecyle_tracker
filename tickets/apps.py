import os
from django.apps import AppConfig

class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        # Import signals to ensure they are registered
        import tickets.signals

        # Only start the scheduler when running the server (not during migrations or other management commands)
        if os.environ.get('RUN_MAIN') == 'true':  # This ensures it's not run during "migrate" or "makemigrations"
            from .scheduler import start_scheduler
            start_scheduler()
