from django import forms
from .models import SignupRequest


class SignupRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de registro"""
    
    class Meta:
        model = SignupRequest
        fields = ['email', 'full_name', 'note']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre completo'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
        labels = {
            'email': 'Correo Electrónico',
            'full_name': 'Nombre Completo',
            'note': 'Notas',
        }
