from django.core.management.base import BaseCommand
from projects.models import Phase

class Command(BaseCommand):
    help = 'Seed the database with predefined phases'
    
    def handle(self, *args, **options):
        phases = [
            {
                'name': 'SYNOPSIS',
                'order': 1,
                'description': 'Project synopsis and initial proposal',
                'deadline_offset_days': 14,
            },
            {
                'name': 'PHASE_1',
                'order': 2,
                'description': 'First development phase',
                'deadline_offset_days': 30,
            },
            {
                'name': 'PHASE_2',
                'order': 3,
                'description': 'Second development phase',
                'deadline_offset_days': 30,
            },
            {
                'name': 'FINAL_REPORT',
                'order': 4,
                'description': 'Final project report and documentation',
                'deadline_offset_days': 14,
            },
            {
                'name': 'PUBLICATION',
                'order': 5,
                'description': 'Project publication and presentation',
                'deadline_offset_days': 7,
            },
        ]
        
        for phase_data in phases:
            phase, created = Phase.objects.get_or_create(
                name=phase_data['name'],
                defaults={
                    'order': phase_data['order'],
                    'description': phase_data['description'],
                    'deadline_offset_days': phase_data['deadline_offset_days'],
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created phase: {phase.get_name_display()}'))
            else:
                self.stdout.write(self.style.WARNING(f'Phase already exists: {phase.get_name_display()}'))
        
        self.stdout.write(self.style.SUCCESS('Phase seeding completed!'))
