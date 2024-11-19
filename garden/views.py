from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Q
import csv 
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import GardenPlot, VolunteerEvent, CropRecord, UserProfile
from .forms import CropRecordForm
from django.conf import settings
from twilio.rest import Client
from .models import Analytics
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

@staff_member_required
def analytics_dashboard(request):
    analytics = Analytics.objects.all().order_by('-timestamp')  # Get all analytics, latest first
    return render(request, 'garden/analytics_dashboard.html', {'analytics': analytics})

@staff_member_required
def export_analytics_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics.csv"'

    writer = csv.writer(response)
    writer.writerow(['User', 'Action', 'Timestamp', 'Details'])  # Header row

    for entry in Analytics.objects.all():
        writer.writerow([
            entry.user.username,
            entry.action,
            entry.timestamp,
            entry.details
        ])

    return response

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')
            UserProfile.objects.create(user=user, phone_number=phone_number)

            Analytics.objects.create(user=user, action="SIGNUP")

            login(request, user)

            # Send SMS
            welcome_message = f"Welcome to the Community Garden, {user.username}!"
            send_sms(phone_number, welcome_message)
            
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'garden/signup.html', {'form': form})



def send_sms(to_phone_number, message):
    print("Preparing to send SMS...")  
    print(f"To: {to_phone_number}, Message: {message}") 

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        print(f"SMS sent successfully! Message SID: {message.sid}") 
        return message.sid
    except Exception as e:
        print(f"Failed to send SMS: {e}")  # Debug log
        return None

@login_required
def apply_for_plot(request, plot_id):
    plot = get_object_or_404(GardenPlot, id=plot_id)
    if request.method == 'POST':
        if plot.status == 'available':
            plot.status = 'pending'
            plot.assigned_gardener = request.user
            plot.save()
            messages.success(request, f"You've successfully applied for Plot {plot.plot_number}.")
        else:
            messages.error(request, "This plot is no longer available.")
    return redirect('plot_list')

# Home page
def home(request):
    if request.user.is_authenticated:
        # Render logged-in user homepage
        return render(request, 'garden/home_user.html')
    else:
        # Render guest homepage
        return render(request, 'garden/home.html')

# Signup view
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')  # Get the phone number

            # Save phone number to UserProfile
            UserProfile.objects.create(user=user, phone_number=phone_number)

            login(request, user)  # Log the user in

            # Send a welcome SMS
            welcome_message = f"Welcome to the Community Garden, {user.username}!"
            send_sms(phone_number, welcome_message)  # Send SMS to the provided phone number

            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'garden/signup.html', {'form': form})

# User login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'garden/login.html', {'form': form})

# User logout
def logout_view(request):
    logout(request)
    return redirect('home')

# List of garden plots
@login_required
def plot_list(request):
    query = request.GET.get('q')
    if query:
        plots = GardenPlot.objects.filter(
            Q(status__icontains=query) | Q(location__icontains=query)
        )
    else:
        plots = GardenPlot.objects.all()
    return render(request, 'garden/plot_list.html', {'plots': plots})

# Apply for a specific plot
@login_required
def apply_for_plot(request, plot_id):
    plot = get_object_or_404(GardenPlot, id=plot_id)
    if plot.status == 'available':
        plot.status = 'pending'
        plot.assigned_gardener = request.user
        plot.save()

        # Log analytics
        Analytics.objects.create(
            user=request.user,
            action="PLOT_APPLICATION",
            details={"plot_id": plot.id, "plot_number": plot.plot_number}
        )

        messages.success(request, 'You have successfully applied for the plot.')
    else:
        messages.error(request, 'This plot is not available.')
    return redirect('plot_list')


# Admin approval for plots
@login_required
def approve_plot(request, plot_id):
    plot = get_object_or_404(GardenPlot, id=plot_id)
    if plot.status == 'pending':
        plot.status = 'occupied'
        plot.save()

        # Send SMS to the gardener
        message = f"Your application for Plot {plot.plot_number} has been approved. Happy gardening!"
        send_sms(plot.assigned_gardener.profile.phone_number, message)

        messages.success(request, 'Plot has been approved, and the gardener has been notified by SMS.')
    else:
        messages.error(request, 'The plot is not in a pending state.')
    return redirect('plot_list')

# List of volunteer events
@login_required
def event_list(request):
    query = request.GET.get('q')
    if query:
        events = VolunteerEvent.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        events = VolunteerEvent.objects.all()

    # Add volunteer count to each event
    for event in events:
        event.volunteer_count = event.assigned_volunteers.count()

    return render(request, 'garden/event_list.html', {'events': events})

# Sign up for a volunteer event
@login_required
def event_list(request):
    query = request.GET.get('q')
    if query:
        events = VolunteerEvent.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        events = VolunteerEvent.objects.all()

    # Add remaining slots to each event
    for event in events:
        event.remaining_slots = event.volunteers_needed - event.assigned_volunteers.count()

    return render(request, 'garden/event_list.html', {'events': events})

# List of crop records
@login_required
def crop_record_list(request):
    query = request.GET.get('q')
    if query:
        records = CropRecord.objects.filter(
            gardener=request.user
        ).filter(
            Q(crop_type__icontains=query) | Q(notes__icontains=query)
        )
    else:
        records = CropRecord.objects.filter(gardener=request.user)

    # Get available plots for the logged-in user
    available_plots = GardenPlot.objects.filter(assigned_gardener=request.user, status='occupied')

    # Initialize the crop record form
    form = CropRecordForm(gardener=request.user)

    return render(request, 'garden/crop_record_list.html', {
        'records': records,
        'form': form,
        'available_plots': available_plots
    })

# Add a new crop record
@login_required
def add_crop_record(request):
    if request.method == 'POST':
        form = CropRecordForm(request.POST, gardener=request.user)
        if form.is_valid():
            form.instance.gardener = request.user  # Assign the logged-in user as the gardener
            form.save()
            messages.success(request, "Crop record added successfully.")
            return redirect('crop_record_list')
        else:
            # Pass the form back to the template with errors
            records = CropRecord.objects.filter(gardener=request.user)
            return render(request, 'garden/crop_record_list.html', {
                'records': records,
                'form': form,
                'errors': form.errors,
            })

@login_required
def sign_up_for_event(request, event_id):
    event = get_object_or_404(VolunteerEvent, id=event_id)
    if request.user in event.assigned_volunteers.all():
        messages.info(request, 'You have already signed up for this event.')
    elif event.assigned_volunteers.count() < event.volunteers_needed:
        event.assigned_volunteers.add(request.user)
        event.save()
        messages.success(request, f'You have successfully signed up for {event.title}.')
    else:
        messages.error(request, 'The event is full.')
    return redirect('event_list')

@login_required
def plot_chart_view(request):
    # Fetch plot data
    plots = GardenPlot.objects.all()
    # Prepare data for the chart
    plot_numbers = [plot.plot_number for plot in plots]
    plot_sizes = [plot.size for plot in plots]
    context = {
        'plot_numbers': plot_numbers,
        'plot_sizes': plot_sizes,
    }
    return render(request, 'garden/plot_chart.html', context)