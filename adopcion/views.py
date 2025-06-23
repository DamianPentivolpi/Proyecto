from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import UsuarioAdoptante, Administrador, Perro, Raza, Vacuna, Temperamento, SolicitudAdopcion, SistemaAdopcion, Historial, PerfilMascota
from .forms import LoginForm, RegistroForm, ConfiguracionUsuarioForm, RazaForm, PerroForm, ConfirmarAdopcionForm, VacunaForm, TemperamentoForm
# Create your views here.
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
               
                usuario = None
                tipo_usuario = None
                
                # Intentar buscar como adoptante
                try:
                    usuario = UsuarioAdoptante.objects.get(email=email, contraseña=password)
                    tipo_usuario = 'adoptante'
                except UsuarioAdoptante.DoesNotExist:
                    pass
                
                # intentar como administrador
                if not usuario:
                    try:
                        usuario = Administrador.objects.get(email=email, contraseña=password)
                        tipo_usuario = 'administrador'
                    except Administrador.DoesNotExist:
                        pass
                
                if usuario:
                    # Guardar información del usuario
                    request.session['usuario_dni'] = usuario.dni if hasattr(usuario, 'dni') else usuario.codigo_admin
                    request.session['usuario_nombre'] = usuario.nombre
                    request.session['usuario_email'] = usuario.email
                    request.session['tipo_usuario'] = tipo_usuario
                    
                    messages.success(request, f'Bienvenido {usuario.nombre} ({usuario.get_tipo_usuario()})!')
                    
                    # administrador inicio
                    if tipo_usuario == 'administrador':
                        return redirect('adminpantalla')  
                    else:
                        return redirect('lista')
                else:
                    messages.error(request, 'Email o contraseña incorrectos')
                    
            except Exception as e:
                messages.error(request, f'Error en el sistema: {str(e)}')
    else:
        form = LoginForm()
    
    return render(request, 'index.html', {'form': form})
## registro de usuario
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                nuevo_usuario = UsuarioAdoptante.objects.create(
                    nombre=form.cleaned_data['nombre'],
                    dni=form.cleaned_data['dni'],
                    email=form.cleaned_data['email'],
                    contraseña=form.cleaned_data['password']
                )
                messages.success(request, 'Usuario registrado')
                return redirect('index')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form})

def lista(request):
    # Verificar si el usuario
    if 'usuario_dni' not in request.session:
        messages.error(request, 'Debe iniciar sesión para ver la lista')
        return redirect('index')
    
    # LISTA de preferencias 
    raza_filtro = request.GET.get('raza', '')
    edad_filtro = request.GET.get('edad', '')
    tamaño_filtro = request.GET.get('tamaño', '')
    busqueda = request.GET.get('busqueda', '')  
    orden = request.GET.get('orden', 'nombre')  
    
    # lista de perros disponibles 
    perros_disponibles = Perro.objects.filter(estado='disponible').select_related('raza')
    
    # busca segun preferencias 
    if raza_filtro:
        perros_disponibles = perros_disponibles.filter(raza__tipo_raza__icontains=raza_filtro)
    
    if edad_filtro:
        perros_disponibles = perros_disponibles.filter(edad=edad_filtro)
    
    if tamaño_filtro:
        perros_disponibles = perros_disponibles.filter(raza__tamaño=tamaño_filtro)
    
    # busqueda en tiempo real
    if busqueda:
        perros_disponibles = perros_disponibles.filter(
            Q(nombre__icontains=busqueda) |
            Q(raza__tipo_raza__icontains=busqueda)
        )
    
    # ordena segun preferencias 
    if orden == 'edad':
        perros_disponibles = perros_disponibles.order_by('edad')
    elif orden == 'nombre':
        perros_disponibles = perros_disponibles.order_by('nombre')
    elif orden == 'raza':
        perros_disponibles = perros_disponibles.order_by('raza__tipo_raza')
    
    # crea listas de perfiles de perros 
    perfiles_perros = []
    for perro in perros_disponibles:
        perfil = PerfilMascota(perro)
        perfiles_perros.append(perfil.get_perfil_completo())
    
    # me muestra los datos de los perros 
    razas_disponibles = Raza.objects.filter(perro__estado='disponible').distinct()
    edades_disponibles = Perro.objects.filter(estado='disponible').values_list('edad', flat=True).distinct().order_by('edad')
    tamaños_disponibles = Raza.objects.filter(perro__estado='disponible').values_list('tamaño', flat=True).distinct()
    
    
    context = {
        'perros_disponibles': perros_disponibles,
        'perfiles_perros': perfiles_perros, 
        'razas_disponibles': razas_disponibles,
        'edades_disponibles': edades_disponibles,
        'tamaños_disponibles': tamaños_disponibles,
        'filtros_activos': {
            'raza': raza_filtro,
            'edad': edad_filtro,
            'tamaño': tamaño_filtro,
            'busqueda': busqueda,
            'orden': orden,
        },
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'email': request.session.get('usuario_email', '')
        }
    }
    
    return render(request, 'lista.html', context)
