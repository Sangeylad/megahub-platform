# backend/file_converter/management/commands/init_file_formats.py

from django.core.management.base import BaseCommand
from file_converter.models import SupportedFormat

class Command(BaseCommand):
    help = 'Initialise les formats supportés'
    
    def handle(self, *args, **options):
        formats_data = [
            # Documents
            {'name': 'pdf', 'mime_type': 'application/pdf', 'category': 'document', 'is_input': True, 'is_output': True},
            {'name': 'docx', 'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'category': 'document', 'is_input': True, 'is_output': True},
            {'name': 'doc', 'mime_type': 'application/msword', 'category': 'document', 'is_input': True, 'is_output': False},
            {'name': 'odt', 'mime_type': 'application/vnd.oasis.opendocument.text', 'category': 'document', 'is_input': True, 'is_output': True},
            {'name': 'txt', 'mime_type': 'text/plain', 'category': 'document', 'is_input': True, 'is_output': True},
            {'name': 'md', 'mime_type': 'text/markdown', 'category': 'document', 'is_input': True, 'is_output': True},
            {'name': 'html', 'mime_type': 'text/html', 'category': 'document', 'is_input': True, 'is_output': True},
            {'name': 'rtf', 'mime_type': 'application/rtf', 'category': 'document', 'is_input': True, 'is_output': True},
            
            # Images
            {'name': 'jpg', 'mime_type': 'image/jpeg', 'category': 'image', 'is_input': True, 'is_output': True},
            {'name': 'jpeg', 'mime_type': 'image/jpeg', 'category': 'image', 'is_input': True, 'is_output': True},
            {'name': 'png', 'mime_type': 'image/png', 'category': 'image', 'is_input': True, 'is_output': True},
            {'name': 'gif', 'mime_type': 'image/gif', 'category': 'image', 'is_input': True, 'is_output': True},
            {'name': 'webp', 'mime_type': 'image/webp', 'category': 'image', 'is_input': True, 'is_output': True},
            {'name': 'bmp', 'mime_type': 'image/bmp', 'category': 'image', 'is_input': True, 'is_output': True},
            
            # Tableurs
            {'name': 'xlsx', 'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'category': 'spreadsheet', 'is_input': True, 'is_output': True},
            {'name': 'xls', 'mime_type': 'application/vnd.ms-excel', 'category': 'spreadsheet', 'is_input': True, 'is_output': False},
            {'name': 'csv', 'mime_type': 'text/csv', 'category': 'spreadsheet', 'is_input': True, 'is_output': True},
            {'name': 'ods', 'mime_type': 'application/vnd.oasis.opendocument.spreadsheet', 'category': 'spreadsheet', 'is_input': True, 'is_output': True},
            
            # Présentations
            {'name': 'pptx', 'mime_type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'category': 'presentation', 'is_input': True, 'is_output': True},
            {'name': 'ppt', 'mime_type': 'application/vnd.ms-powerpoint', 'category': 'presentation', 'is_input': True, 'is_output': False},
            {'name': 'odp', 'mime_type': 'application/vnd.oasis.opendocument.presentation', 'category': 'presentation', 'is_input': True, 'is_output': True},
            
            # Autres formats texte
            {'name': 'epub', 'mime_type': 'application/epub+zip', 'category': 'document', 'is_input': True, 'is_output': True},
            {'name': 'latex', 'mime_type': 'application/x-latex', 'category': 'document', 'is_input': True, 'is_output': True},
        ]
        
        created_count = 0
        updated_count = 0
        
        for format_data in formats_data:
            format_obj, created = SupportedFormat.objects.get_or_create(
                name=format_data['name'],
                defaults=format_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Créé: {format_obj}")
            else:
                # Mettre à jour si nécessaire
                updated = False
                for key, value in format_data.items():
                    if getattr(format_obj, key) != value:
                        setattr(format_obj, key, value)
                        updated = True
                
                if updated:
                    format_obj.save()
                    updated_count += 1
                    self.stdout.write(f"Mis à jour: {format_obj}")
        
        self.stdout.write(
            self.style.SUCCESS(f'{created_count} formats créés, {updated_count} mis à jour')
        )