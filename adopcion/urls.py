from django.urls import path
from .views import (
    registro, index, lista, confusu, logout, perro_detalle, solicitar_adopcion, 
    admin_dashboard, admin_perros_lista, admin_perro_crear, 
    admin_perro_editar, admin_perro_eliminar, admin_razas_lista, admin_raza_crear,
    admin_raza_editar, admin_raza_eliminar, admin_confirmar_adopcion
)



urlpatterns = [
   ##urls inicio
    path('', index, name='index'),
    path('registro/', registro, name='registro'),
    ##urls usuario
    path('lista/', lista, name='lista'),
    path('confusu/', confusu, name='confusu'),
    path('logout/', logout, name='logout'),
    path('perro/<int:perro_id>/', perro_detalle, name='perro_detalle'),
    path('perro/<int:perro_id>/solicitar/', solicitar_adopcion, name='solicitar_adopcion'),

    # URLs para administrador 
    path('administrador/dashboard/', admin_dashboard, name='adminpantalla'),
    path('administrador/perros/', admin_perros_lista, name='adminperrolista'),
    path('administrador/perros/crear/', admin_perro_crear, name='adminperrocrear'),
    path('administrador/perros/<int:perro_id>/editar/', admin_perro_editar, name='adminperroeditar'),
    path('administrador/perros/<int:perro_id>/eliminar/', admin_perro_eliminar, name='adminperroeliminar'),
    path('administrador/razas/', admin_razas_lista, name='adminrazalista'),
    path('administrador/razas/crear/', admin_raza_crear, name='adminrazacrear'),
    path('administrador/razas/<int:raza_id>/editar/', admin_raza_editar, name='adminrazaeditar'),
    path('administrador/razas/<int:raza_id>/eliminar/', admin_raza_eliminar, name='adminrazaeliminar'),
    path('administrador/solicitud/<int:solicitud_id>/confirmar/', admin_confirmar_adopcion, name='adminconfirmaradop'),

]