from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'ticket_type', 'status', 'priority', 'center', 'description']  # Add 'description' field , 'assignee' excluded