def perro_detalle(request, perro_id):
    # verifica el logueo
    if 'usuario_dni' not in request.session:
        messages.error(request, 'Debe iniciar sesión para ver los detalles')
        return redirect('index')
    
    # obtengo informacion del perro
    perro = get_object_or_404(Perro, id=perro_id)
    vacunas, _ = Vacuna.objects.get_or_create(perro=perro)
    temperamento, _ = Temperamento.objects.get_or_create(perro=perro)
    
    # verifica el estado de solicitud
    solicitud_existente = None
    try:
        usuario_actual = UsuarioAdoptante.objects.get(dni=request.session['usuario_dni'])
        solicitud_existente = SolicitudAdopcion.objects.filter(
            usuarioadop=usuario_actual,
            perroelegido=perro
        ).first()
    except UsuarioAdoptante.DoesNotExist:
        pass
    
    # verifica el estado del perro 
    perro_disponible = perro.estado == 'disponible'
    
    context = {
        'perro': perro,
        'vacunas': vacunas,
        'temperamento': temperamento,
        'solicitud_existente': solicitud_existente,
        'perro_disponible': perro_disponible,
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'email': request.session.get('usuario_email', '')
        }
    }
    
    return render(request, 'perro_detalle.html', context)
def solicitar_adopcion(request, perro_id):
    #  verifica el logueo
    if 'usuario_dni' not in request.session:
        messages.error(request, 'Debe iniciar sesión para solicitar adopción')
        return redirect('index')
    
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('perro_detalle', perro_id=perro_id)
    
    try:
        # guardo perro y usuario
        perro = get_object_or_404(Perro, id=perro_id)
        usuario_actual = UsuarioAdoptante.objects.get(dni=request.session['usuario_dni'])
        
        # Verificar que el perro esté disponible
        if perro.estado != 'disponible':
            messages.error(request, f'{perro.nombre} no está disponible para adopción')
            return redirect('perro_detalle', perro_id=perro_id)
        
        # verifica si hay solicitud
        solicitud_existente = SolicitudAdopcion.objects.filter(
            usuarioadop=usuario_actual,
            perroelegido=perro
        ).first()
        
        if solicitud_existente:
            messages.warning(request, f'Ya tienes una solicitud pendiente para {perro.nombre}')
            return redirect('perro_detalle', perro_id=perro_id)
        
        # Crea la solicitud 
        solicitud = SolicitudAdopcion.objects.create(
            usuarioadop=usuario_actual,
            perroelegido=perro
        )
        
        # Crea el sistema de adopción
        sistema_adopcion = SistemaAdopcion.objects.create(
            peticion_adopcion=solicitud,
            fecha=timezone.now().date(),
            confirmar=False  
        )
        
        # Cambia el estado del perro a reservado
        perro.estado = 'reservado'
        perro.save()
        
        # Crea registro en el historial
        historial = Historial.objects.create(
            usuario=usuario_actual,
            fecha=sistema_adopcion,
            perro_adoptado=perro,
            adopcion_completada=False  
        )
        
        messages.success(request, f'¡Solicitud de adopción enviada exitosamente para {perro.nombre}! El perro ha sido reservado.')
        return redirect('perro_detalle', perro_id=perro_id)
        
    except Exception as e:
        messages.error(request, f'Error al procesar la solicitud: {str(e)}')
        return redirect('perro_detalle', perro_id=perro_id)

