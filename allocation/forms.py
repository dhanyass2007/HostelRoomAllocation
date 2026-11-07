
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Block, Room, StudentProfile


# --------------------------------
# BLOCK FORM
# --------------------------------

class BlockForm(forms.ModelForm):

    class Meta:
        model = Block
        fields = ['block_name']

        widgets = {
            'block_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter block name'
            }),
        }


# --------------------------------
# ROOM FORM
# --------------------------------

class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = ['block', 'room_number', 'capacity']

        widgets = {
            'block': forms.Select(attrs={
                'class': 'form-select'
            }),

            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room number'
            }),

            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room capacity',
                'min': 1
            }),
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')

        if capacity is not None and capacity < 1:
            raise forms.ValidationError(
                "Room capacity must be at least 1."
            )

        return capacity


# --------------------------------
# STUDENT REGISTRATION FORM
# --------------------------------

class StudentRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )

    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
    )

    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number'
        })
    )

    department = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter department'
        })
    )

    year = forms.IntegerField(
        min_value=1,
        max_value=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter year',
            'min': 1,
            'max': 6
        })
    )

    class Meta:
        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
        }

    def save(self, commit=True):

        user = super().save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'phone': self.cleaned_data['phone'],
                    'department': self.cleaned_data['department'],
                    'year': self.cleaned_data['year'],
                }
            )

        return user
