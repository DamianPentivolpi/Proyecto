# Proyecto de Adopción de Perros

Este es un proyecto de aplicación web desarrollado con Django para gestionar un sistema de adopción de perros.


-Cuenta usuario creada o crear: 
            email: Damian@gmail.com
            contraseña: chiqui1302

-Cuenta admin de gestion :
        email: damian@adminadop.com
        contra :  damianadop1302

-Cuenta admin django: 
            username: damian
            contraseña: damian1313

Lenguaje usado:

Python con el framework Django.
HTML con jinja, CSS.
SQLite (para desarrollo).

## Funcionalidades

La plataforma ofrece dos roles principales: Adoptante y Administrador

### Funcionalidades para Adoptantes

   Registro e Inicio de Sesión: Los usuarios pueden crear una cuenta y acceder a la plataforma.
   Ver Lista de Perros: Visualizar una lista de todos los perros disponibles para adopción.
   
   Filtrado y Búsqueda:
       Filtrar perros por raza, edad y tamaño.
       Ordenar la lista por nombre, edad o raza.
   
   Ver Detalles del Perro: Acceder a un perfil detallado para cada perro, que incluye información sobre sus vacunas y temperamento.
	
    Solicitar Adopción: Los usuarios pueden enviar una solicitud de adopción para un perro y ponerlos en reservados
   
   Gestión de Perfil:
       Actualizar su información personal (nombre, email, contraseña).
       Ver su historial de adopciones y el estado de sus solicitudes.

### Funcionalidades para Administradores
   Dashboard de Administrador: Un panel central para gestionar las operaciones del sitio.
   
   Gestión de Adopciones:
       Ver todas las solicitudes de adopción pendientes.
       Confirmar adopciones, lo que cambia el estado del perro a "adoptado" y completa el proceso.
   
   Gestión de Perros:
       Crear, Leer, Actualizar y Eliminar los perfiles de los perros.
       Listar todos los perros y filtrarlos por su estado (disponible, reservado, adoptado).
       Añadir y editar información completa del perro, incluyendo vacunas y temperamento.
   
   Gestión de Razas:
        Crear, Leer, Actualizar y Eliminar  las razas de perros.
       Evitar la eliminación de razas que ya están asociadas a algún perro. 