def confusu(request):
    #  verifica el logueo
    if 'usuario_dni' not in request.session:
        messages.error(request, 'Debe iniciar sesión para acceder a la configuración')
        return redirect('index')
    
    # obtengo el usuario acutal
    try:
        usuario_actual = UsuarioAdoptante.objects.get(dni=request.session['usuario_dni'])
    except UsuarioAdoptante.DoesNotExist:
        # ve si esta existe el usuario
        request.session.flush()
        messages.error(request, 'Usuario no encontrado. Por favor inicie sesión nuevamente.')
        return redirect('index')
    
    #me guarda el historial de adopciones
    historial_adopciones = Historial.objects.filter(
        usuario=usuario_actual
    ).select_related('perro_adoptado', 'perro_adoptado__raza', 'fecha', 'fecha__peticion_adopcion').order_by('-fecha__fecha')
    
    if request.method == 'POST':
        form = ConfiguracionUsuarioForm(request.POST, usuario_actual=usuario_actual)
        if form.is_valid():
            try:
                # cambia el dni
                usuario_actual.nombre = form.cleaned_data['nombre']
                usuario_actual.email = form.cleaned_data['email']
                
                # actualiza la contraseña
                if form.cleaned_data.get('nueva_password'):
                    usuario_actual.contraseña = form.cleaned_data['nueva_password']
                
                usuario_actual.save()
                
                # actualiza la informacion
                request.session['usuario_nombre'] = usuario_actual.nombre
                request.session['usuario_email'] = usuario_actual.email
                request.session['usuario_dni'] = usuario_actual.dni
                
                messages.success(request, 'Información actualizada exitosamente')
                return redirect('confusu')
            except Exception as e:
                messages.error(request, f'Error al actualizar la información: {str(e)}')
    else:
        # llama el formulario de usuario
        form = ConfiguracionUsuarioForm(initial={
            'nombre': usuario_actual.nombre,
            'dni': usuario_actual.dni,
            'email': usuario_actual.email,
        }, usuario_actual=usuario_actual)
    
    return render(request, 'confusu.html', {
        'form': form,
        'usuario': usuario_actual,
        'historial_adopciones': historial_adopciones
    })

def logout(request):
    # deslogea al usuario borrando la sesion
    try:
        del request.session['usuario_dni']
        del request.session['usuario_nombre']
        del request.session['usuario_email']
        del request.session['tipo_usuario']
    except KeyError:
        pass
    messages.success(request, 'Has cerrado sesión')
    return redirect('index')

def admin_dashboard(request):
    # pregunta si es el admin
    if request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso no autorizado')
        return redirect('index')
    
    try:
        
        admin_actual = Administrador.objects.get(codigo_admin=request.session['usuario_dni'])
        
       #solicitudes de usuarios para aprobar
        solicitudes_pendientes = admin_actual.get_solicitudes_pendientes()
        puede_aprobar = admin_actual.puede_aprobar_solicitudes()
        

        
        context = {
            'admin': admin_actual,
           
            'puede_aprobar': puede_aprobar,
            'solicitudes_pendientes': solicitudes_pendientes,
            'usuario_actual': {
                'nombre': request.session.get('usuario_nombre', ''),
                'email': request.session.get('usuario_email', ''),
                'tipo': request.session.get('tipo_usuario', '')
            }
        }
        
        return render(request, 'admin/adminpantalla.html', context)
        
    except Administrador.DoesNotExist:
        messages.error(request, 'Administrador no encontrado')
        return redirect('index')
    except Exception as e:
        messages.error(request, f'Error en el sistema: {str(e)}')
        return redirect('index')

