from django.db import models

# Enums
class EstadoMascota(models.TextChoices):
    DISPONIBLE = 'disponible', 'Disponible'
    RESERVADO = 'reservado', 'Reservado'
    ADOPTADO = 'adoptado', 'Adoptado'

class Tamaño(models.TextChoices):
    MINIATURA = 'miniatura', 'Miniatura'
    PEQUEÑO = 'pequeño', 'Pequeño'
    MEDIANO = 'mediano', 'Mediano'
    GRANDE = 'grande', 'Grande'
    GIGANTE = 'gigante', 'Gigante'

class EstadoSalud(models.TextChoices):
    SANO = 'sano', 'Sano'
    EN_TRATAMIENTO = 'tratamiento', 'En tratamiento'
    ENFERMO = 'enfermo', 'Enfermo'

class TipoUsuario(models.TextChoices):
    ADOPTANTE = 'adoptante', 'Adoptante'
    ADMINISTRADOR = 'administrador', 'Administrador'


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    contraseña = models.CharField(max_length=128)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def get_info_basica(self):
        return f"{self.nombre} - {self.email}"
    
    def esta_activo(self):
        return self.activo
    
    def get_tipo_usuario(self):
        raise NotImplementedError("Tipo de usuario get_tipo_usuario")
    
    def puede_adoptar(self):
        return self.esta_activo()
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_usuario()})"

# perro

class Raza(models.Model):
    tipo_raza = models.CharField(max_length=30)
    tamaño = models.CharField(
        max_length=10,
        choices=Tamaño.choices,
        default=Tamaño.MINIATURA
    )
    peso = models.IntegerField()

    def __str__(self):
        return f"{self.tipo_raza}"

class Perro(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    estado_salud = models.CharField(
        max_length=50,
        choices=EstadoSalud.choices,
        default=EstadoSalud.SANO)
    estado = models.CharField(
        max_length=10,
        choices=EstadoMascota.choices,
        default=EstadoMascota.DISPONIBLE
    )
    raza = models.ForeignKey(Raza, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.raza})"

class Vacuna(models.Model):
    perro = models.OneToOneField(Perro, on_delete=models.CASCADE, null=True, blank=True)
    moquillo_canino = models.BooleanField(null=True, blank=True)
    parvovirus = models.BooleanField(null=True, blank=True)
    hepatitis_infecciosa_canina = models.BooleanField(null=True, blank=True)
    rabia = models.BooleanField(null=True, blank=True)
    leptos_pirosis = models.BooleanField(null=True, blank=True)
    
    def __str__(self):
        return f"Vacunas de {self.perro}"

class Temperamento(models.Model):
    perro = models.OneToOneField(Perro, on_delete=models.CASCADE, null=True, blank=True)
    enojado = models.BooleanField(null=True, blank=True)
    tranquilo = models.BooleanField(null=True, blank=True)
    travieso = models.BooleanField(null=True, blank=True)
    alegre = models.BooleanField(null=True, blank=True)
    
    def __str__(self):
        return f"Temperamento de {self.perro}"

