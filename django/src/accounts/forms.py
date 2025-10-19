from django import forms
from django.contrib.auth.hashers import make_password
from .models import SignupRequest


class SignupRequestForm(forms.ModelForm):
    """Formulario para crear solicitudes de registro"""
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    
    class Meta:
        model = SignupRequest
        fields = ['email', 'full_name', 'note', 'password']
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
            'password': 'Contraseña',
        }

    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.password_hash = make_password(self.cleaned_data["password"])
        if commit:
            inst.save()
        return inst