# como se muestra al admin la lista de perros 
def admin_perros_lista(request):
    """Lista completa de perros para administrador"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    # me mustra la info segun raza
    perros = Perro.objects.all().select_related('raza').order_by('-id')
    
    # Filtra perros
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        perros = perros.filter(estado=estado_filtro)
    
    context = {
        'perros': perros,
        'estados': Perro.estado.field.choices,
        'filtro_activo': estado_filtro,
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminperrolista.html', context)

#formulario para crear al perro
def admin_perro_crear(request):
    """Crear nuevo perro con vacunas y temperamento"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    if request.method == 'POST':
        perro_form = PerroForm(request.POST)
        vacuna_form = VacunaForm(request.POST)
        temperamento_form = TemperamentoForm(request.POST)
        
        if perro_form.is_valid() and vacuna_form.is_valid() and temperamento_form.is_valid():
            perro = perro_form.save()
            
            vacuna = vacuna_form.save(commit=False)
            vacuna.perro = perro
            vacuna.save()
            
            temperamento = temperamento_form.save(commit=False)
            temperamento.perro = perro
            temperamento.save()
            
            messages.success(request, f'Perro "{perro.nombre}" creado exitosamente con su información completa')
            return redirect('adminperrolista')
    else:
        perro_form = PerroForm()
        vacuna_form = VacunaForm()
        temperamento_form = TemperamentoForm()
    
    context = {
        'perro_form': perro_form,
        'vacuna_form': vacuna_form,
        'temperamento_form': temperamento_form,
        'accion': 'Crear',
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminperroform.html', context)

#formulario para editarlo
def admin_perro_editar(request, perro_id):
    """Editar perro existente con vacunas y temperamento"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    perro = get_object_or_404(Perro, id=perro_id)
    vacuna, _ = Vacuna.objects.get_or_create(perro=perro)
    temperamento, _ = Temperamento.objects.get_or_create(perro=perro)
    
    if request.method == 'POST':
        perro_form = PerroForm(request.POST, instance=perro)
        vacuna_form = VacunaForm(request.POST, instance=vacuna)
        temperamento_form = TemperamentoForm(request.POST, instance=temperamento)
        
        if perro_form.is_valid() and vacuna_form.is_valid() and temperamento_form.is_valid():
            perro_form.save()
            vacuna_form.save()
            temperamento_form.save()
            
            messages.success(request, f'Perro "{perro.nombre}" actualizado exitosamente con su información completa')
            return redirect('adminperrolista')
    else:
        perro_form = PerroForm(instance=perro)
        vacuna_form = VacunaForm(instance=vacuna)
        temperamento_form = TemperamentoForm(instance=temperamento)
    
    context = {
        'perro_form': perro_form,
        'vacuna_form': vacuna_form,
        'temperamento_form': temperamento_form,
        'perro': perro,
        'accion': 'Editar',
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminperroform.html', context)

#funcion para eliminar al perro
def admin_perro_eliminar(request, perro_id):
    """Eliminar perro"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    perro = get_object_or_404(Perro, id=perro_id)
    
    if request.method == 'POST':
        nombre_perro = perro.nombre
        perro.delete()
        messages.success(request, f'Perro "{nombre_perro}" eliminado exitosamente')
        return redirect('adminperrolista')
    
    context = {
        'perro': perro,
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminperroeliminar.html', context)

# lista de razas
def admin_razas_lista(request):
    """Lista de razas para administrador"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    razas = Raza.objects.all().order_by('tipo_raza')
    
    context = {
        'razas': razas,
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminrazalista.html', context)

#formulario para crear la raza
def admin_raza_crear(request):
    """Crear nueva raza"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    if request.method == 'POST':
        form = RazaForm(request.POST)
        if form.is_valid():
            raza = form.save()
            messages.success(request, f'Raza "{raza.tipo_raza}" creada exitosamente')
            return redirect('adminrazalista')
    else:
        form = RazaForm()
    
    context = {
        'form': form,
        'accion': 'Crear',
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminrazaform.html', context)
#formulario para editar la raza
def admin_raza_editar(request, raza_id):
    """Editar raza existente"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    raza = get_object_or_404(Raza, id=raza_id)
    
    if request.method == 'POST':
        form = RazaForm(request.POST, instance=raza)
        if form.is_valid():
            form.save()
            messages.success(request, f'Raza "{raza.tipo_raza}" actualizada exitosamente')
            return redirect('adminrazalista')
    else:
        form = RazaForm(instance=raza)
    
    context = {
        'form': form,
        'raza': raza,
        'accion': 'Editar',
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminrazaform.html', context)
#funcion para eliminar la raza
def admin_raza_eliminar(request, raza_id):
    """Eliminar raza"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    raza = get_object_or_404(Raza, id=raza_id)
    
    # Verificar si hay perros usando esta raza
    perros_con_raza = Perro.objects.filter(raza=raza).count()
    
    if request.method == 'POST':
        nombre_raza = raza.tipo_raza
        raza.delete()
        messages.success(request, f'Raza "{nombre_raza}" eliminada exitosamente')
        return redirect('adminrazalista')
    
    context = {
        'raza': raza,
        'perros_con_raza': perros_con_raza,
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminrazaeliminar.html', context)

# visual para confirmar adopcion
def admin_confirmar_adopcion(request, solicitud_id):
    """Confirmar adopción y cambiar estado del perro"""
    if 'usuario_dni' not in request.session or request.session.get('tipo_usuario') != 'administrador':
        messages.error(request, 'Acceso denegado. Solo administradores.')
        return redirect('index')
    
    solicitud = get_object_or_404(SolicitudAdopcion, id=solicitud_id)
    
    if request.method == 'POST':
        form = ConfirmarAdopcionForm(request.POST)
        if form.is_valid():
            try:
                # imprime la info
                print(f"Confirmando adopción para solicitud {solicitud_id}")
                print(f"Perro: {solicitud.perroelegido.nombre} - Estado actual: {solicitud.perroelegido.estado}")
                
                # cambia el estado del perro
                perro = solicitud.perroelegido
                perro.estado = 'adoptado'
                perro.save()
                print(f"Perro actualizado - Nuevo estado: {perro.estado}")
                
                # verifica si ya existe un sistema de adopcion
                try:
                    sistema_adopcion = SistemaAdopcion.objects.get(peticion_adopcion=solicitud)
                    print(f"SistemaAdopcion existente encontrado: {sistema_adopcion}")
                    sistema_adopcion.confirmar = True
                    sistema_adopcion.fecha = timezone.now().date()
                    sistema_adopcion.save()
                    print(f"SistemaAdopcion actualizado - confirmar: {sistema_adopcion.confirmar}")
                except SistemaAdopcion.DoesNotExist:
                    print("Creando nuevo SistemaAdopcion")
                    sistema_adopcion = SistemaAdopcion.objects.create(
                        peticion_adopcion=solicitud,
                        fecha=timezone.now().date(),
                        confirmar=True
                    )
                    print(f"Nuevo SistemaAdopcion creado: {sistema_adopcion}")
                
                # crea el registro en el historial
                historial = Historial.objects.create(
                    usuario=solicitud.usuarioadop,
                    fecha=sistema_adopcion,
                    perro_adoptado=perro,
                    adopcion_completada=True
                )
                print(f"Historial creado: {historial}")
                
                # verifica que los cambios se guardaron
                perro.refresh_from_db()
                sistema_adopcion.refresh_from_db()
                print(f"Verificación final - Perro estado: {perro.estado}")
                print(f"Verificación final - SistemaAdopcion confirmar: {sistema_adopcion.confirmar}")
                
                messages.success(request, f'Adopción de "{perro.nombre}" confirmada exitosamente')
                return redirect('adminpantalla')
                
            except Exception as e:
                print(f"Error en confirmar adopción: {str(e)}")
                messages.error(request, f'Error al confirmar la adopción: {str(e)}')
                
    else:
        form = ConfirmarAdopcionForm()
    # me muestra la info
    context = {
        'form': form,
        'solicitud': solicitud,
        'perro': solicitud.perroelegido,
        'adoptante': solicitud.usuarioadop,
        'usuario_actual': {
            'nombre': request.session.get('usuario_nombre', ''),
            'tipo': request.session.get('tipo_usuario', '')
        }
    }
    
    return render(request, 'admin/adminconfirmaradop.html', context)