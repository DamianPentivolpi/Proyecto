from django import forms
from django.core.exceptions import ValidationError
from .models import UsuarioAdoptante, Perro, Raza, Vacuna, Temperamento

##LOGIN
class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'required': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'required': True
        })
    )
#registro
class RegistroForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre completo',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre completo',
            'required': True
        })
    )
    
    dni = forms.CharField(
        label='DNI',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678',
            'required': True
        })
    )
    
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'required': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'required': True
        })
    )

class ConfiguracionUsuarioForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre completo',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre completo',
            'required': True
        })
    )
    
    dni = forms.CharField(
        label='DNI',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': 'background-color: #f7fafc; color: #718096;'
        }),
        required=False
    )
    
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'required': True
        })
    )
    
    password_actual = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'required': False
        }),
        required=False
    )
    
    nueva_password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'required': False
        }),
        required=False
    )
    
    confirmar_nueva_password = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'required': False
        }),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.usuario_actual = kwargs.pop('usuario_actual', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password_actual = cleaned_data.get('password_actual')
        nueva_password = cleaned_data.get('nueva_password')
        confirmar_nueva_password = cleaned_data.get('confirmar_nueva_password')
        
        # Validar que el email no exista en otro usuario
        if email and self.usuario_actual:
            if UsuarioAdoptante.objects.filter(email=email).exclude(dni=self.usuario_actual.dni).exists():
                raise ValidationError('Este email ya está registrado por otro usuario')
        
        # Validar cambio de contraseña
        if nueva_password or confirmar_nueva_password:
            if not password_actual:
                raise ValidationError('Debe ingresar su contraseña actual para cambiarla')
            
            if not self.usuario_actual or self.usuario_actual.contraseña != password_actual:
                raise ValidationError('La contraseña actual es incorrecta')
            
            if nueva_password != confirmar_nueva_password:
                raise ValidationError('Las nuevas contraseñas no coinciden')
        
        return cleaned_data
    
    # FORMULARIOS PARA ADMINISTRADOR
class RazaForm(forms.ModelForm):
    """Formulario para gestionar razas"""
    class Meta:
        model = Raza
        fields = ['tipo_raza', 'tamaño', 'peso']
        widgets = {
            'tipo_raza': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Labrador, Pastor Alemán'
            }),
            'tamaño': forms.Select(attrs={
                'class': 'form-control'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peso en kg'
            })
        }

class VacunaForm(forms.ModelForm):
    """Formulario para gestionar vacunas del perro"""
    class Meta:
        model = Vacuna
        fields = ['moquillo_canino', 'parvovirus', 'hepatitis_infecciosa_canina', 'rabia', 'leptos_pirosis']
        widgets = {
            'moquillo_canino': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'parvovirus': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'hepatitis_infecciosa_canina': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'rabia': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'leptos_pirosis': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'moquillo_canino': 'Moquillo Canino',
            'parvovirus': 'Parvovirus',
            'hepatitis_infecciosa_canina': 'Hepatitis Infecciosa Canina',
            'rabia': 'Rabia',
            'leptos_pirosis': 'Leptospirosis'
        }

class TemperamentoForm(forms.ModelForm):
    """Formulario para gestionar temperamento del perro"""
    class Meta:
        model = Temperamento
        fields = ['enojado', 'tranquilo', 'travieso', 'alegre']
        widgets = {
            'enojado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tranquilo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'travieso': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'alegre': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'enojado': 'Enojado/Agresivo',
            'tranquilo': 'Tranquilo',
            'travieso': 'Travieso',
            'alegre': 'Alegre'
        }

class PerroForm(forms.ModelForm):
    """Formulario para gestionar perros con vacunas y temperamento"""
    class Meta:
        model = Perro
        fields = ['nombre', 'edad', 'estado_salud', 'estado', 'raza']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del perro'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Edad en años'
            }),
            'estado_salud': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'raza': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class ConfirmarAdopcionForm(forms.Form):
    """Formulario para confirmar adopción"""
    confirmar = forms.BooleanField(
        label='Confirmo que la adopción se ha completado exitosamente',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    observaciones = forms.CharField(
        label='Observaciones',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones sobre la adopción (opcional)'
        }),
        required=False
    ) 