# Perfil
class PerfilMascota:
    
    def __init__(self, perro):
        self.perro = perro
        self.vacunas = None
        self.temperamento = None
        self._cargar_componentes()
    
    def _cargar_componentes(self):
        try:
            if hasattr(self.perro, 'vacuna'):
                self.vacunas = self.perro.vacuna
        except:
            pass
        
        try:
            if hasattr(self.perro, 'temperamento'):
                self.temperamento = self.perro.temperamento
        except:
            pass
    
    def get_perfil_completo(self):
        perfil = {
            'perro': self.perro,
            'info_basica': self.get_info_basica(),
            'vacunas': self._get_info_vacunas(),
            'temperamento': self._get_info_temperamento(),
        }
        return perfil
    
    def get_info_basica(self):
        return f"{self.perro.nombre} - {self.perro.edad} años - {self.perro.estado_salud}"
    
    
    def _get_info_vacunas(self):
        if self.vacunas:
            vacunas_aplicadas = []
            if self.vacunas.moquillo_canino:
                vacunas_aplicadas.append("Moquillo Canino")
            if self.vacunas.parvovirus:
                vacunas_aplicadas.append("Parvovirus")
            if self.vacunas.hepatitis_infecciosa_canina:
                vacunas_aplicadas.append("Hepatitis Infecciosa")
            if self.vacunas.rabia:
                vacunas_aplicadas.append("Rabia")
            if self.vacunas.leptos_pirosis:
                vacunas_aplicadas.append("Leptospirosis")
            return vacunas_aplicadas
        return []
    
    def _get_info_temperamento(self):
        if self.temperamento:
            caracteristicas = []
            if self.temperamento.enojado:
                caracteristicas.append("Enojado")
            if self.temperamento.tranquilo:
                caracteristicas.append("Tranquilo")
            if self.temperamento.travieso:
                caracteristicas.append("Travieso")
            if self.temperamento.alegre:
                caracteristicas.append("Alegre")
            return caracteristicas
        return []
    
    def es_apto_para_adopcion(self):
        if self.perro.estado != 'disponible':
            return False, "Perro no disponible"
        
        vacunas_basicas = ["Moquillo Canino", "Parvovirus", "Rabia"]
        vacunas_aplicadas = self._get_info_vacunas()
        vacunas_faltantes = [v for v in vacunas_basicas if v not in vacunas_aplicadas]
        
        if vacunas_faltantes:
            return False, f"Faltan vacunas: {', '.join(vacunas_faltantes)}"
        
        if self.temperamento and self.temperamento.enojado:
            return False, "Temperamento agresivo"
        
        return True, "Apto para adopción"

# usuario
class UsuarioAdoptante(Usuario):
    dni = models.CharField(max_length=20, primary_key=True)
    
    def get_tipo_usuario(self):
        return "Adoptante"
    
    def get_info_completa(self):
        info_basica = self.get_info_basica()
        return f"{info_basica} - DNI: {self.dni} "
    
    def puede_adoptar(self):
        if not super().puede_adoptar():
            return False
        
        if not self.dni or len(self.dni) < 7:
            return False
        
        return True
    
    def get_historial_adopciones(self):
        return Historial.objects.filter(usuario=self)

# Admin
class Administrador(Usuario):
    codigo_admin = models.CharField(max_length=10, unique=True)
    puede_aprobar_adopciones = models.BooleanField(default=True)
    
    def get_tipo_usuario(self):
        return "Administrador"
    
    def get_info_completa(self):
        info_basica = self.get_info_basica()
        return f"{info_basica} - Código: {self.codigo_admin}"
    
    def puede_adoptar(self):
        return False
    
    def puede_aprobar_solicitudes(self):
        return self.puede_aprobar_adopciones and self.esta_activo()
    
    def get_solicitudes_pendientes(self):
        solicitudes = SolicitudAdopcion.objects.all().select_related('usuarioadop', 'perroelegido')
        
        # filtro de solicitudes
        solicitudes_pendientes = []
        for solicitud in solicitudes:
            try:
                sistema_adopcion = SistemaAdopcion.objects.get(peticion_adopcion=solicitud)
                if not sistema_adopcion.confirmar:
                    solicitudes_pendientes.append(solicitud)
            except SistemaAdopcion.DoesNotExist:
                solicitudes_pendientes.append(solicitud)
        
        return solicitudes_pendientes

# Solicitud
class SolicitudAdopcion(models.Model):
    usuarioadop = models.ForeignKey(UsuarioAdoptante, on_delete=models.CASCADE, null=True, blank=True)
    perroelegido = models.ForeignKey(Perro, on_delete=models.CASCADE, null=True, blank=True)
    
    def get_peticion(self):
        return f"{self.usuarioadop} - {self.perroelegido}"
    
    def __str__(self):
        return f"Solicitud de {self.usuarioadop}"

#sistema de adopcion
class SistemaAdopcion(models.Model):
    peticion_adopcion = models.ForeignKey(SolicitudAdopcion, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateField()
    confirmar = models.BooleanField(null=True, blank=True)

    
    def __str__(self):
        return f"Peticion de {self.peticion_adopcion}"

#Historial
class Historial(models.Model):
    usuario = models.ForeignKey(UsuarioAdoptante, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.ForeignKey(SistemaAdopcion, on_delete=models.CASCADE, null=True, blank=True)
    perro_adoptado = models.ForeignKey(Perro, on_delete=models.CASCADE, null=True, blank=True)
    adopcion_completada = models.BooleanField(default=False, verbose_name="Adopción Completada")
    
    def __str__(self):
        return f"Historial {self.usuario}"
    