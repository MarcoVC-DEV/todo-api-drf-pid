# Todo API - Task Management System

## Descripción del Proyecto

Este proyecto es una API RESTful desarrollada con Django y Django REST Framework (DRF) para la gestión de tareas, espacios de trabajo y etiquetas. Está diseñada para facilitar la organización y colaboración en equipos, permitiendo a los usuarios crear, asignar y completar tareas dentro de espacios de trabajo compartidos. Este proyecto tiene como objetivo cumplir con los requisitos de una asignatura de prácticas laborales y se encuentra aún en desarrollo.

### Características principales:
- Gestión de espacios de trabajo: creación, edición, eliminación y asignación de usuarios.
- Gestión de tareas: creación, asignación, filtrado, búsqueda y finalización de tareas.
- Gestión de etiquetas: creación y asignación de etiquetas a tareas.
- Autenticación y autorización: basada en tokens JWT para garantizar la seguridad.
- Documentación interactiva con Swagger.

El proyecto está desplegado y accesible en la siguiente URL:  
**[https://todo-api-drf-pid.onrender.com](https://todo-api-drf-pid.onrender.com)**

Para consultar la documentación interactiva de la API, visita:  
**[https://todo-api-drf-pid.onrender.com/swagger/](https://todo-api-drf-pid.onrender.com/swagger/)**

---

## Instalación

Sigue los pasos a continuación para instalar y ejecutar el proyecto localmente:

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```
### 2. Crear y activar un entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```
### 3. Instalar las dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Configurar las variables de entorno
```bash
SECRET_KEY=tu_clave_secreta
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3  # O configura tu base de datos preferida
```
### 5. Aplicar las migraciones
```bash
python manage.py migrate
```
### 6. Crear un superusuario (opcional)
```bash
python manage.py createsuperuser
```
### 7. Ejecutar el servidor
```bash
python manage.py runserver
```

### Documentación interactiva
Para explorar y probar los endpoints de la API, utiliza la documentación Swagger disponible en:
https://todo-api-drf-pid.onrender.com/swagger/

### Ejemplo de solicitud
```bash
curl -X POST https://todo-api-drf-pid.onrender.com/todo/workspaces/1/tasks/ \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "title": "Nueva tarea",
  "status": "pending",
  "tags": [1, 2]
}'
```
### Tecnologías utilizadas
Lenguaje: Python
Frameworks: Django, Django REST Framework
Base de datos: PostgreSQL (o SQLite para desarrollo local)
Despliegue: Render
Documentación: Swagger (drf-yasg)

### Contribuciones
Si deseas contribuir al proyecto, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad (git checkout -b feature/nueva-funcionalidad).
3. Realiza tus cambios y haz commit (git commit -m "Añadir nueva funcionalidad").
4. Sube tus cambios (git push origin feature/nueva-funcionalidad).
5. Abre un Pull Request.
