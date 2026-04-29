import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone_tracker.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
email = 'admin@local.test'
password = 'admin'
first_name = 'Super'
last_name = 'Admin'

if User.objects.filter(username=username).exists():
    print(f"Superuser '{username}' already exists.")
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='ADMIN',
        first_name=first_name,
        last_name=last_name,
    )
    print('Superuser created successfully!')

