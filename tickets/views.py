from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.db.models import Count
from .models import CustomUser, Ticket
from .forms import TicketForm

# Home page view
def home(request):
    return render(request, 'tickets/home.html')

# Redirect based on user role after login
@login_required
def redirect_dashboard(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'technician':
        return redirect('technician_dashboard')
    else:
        # Optional: Logout and redirect to home if role is unrecognized
        logout(request)
        return redirect('home')

# Admin dashboard showing all tickets
@login_required
def admin_dashboard(request):
    tickets = Ticket.objects.all()
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
    }
    return render(request, 'tickets/admin_dashboard.html', context)

# Technician dashboard showing only tickets assigned to the technician
@login_required
def technician_dashboard(request):
    tickets = Ticket.objects.filter(assignee=request.user).select_related('product')
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
    }
    return render(request, 'tickets/technician_dashboard.html', context)


# Contact admin view
def contact_admin(request):
    return render(request, 'tickets/contact_admin.html')

# Ticket list view (paginated)
@login_required
def tickets_list(request):
    try:
        if hasattr(request.user, 'technicianprofile') and request.user.technicianprofile.role == 'technician':
            tickets = Ticket.objects.filter(assignee=request.user)
        else:
            tickets = Ticket.objects.all()
    except AttributeError:
        tickets = Ticket.objects.all()

    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tickets/tickets_list.html', {'page_obj': page_obj})

# Ticket detail view
@login_required
def ticket_detail(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

# Edit ticket view
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

# Create a new ticket
# @login_required
# def ticket_create(request):
#     if request.method == 'POST':
#         form = TicketForm(request.POST)
#         if form.is_valid():
#             ticket = form.save(commit=False)
#             if not ticket.assignee:
#                 assign_to_least_busy_technician(ticket)
#             if ticket.assignee and not ticket.assigned_date:
#                 ticket.assigned_date = timezone.now()
#             ticket.save()
#             return redirect('tickets_list')
#     else:
#         form = TicketForm()
#     return render(request, 'tickets/ticket_form.html', {'form': form})
@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            # Check if product is assigned, otherwise assign automatically
            if not ticket.product:
                default_product = NewInventory.objects.filter(product_status='active').first()
                ticket.product = default_product
            
            # Automatically assign technician if not assigned
            if not ticket.assignee:
                ticket.assign_to_technician()
            
            ticket.save()
            return redirect('tickets_list')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})


# Delete a ticket
@login_required
def ticket_delete(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    if request.method == 'POST':
        ticket.delete()
        return redirect('tickets_list')
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})

# Assign ticket to the least busy technician
def assign_to_least_busy_technician(ticket):
    least_busy_technician = CustomUser.objects.filter(role='technician').annotate(ticket_count=Count('ticket')).order_by('ticket_count').first()
    if least_busy_technician:
        ticket.assignee = least_busy_technician
        ticket.save()

# Technicians and their assigned tickets
@login_required
def technicians_with_tickets(request):
    technicians = CustomUser.objects.filter(role='technician').prefetch_related('ticket_set')
    context = {'technicians': technicians}
    return render(request, 'tickets/technicians_with_tickets.html', context)
