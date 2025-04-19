from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from decouple import config

@receiver(post_migrate, weak=False)
def create_superuser(sender, **kwargs):
    try:
        if sender.name == 'user':
            print("Running Post-Migrate")
            superuser_email=config('DJANGO_SUPERUSER_EMAIL',default='admin@example.com')
            superuser_username=config('DJANGO_SUPERUSER_USERNAME',default='admin')
            if not User.objects.filter(email=superuser_email).exists() and not User.objects.filter(username=superuser_username).exists():
                User.objects.create_superuser(
                    username=superuser_username,
                    email=superuser_email,
                    password=config('DJANGO_SUPERUSER_PASSWORD',default='pass'),
                    first_name=config('DJANGO_SUPERUSER_FIRST_NAME',default='admin'),
                    last_name=config("DJANGO_SUPERUSER_LAST_NAME",default="admin"),
                )
                print("Superuser created successfully")
            else:
                print("A superuser with this email or username already exists")
    except Exception as e:
        print(e)