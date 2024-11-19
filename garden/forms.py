from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
from django import forms
from .models import CropRecord, GardenPlot

class CropRecordForm(forms.ModelForm):
    class Meta:
        model = CropRecord
        fields = ['plot', 'crop_type', 'planting_date', 'expected_harvest_date', 'notes']

    def __init__(self, *args, **kwargs):
        gardener = kwargs.pop('gardener', None)
        super().__init__(*args, **kwargs)
        if gardener:
            self.fields['plot'].queryset = GardenPlot.objects.filter(assigned_gardener=gardener)
            
class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        help_text="Enter a valid phone number, including the country code (e.g., +250123456789)."
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'phone_number')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters long.")
        if not re.match(r'^\w+$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+\d{10,15}$', phone_number):
            raise forms.ValidationError("Phone number must be in international format (e.g., +250123456789).")
        return phone_number

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password2