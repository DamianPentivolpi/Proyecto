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


class Raza(models.Model):
    tipo_raza = models.CharField(max_length=30)
    tamaño = models.CharField(
        max_length=10,
        choices=Tamaño.choices,
        default=Tamaño.MINIATURA
    )
    peso = models.IntegerField()

    def __str__(self):
        return f"{self.tipo_raza} ({self.tamaño}, {self.peso}kg)"

class Perro(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    estado_salud = models.CharField(max_length=100)
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

class Temperamento(models.Model):
    perro = models.OneToOneField(Perro, on_delete=models.CASCADE, null=True, blank=True)
    enojado = models.BooleanField(null=True, blank=True)
    tranquilo = models.BooleanField(null=True, blank=True)
    travieso = models.BooleanField(null=True, blank=True)
    alegre = models.BooleanField(null=True, blank=True)



class UsuarioAdoptante(models.Model):
    nombre_usu = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, primary_key=True)
    email = models.EmailField(max_length=254, unique=True)
    contraseña = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.nombre_usu}"
    

class Preferencias(models.Model):
    pref_raza = models.ForeignKey(Raza, on_delete=models.CASCADE, null=True, blank=True)
    pref_edad = models.IntegerField()
    pref_tamaño = models.CharField(
        max_length=10,
        choices=Tamaño.choices,
        default=Tamaño.MINIATURA
    )

class SolicitudAdopcion(models.Model):
    usuarioadop = models.ForeignKey(UsuarioAdoptante, on_delete=models.CASCADE, null=True, blank=True)
    perroelegido = models.ForeignKey(Perro, on_delete=models.CASCADE, null=True, blank=True)
    peticion = "{usuarioadop}" + "{perroelegido}"

class SistemaAdopcion(models.Model):
    peticion_adopcion = models.ForeignKey(SolicitudAdopcion, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateField()
    confirmar = models.BooleanField(null=True, blank=True)

class Historial(models.Model):
    usuario = models.ForeignKey(UsuarioAdoptante, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.ForeignKey(SistemaAdopcion, on_delete=models.CASCADE, null=True, blank=True)
    perro_adoptado = models.ForeignKey(Perro, on_delete=models.CASCADE, null=True, blank=True)
    histo_pref = models.ForeignKey(Preferencias, on_delete=models.CASCADE, null=True, blank=True)