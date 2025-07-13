# backend/blog_content/management/commands/create_blog_authors.py

from django.core.management.base import BaseCommand
from users_core.models import CustomUser
from blog_content.models import BlogAuthor

class Command(BaseCommand):
    help = 'Crée un BlogAuthor pour chaque CustomUser qui n\'en a pas'

    def handle(self, *args, **options):
        users_without_author = CustomUser.objects.filter(
            blog_author__isnull=True
        ).exclude(username='AnonymousUser')
        
        created_count = 0
        
        for user in users_without_author:
            display_name = user.get_full_name() or user.username
            
            BlogAuthor.objects.create(
                user=user,
                display_name=display_name,
                bio=f"Membre de l'équipe {user.company.name if user.company else 'MEGAHUB'}",
                expertise_topics=[]
            )
            created_count += 1
            self.stdout.write(f"Créé auteur pour : {display_name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Terminé ! {created_count} auteurs créés.')
        )