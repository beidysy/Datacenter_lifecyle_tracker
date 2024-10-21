from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Ticket
from .forms import TicketForm  # Assuming you have a form for Ticket
from django.utils import timezone
from django.db.models import Count


@login_required
def tickets_list(request):
    try:
        # If the user is a technician, show only their assigned tickets
        if hasattr(request.user, 'technicianprofile') and request.user.technicianprofile.role == 'technician':
            tickets = Ticket.objects.filter(assignee=request.user)
        else:  # If the user is an admin or no TechnicianProfile, show all tickets
            tickets = Ticket.objects.all()

        # Debugging: Print the list of all tickets
        print("Total tickets in view: ", tickets)

    except AttributeError:
        # If there is an issue accessing technicianprofile, treat user as admin
        tickets = Ticket.objects.all()

    # Set up pagination: 10 tickets per page (you can adjust this number)
    paginator = Paginator(tickets, 10)

    # Get the page number from the request GET parameter
    page_number = request.GET.get('page')

    # Get the appropriate page of tickets
    page_obj = paginator.get_page(page_number)

    return render(request, 'tickets/tickets_list.html', {'page_obj': page_obj})


@login_required
def ticket_detail(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def ticket_edit(request, id):
    ticket = get_object_or_404(Ticket, pk=id)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            if ticket.assignee and not ticket.assigned_date:
                ticket.assigned_date = timezone.now()
            ticket.save()
            return redirect('ticket_detail', id=ticket.id)
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/ticket_edit.html', {'form': form, 'ticket': ticket})


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)

            # Automatically assign the ticket to the least busy technician if no assignee
            if not ticket.assignee:
                assign_to_least_busy_technician(ticket)

            if ticket.assignee and not ticket.assigned_date:
                ticket.assigned_date = timezone.now()  # Automatically set assigned date
            ticket.save()
            return redirect('tickets_list')
    else:
        form = TicketForm()

    return render(request, 'tickets/ticket_form.html', {'form': form})


@login_required
def ticket_delete(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    if request.method == 'POST':
        ticket.delete()
        return redirect('tickets_list')  # Redirect to the tickets list after deletion
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})


def assign_to_least_busy_technician(ticket):
    # Get all technicians ordered by the number of tickets assigned to them
    least_busy_technician = CustomUser.objects.filter(role='technician').annotate(ticket_count=Count('ticket')).order_by('ticket_count').first()

    if least_busy_technician:
        ticket.assignee = least_busy_technician
        ticket.save()


# @login_required
# def technicians_with_tickets(request):
#     # Fetch all technicians and their assigned tickets
#     technicians = CustomUser.objects.filter(role='technician').prefetch_related('ticket_set')
#     context = {'technicians': technicians}
#     return render(request, 'tickets/technicians_with_tickets.html', context)

@login_required
def technicians_with_tickets(request):
    technicians = CustomUser.objects.filter(role='technician').prefetch_related('ticket_set')
    context = {'technicians': technicians}
    return render(request, 'tickets/technicians_with_tickets.html', context)