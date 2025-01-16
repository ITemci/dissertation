from django import forms
from .models import Reservation
from django.utils import timezone
import datetime
from django.db import models

class ReservationForm(forms.ModelForm):
    available_times = [(f"{hour}:00", f"{hour}:00") for hour in range(10, 22)]  # Times from 10 AM to 9 PM

    time = forms.ChoiceField(choices=available_times, required=True)
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )

    class Meta:
        model = Reservation
        fields = ['date', 'time', 'num_tables']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter available times dynamically
        if 'date' in self.data:
            try:
                date = datetime.datetime.strptime(self.data.get('date'), '%Y-%m-%d').date()
                self.fields['time'].choices = self.get_available_times(date)
            except ValueError:
                pass

    def get_available_times(self, date):
        """
        Return a list of available times for the selected date.
        """
        if date < timezone.now().date():
            return []

        available_times = []
        for hour in range(10, 22):  # From 10:00 to 21:00
            time = f"{hour}:00"
            total_reserved = (
                    Reservation.objects.filter(date=date, time=time)
                    .aggregate(total=models.Sum('num_tables'))['total'] or 0
            )
            if total_reserved < 10:
                available_times.append((time, time))
        return available_times

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        num_tables = cleaned_data.get('num_tables', 1)

        if date < timezone.now().date():
            raise forms.ValidationError("The reservation date must be in the future.")

        if not Reservation.is_available(date, time, num_tables):
            raise forms.ValidationError("No tables are available for the selected date and time.")

        return cleaned_data
