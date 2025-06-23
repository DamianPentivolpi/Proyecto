from django.core.management.base import BaseCommand
from adopcion.models import Administrador
import argparse

class Command(BaseCommand):
    help = 'Crea un nuevo administrador con los datos especificados.'

    def add_arguments(self, parser):
        parser.add_argument('codigo_admin', type=str, help='El código único para el nuevo administrador (ej: ADMIN002)')
        parser.add_argument('nombre', type=str, help='El nombre completo del administrador')
        parser.add_argument('email', type=str, help='El email del administrador')
        parser.add_argument('contraseña', type=str, help='La contraseña para el nuevo administrador')
        
        # Argumento opcional para evitar la aprobación de adopciones
        parser.add_argument(
            '--no-aprobar',
            action='store_false',
            dest='puede_aprobar',
            help='Usar esta bandera para que el admin no pueda aprobar adopciones'
        )

    def handle(self, *args, **options):
        codigo_admin = options['codigo_admin']
        nombre = options['nombre']
        email = options['email']
        password = options['contraseña']
        puede_aprobar = options['puede_aprobar']

        try:
            # Verificar si ya existe un admin con ese código o email
            if Administrador.objects.filter(codigo_admin=codigo_admin).exists():
                self.stdout.write(self.style.ERROR(f'Ya existe un administrador con el código {codigo_admin}'))
                return
            
            if Administrador.objects.filter(email=email).exists():
                self.stdout.write(self.style.ERROR(f'Ya existe un administrador con el email {email}'))
                return

            # Crear el nuevo administrador
            admin = Administrador.objects.create(
                codigo_admin=codigo_admin,
                nombre=nombre,
                email=email,
                contraseña=password,
                puede_aprobar_adopciones=puede_aprobar,
                activo=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Administrador creado exitosamente:\n'
                    f'   Código: {admin.codigo_admin}\n'
                    f'   Nombre: {admin.nombre}\n'
                    f'   Email: {admin.email}\n'
                    f'   Puede Aprobar: {admin.puede_aprobar_adopciones}'
                )
            )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear administrador: {str(e)}')
            ) 