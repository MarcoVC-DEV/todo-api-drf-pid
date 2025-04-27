from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from decouple import config



# Este decorador indica que la función `create_superuser` será ejecutada automáticamente
# después de que se complete una migración en la aplicación Django. Esto se creó con el objetivo
# de crear un superusuario después de desplegar la aplicación en Render, ya que no permite
# interacción directa con la consola.

@receiver(post_migrate, weak=False)
def create_superuser(sender, **kwargs):
    try:
        # Verifica si el nombre del módulo que envía la señal es 'user'.
        # Esto asegura que la lógica solo se ejecute cuando las migraciones
        # de la aplicación 'user' se completen.
        if sender.name == 'user':
            print("Running Post-Migrate")  # Mensaje para indicar que la función se está ejecutando.

            # Obtiene el correo electrónico del superusuario desde las variables de entorno.
            # Si no se encuentra, utiliza un valor predeterminado.
            superuser_email = config('DJANGO_SUPERUSER_EMAIL', default='admin@example.com')

            # Obtiene el nombre de usuario del superusuario desde las variables de entorno.
            # Si no se encuentra, utiliza un valor predeterminado.
            superuser_username = config('DJANGO_SUPERUSER_USERNAME', default='admin')

            # Verifica si ya existe un usuario con el correo electrónico o nombre de usuario
            # especificado. Si no existe, procede a crear el superusuario.
            if not User.objects.filter(email=superuser_email).exists() and not User.objects.filter(username=superuser_username).exists():
                # Crea un superusuario con los datos obtenidos de las variables de entorno.
                User.objects.create_superuser(
                    username=superuser_username,
                    email=superuser_email,
                    password=config('DJANGO_SUPERUSER_PASSWORD', default='pass'),  # Contraseña del superusuario.
                    first_name=config('DJANGO_SUPERUSER_FIRST_NAME', default='admin'),  # Nombre del superusuario.
                    last_name=config("DJANGO_SUPERUSER_LAST_NAME", default="admin"),  # Apellido del superusuario.
                )
                print("Superuser created successfully")  # Mensaje indicando que el superusuario fue creado.
            else:
                # Si ya existe un usuario con el correo o nombre de usuario, muestra un mensaje.
                print("A superuser with this email or username already exists")
    except Exception as e:
        # Captura cualquier excepción que ocurra durante la ejecución y la imprime.
        print(e)