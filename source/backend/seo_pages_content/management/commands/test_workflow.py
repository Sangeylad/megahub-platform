# backend/seo_pages_content/management/commands/test_workflow.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

from brands_core.models import Brand
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_workflow.models import PageStatus, PageScheduling, PageWorkflowHistory
from seo_pages_workflow.filters import PageStatusFilter, PageWorkflowHistoryFilter, PageSchedulingFilter

User = get_user_model()

class Command(BaseCommand):
    help = 'Test spécifique du workflow de publication'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📋 Testing SEO Pages Workflow Module\n'))
        
        # Setup
        self.setup_test_data()
        
        # Tests
        self.test_status_lifecycle()
        self.test_status_transitions()
        self.test_workflow_history()
        self.test_scheduling()
        self.test_workflow_filters()
        self.test_bulk_workflow()
        
        # Cleanup
        self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Workflow tests completed!'))
    
    def setup_test_data(self):
        """Setup test data"""
        self.stdout.write('📝 Setting up workflow test data...')
        
        # Get test user and brand
        self.test_user = User.objects.first()
        self.test_brand = Brand.objects.filter(seo_website__isnull=False).first()
        
        if not self.test_brand or not self.test_user:
            self.stdout.write(self.style.ERROR('❌ Missing test data'))
            return
            
        self.test_website = self.test_brand.seo_website
        
        # Create test pages with unique namespace
        self.test_namespace = f'workflow-test-{uuid.uuid4().hex[:6]}'
        self.test_pages = []
        
        for i in range(5):
            page = Page.objects.create(
                website=self.test_website,
                title=f'Workflow Test Page {i+1} {self.test_namespace}',
                url_path=f'/workflow-test-{i+1}-{self.test_namespace}',
                page_type='blog' if i % 2 == 0 else 'vitrine',
                search_intent='TOFU'
            )
            self.test_pages.append(page)
        
        self.stdout.write(f'  ✅ Created {len(self.test_pages)} test pages')
    
    def _get_or_create_status(self, page, initial_status='draft'):
        """Helper pour obtenir ou créer un status de manière sûre"""
        status, created = PageStatus.objects.get_or_create(
            page=page,
            defaults={
                'status': initial_status,
                'status_changed_by': self.test_user,
                'production_notes': f'Test status for {page.title}'
            }
        )
        if not created and status.status != initial_status:
            # Si le status existe mais n'est pas celui voulu, on le met à jour
            status.status = initial_status
            status.status_changed_by = self.test_user
            status.save()
        return status, created
    
    def test_status_lifecycle(self):
        """Test complete status lifecycle"""
        self.stdout.write('\n🔄 Testing status lifecycle...')
        
        page = self.test_pages[0]
        
        # Get or create initial status
        status, created = self._get_or_create_status(page, 'draft')
        
        if created:
            self.stdout.write(f'  ✅ Initial status created: {status.get_status_display()}')
        else:
            self.stdout.write(f'  ℹ️  Using existing status: {status.get_status_display()}')
        
        self.stdout.write(f'     - Color: {status.get_status_color()}')
        self.stdout.write(f'     - Can publish: {status.can_be_published()}')
        self.stdout.write(f'     - Is public: {status.is_publicly_accessible()}')
        
        # Complete workflow selon le vrai modèle
        workflow_steps = [
            ('in_progress', 'Started working on content'),
            ('pending_review', 'Ready for client review'),
            ('under_review', 'Internal team reviewing'),
            ('changes_requested', 'Client requested changes'),
            ('in_progress', 'Making requested changes'),
            ('pending_review', 'Changes completed'),
            ('approved', 'Client approved'),
            ('scheduled', 'Scheduled for tomorrow'),
            ('published', 'Published live')
        ]
        
        for new_status, notes in workflow_steps:
            possible = status.get_next_possible_statuses()
            
            if new_status in possible:
                old_status = status.status
                status.update_status(new_status, self.test_user, notes)
                
                # Create history
                PageWorkflowHistory.objects.create(
                    page=page,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=self.test_user,
                    notes=notes
                )
                
                self.stdout.write(f'  ✅ {old_status} → {new_status}: {notes}')
            else:
                self.stdout.write(f'  ⚠️ Cannot transition to {new_status} from {status.status}')
                self.stdout.write(f'     Possible transitions: {possible}')
    
    def test_status_transitions(self):
        """Test specific status transitions selon le vrai modèle"""
        self.stdout.write('\n🔀 Testing status transitions...')
        
        # Test cases basés sur le vrai modèle PageStatus
        test_cases = [
            ('draft', ['in_progress', 'pending_review', 'archived']),
            ('in_progress', ['pending_review', 'draft']),
            ('pending_review', ['under_review', 'approved', 'changes_requested']),
            ('under_review', ['approved', 'changes_requested', 'pending_review']),
            ('changes_requested', ['in_progress', 'pending_review']),
            ('approved', ['published', 'scheduled', 'pending_review']),
            ('scheduled', ['published', 'approved']),
            ('published', ['archived', 'deactivated', 'approved']),
            ('archived', ['draft', 'deactivated']),
            ('deactivated', ['draft', 'approved', 'archived']),
        ]
        
        for status_name, expected_next in test_cases:
            # Générer une URL unique avec uuid
            unique_suffix = uuid.uuid4().hex[:6]
            page = Page.objects.create(
                website=self.test_website,
                title=f'Transition test {status_name} {unique_suffix}',
                url_path=f'/transition-test-{status_name}-{unique_suffix}',
                page_type='blog'
            )
            
            # Utiliser le helper
            status, created = self._get_or_create_status(page, status_name)
            
            possible = status.get_next_possible_statuses()
            self.stdout.write(f'\n  Status: {status_name}')
            self.stdout.write(f'  Expected: {expected_next}')
            self.stdout.write(f'  Actual: {possible}')
            
            if set(possible) == set(expected_next):
                self.stdout.write('  ✅ Transitions correct')
            else:
                missing = set(expected_next) - set(possible)
                extra = set(possible) - set(expected_next)
                if missing:
                    self.stdout.write(f'  ❌ Missing transitions: {missing}')
                if extra:
                    self.stdout.write(f'  ❌ Extra transitions: {extra}')
    
    def test_workflow_history(self):
        """Test workflow history tracking"""
        self.stdout.write('\n📜 Testing workflow history...')
        
        page = self.test_pages[1]
        
        # Get or create status with history
        status, created = self._get_or_create_status(page, 'draft')
        
        # Quick workflow selon les vraies transitions
        workflow_path = [
            ('in_progress', 'Started development'),
            ('pending_review', 'Ready for review'),
            ('approved', 'Approved for publication'),
            ('published', 'Published live')
        ]
        
        for new_status, notes in workflow_path:
            if new_status in status.get_next_possible_statuses():
                old_status = status.status
                status.update_status(new_status, self.test_user, notes)
                
                PageWorkflowHistory.objects.create(
                    page=page,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=self.test_user,
                    notes=notes
                )
            else:
                # Si transition directe impossible, essayer un chemin alternatif
                possible = status.get_next_possible_statuses()
                if possible:
                    intermediate = possible[0]
                    old_status = status.status
                    status.update_status(intermediate, self.test_user, f'Intermediate step to reach {new_status}')
                    
                    PageWorkflowHistory.objects.create(
                        page=page,
                        old_status=old_status,
                        new_status=intermediate,
                        changed_by=self.test_user,
                        notes=f'Intermediate step to reach {new_status}'
                    )
                    
                    # Puis essayer la transition finale
                    if new_status in status.get_next_possible_statuses():
                        old_status = status.status
                        status.update_status(new_status, self.test_user, notes)
                        
                        PageWorkflowHistory.objects.create(
                            page=page,
                            old_status=old_status,
                            new_status=new_status,
                            changed_by=self.test_user,
                            notes=notes
                        )
        
        # Query history
        history = PageWorkflowHistory.objects.filter(
            page=page
        ).order_by('created_at')
        
        self.stdout.write(f'  ✅ History entries: {history.count()}')
        
        for entry in history[:5]:  # Limiter l'affichage
            duration = entry.get_duration_display()
            self.stdout.write(f'     {entry.old_status} → {entry.new_status} ({duration})')
        
        # Test progression detection
        progressions = history.filter(old_status='draft', new_status='in_progress')
        regressions = history.filter(old_status='approved', new_status='changes_requested')
        
        self.stdout.write(f'  ✅ Progressions: {progressions.count()}')
        self.stdout.write(f'  ✅ Regressions: {regressions.count()}')
    
    def test_scheduling(self):
        """Test publication scheduling"""
        self.stdout.write('\n📅 Testing scheduling...')
        
        page = self.test_pages[2]
        
        # Get or create status in approved state
        status, created = self._get_or_create_status(page, 'draft')
        
        # Transition to approved if not already
        if status.status != 'approved':
            # Faire les transitions nécessaires pour arriver à approved
            workflow_to_approved = [
                ('in_progress', 'Development started'),
                ('pending_review', 'Ready for review'),
                ('approved', 'Approved for scheduling test')
            ]
            
            for next_status, notes in workflow_to_approved:
                if next_status in status.get_next_possible_statuses():
                    status.update_status(next_status, self.test_user, notes)
                elif status.status != next_status:
                    # Si on ne peut pas y aller directement, essayer via pending_review
                    if 'pending_review' in status.get_next_possible_statuses() and next_status == 'approved':
                        status.update_status('pending_review', self.test_user, 'Via pending_review')
                        if 'approved' in status.get_next_possible_statuses():
                            status.update_status('approved', self.test_user, notes)
        
        # Schedule for future
        future_date = timezone.now() + timezone.timedelta(days=2)
        
        # get_or_create pour scheduling
        scheduling, created = PageScheduling.objects.get_or_create(
            page=page,
            defaults={
                'scheduled_publish_date': future_date,
                'auto_publish': True,
                'scheduled_by': self.test_user,
                'notes': 'Scheduled for weekend'
            }
        )
        
        if not created:
            # Mettre à jour si existe déjà
            scheduling.scheduled_publish_date = future_date
            scheduling.auto_publish = True
            scheduling.save()
        
        self.stdout.write(f'  ✅ Scheduled for: {scheduling.scheduled_publish_date}')
        self.stdout.write(f'     - Auto publish: {scheduling.auto_publish}')
        self.stdout.write(f'     - Ready now: {scheduling.is_ready_to_publish()}')
        
        # Test past scheduling
        past_page = self.test_pages[3]
        
        past_status, created = self._get_or_create_status(past_page, 'approved')
        
        past_date = timezone.now() - timezone.timedelta(hours=1)
        past_scheduling, created = PageScheduling.objects.get_or_create(
            page=past_page,
            defaults={
                'scheduled_publish_date': past_date,
                'auto_publish': True,
                'scheduled_by': self.test_user
            }
        )
        
        self.stdout.write(f'  ✅ Past scheduling ready: {past_scheduling.is_ready_to_publish()}')
        
        # Test unpublish scheduling
        unpublish_date = timezone.now() + timezone.timedelta(days=30)
        scheduling.scheduled_unpublish_date = unpublish_date
        scheduling.save()
        
        self.stdout.write(f'  ✅ Unpublish scheduled: {scheduling.scheduled_unpublish_date}')
    
    def test_workflow_filters(self):
        """Test workflow filters"""
        self.stdout.write('\n🔍 Testing workflow filters...')
        
        # Create various statuses selon le vrai modèle
        test_statuses = ['draft', 'in_progress', 'published', 'published', 'archived']
        
        for i, status_name in enumerate(test_statuses):
            if i < len(self.test_pages):
                # Ne créer que si n'existe pas déjà
                if not hasattr(self.test_pages[i], 'workflow_status'):
                    PageStatus.objects.create(
                        page=self.test_pages[i],
                        status=status_name,
                        status_changed_by=self.test_user
                    )
        
        # Test status filters
        published_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'is_published': True
        })
        
        if published_filter.is_valid():
            published_count = published_filter.qs.count()
            self.stdout.write(f'  ✅ Published pages: {published_count}')
        else:
            self.stdout.write(f'  ⚠️ Published filter invalid: {published_filter.errors}')
        
        # Test needs review filter
        review_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'needs_review': True
        })
        
        if review_filter.is_valid():
            review_count = review_filter.qs.count()
            self.stdout.write(f'  ✅ Needs review: {review_count}')
        else:
            self.stdout.write(f'  ⚠️ Review filter invalid: {review_filter.errors}')
        
        # Test can publish filter
        can_publish_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'can_publish': True
        })
        
        if can_publish_filter.is_valid():
            can_publish_count = can_publish_filter.qs.count()
            self.stdout.write(f'  ✅ Can publish: {can_publish_count}')
        else:
            self.stdout.write(f'  ⚠️ Can publish filter invalid: {can_publish_filter.errors}')
        
        # Test scheduling filters
        scheduling_filter = PageSchedulingFilter(data={
            'website': self.test_website.id,
            'auto_publish': True
        })
        
        if scheduling_filter.is_valid():
            auto_publish_count = scheduling_filter.qs.count()
            self.stdout.write(f'  ✅ Auto-publish scheduled: {auto_publish_count}')
        else:
            self.stdout.write(f'  ⚠️ Scheduling filter invalid: {scheduling_filter.errors}')
    
    def test_bulk_workflow(self):
        """Test bulk workflow operations"""
        self.stdout.write('\n📦 Testing bulk workflow...')
        
        # Créer de nouvelles pages spécifiquement pour le bulk test
        bulk_pages = []
        for i in range(3):
            page = Page.objects.create(
                website=self.test_website,
                title=f'Bulk Test Page {i+1} {self.test_namespace}',
                url_path=f'/bulk-test-{i+1}-{self.test_namespace}',
                page_type='blog'
            )
            bulk_pages.append(page)
        
        # Bulk create draft statuses
        statuses = []
        for page in bulk_pages:
            status = PageStatus(
                page=page,
                status='draft',
                status_changed_by=self.test_user,
                production_notes='Bulk created'
            )
            statuses.append(status)
        
        PageStatus.objects.bulk_create(statuses, ignore_conflicts=True)
        self.stdout.write(f'  ✅ Bulk created {len(statuses)} draft statuses')
        
        # Test bulk transition
        draft_pages = PageStatus.objects.filter(
            page__in=bulk_pages,
            status='draft'
        )
        
        updated = 0
        for status in draft_pages[:2]:
            # Vérifier que la transition est possible
            if 'in_progress' in status.get_next_possible_statuses():
                status.update_status('in_progress', self.test_user, 'Bulk update')
                updated += 1
        
        self.stdout.write(f'  ✅ Bulk transitioned {updated} pages to in_progress')
        
        # Test statistiques de statuts
        status_counts = {}
        all_statuses = PageStatus.objects.filter(page__in=bulk_pages)
        for status in all_statuses:
            status_counts[status.status] = status_counts.get(status.status, 0) + 1
        
        self.stdout.write(f'  ✅ Status distribution: {status_counts}')
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.stdout.write('\n🧹 Cleaning up test data...')
        
        # Nettoyer toutes les pages créées avec notre namespace
        deleted_count = Page.objects.filter(
            title__contains=self.test_namespace,
            website=self.test_website
        ).count()
        
        Page.objects.filter(
            title__contains=self.test_namespace,
            website=self.test_website
        ).delete()
        
        # Nettoyer aussi les pages de transition
        transition_deleted = Page.objects.filter(
            title__startswith='Transition test',
            website=self.test_website
        ).count()
        
        Page.objects.filter(
            title__startswith='Transition test',
            website=self.test_website
        ).delete()
        
        total_deleted = deleted_count + transition_deleted
        self.stdout.write(f'  ✅ Test data cleaned ({total_deleted} pages deleted)')