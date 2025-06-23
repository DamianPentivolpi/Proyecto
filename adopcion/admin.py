from django.contrib import admin
from .models import Perro,Raza,Vacuna,Temperamento,UsuarioAdoptante,SolicitudAdopcion,SistemaAdopcion,Historial
from .models import Raza
# Register your models here.
admin.site.register(Perro)
admin.site.register(Raza)
admin.site.register(Vacuna)
admin.site.register(Temperamento)
admin.site.register(UsuarioAdoptante)
admin.site.register(SolicitudAdopcion)
admin.site.register(Historial)
admin.site.register(SistemaAdopcion)