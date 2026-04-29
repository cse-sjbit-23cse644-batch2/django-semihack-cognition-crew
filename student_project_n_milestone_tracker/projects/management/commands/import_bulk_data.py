import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from projects.models import Domain, Class

User = get_user_model()

class Command(BaseCommand):
    help = 'Import users and classes from CSV files'
    
    def add_arguments(self, parser):
        parser.add_argument('--users', type=str, help='Path to users CSV file')
        parser.add_argument('--classes', type=str, help='Path to classes CSV file')
    
    def handle(self, *args, **options):
        if options.get('users'):
            self.import_users(options['users'])
        
        if options.get('classes'):
            self.import_classes(options['classes'])
        
        if not options.get('users') and not options.get('classes'):
            raise CommandError('Please provide --users and/or --classes file paths')
    
    def import_users(self, filepath):
        """
        CSV format: username,email,first_name,last_name,role,domain
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                created_count = 0
                updated_count = 0
                
                for row in reader:
                    username = row['username'].strip()
                    email = row['email'].strip()
                    role = row.get('role', 'STUDENT').strip()
                    domain_name = row.get('domain', '').strip()
                    
                    domain = None
                    if domain_name:
                        domain, _ = Domain.objects.get_or_create(name=domain_name)
                    
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': row.get('first_name', '').strip(),
                            'last_name': row.get('last_name', '').strip(),
                            'role': role,
                            'domain': domain,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'Users imported: {created_count} created, {updated_count} existed'))
        
        except FileNotFoundError:
            raise CommandError(f'File not found: {filepath}')
        except Exception as e:
            raise CommandError(f'Error importing users: {str(e)}')
    
    def import_classes(self, filepath):
        """
        CSV format: code,name,domain,guide_username
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                created_count = 0
                
                for row in reader:
                    code = row['code'].strip()
                    name = row['name'].strip()
                    domain_name = row.get('domain', '').strip()
                    guide_username = row.get('guide_username', '').strip()
                    
                    domain, _ = Domain.objects.get_or_create(name=domain_name)
                    
                    guide = None
                    if guide_username:
                        try:
                            guide = User.objects.get(username=guide_username)
                        except User.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'Guide not found: {guide_username}'))
                    
                    class_obj, created = Class.objects.get_or_create(
                        code=code,
                        defaults={
                            'name': name,
                            'domain': domain,
                            'guide': guide,
                        }
                    )
                    
                    if created:
                        created_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'Classes imported: {created_count} created'))
        
        except FileNotFoundError:
            raise CommandError(f'File not found: {filepath}')
        except Exception as e:
            raise CommandError(f'Error importing classes: {str(e)}')
