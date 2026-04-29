"""
Management command to create a coordinator account.

Usage:
    python manage.py create_coordinator --username john_coord --email john@example.com --first-name John --last-name Doe
"""

from django.core.management.base import BaseCommand
from auth_app.models import User


class Command(BaseCommand):
    help = 'Create a new coordinator account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Coordinator username')
        parser.add_argument('--email', type=str, required=True, help='Coordinator email')
        parser.add_argument('--password', type=str, help='Coordinator password (will prompt if not provided)')
        parser.add_argument('--first-name', type=str, default='', help='First name')
        parser.add_argument('--last-name', type=str, default='', help='Last name')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'Error: User with username "{username}" already exists!')
            )
            return

        # If password not provided, prompt for it
        if not password:
            password = self.getpass('Enter password for coordinator: ')
            password_confirm = self.getpass('Confirm password: ')
            
            if password != password_confirm:
                self.stdout.write(
                    self.style.ERROR('Error: Passwords do not match!')
                )
                return

        try:
            # Create coordinator user
            coordinator = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='COORDINATOR',
                first_name=first_name,
                last_name=last_name
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Coordinator "{username}" created successfully!\n'
                    f'  Email: {email}\n'
                    f'  Name: {first_name} {last_name}\n'
                    f'  Role: COORDINATOR'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating coordinator: {str(e)}')
            )
