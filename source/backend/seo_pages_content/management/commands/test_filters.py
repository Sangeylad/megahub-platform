# backend/seo_pages_content/management/commands/test_filters.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models
import uuid
from datetime import timedelta

from brands_core.models import Brand
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_hierarchy.models import PageHierarchy, PageBreadcrumb
from seo_pages_layout.models import PageLayout, PageSection
from seo_pages_seo.models import PageSEO, PagePerformance
from seo_pages_workflow.models import PageStatus, PageScheduling, PageWorkflowHistory
from seo_pages_keywords.models import PageKeyword

# Import all filters
from seo_websites_core.filters import WebsiteFilter
from seo_pages_content.filters import PageFilter
from seo_pages_hierarchy.filters import PageHierarchyFilter, PageBreadcrumbFilter
from seo_pages_layout.filters import PageLayoutFilter, PageSectionFilter
from seo_pages_seo.filters import PageSEOFilter, PagePerformanceFilter
from seo_pages_workflow.filters import PageStatusFilter, PageWorkflowHistoryFilter, PageSchedulingFilter
from seo_pages_keywords.filters import PageKeywordFilter

# Try import keywords
try:
    from seo_keywords_base.models import Keyword
    KEYWORDS_AVAILABLE = True
except ImportError:
    KEYWORDS_AVAILABLE = False

User = get_user_model()

class Command(BaseCommand):
    help = 'Test spécifique de tous les filtres SEO Pages'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Testing All SEO Pages Filters\n'))
        
        # Setup comprehensive test data
        self.setup_test_data()
        
        # Test each filter module
        self.test_website_filters()
        self.test_page_filters()
        self.test_hierarchy_filters()
        self.test_layout_filters()
        self.test_seo_filters()
        self.test_workflow_filters()
        self.test_keyword_filters()
        self.test_combined_filters()
        
        # Cleanup
        self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Filter tests completed!'))
    
    def setup_test_data(self):
        """Setup comprehensive test data for filters"""
        self.stdout.write('📝 Setting up filter test data...')
        
        self.test_user = User.objects.first()
        self.test_brand = Brand.objects.filter(seo_website__isnull=False).first()
        
        if not self.test_brand or not self.test_user:
            self.stdout.write(self.style.ERROR('❌ Missing test data'))
            return
            
        self.test_website = self.test_brand.seo_website
        
        # ✅ Namespace unique pour éviter conflits
        test_namespace = f"filter-test-{uuid.uuid4().hex[:8]}"
        
        # Create diverse pages with UNIQUE URLs
        self.test_pages = []
        page_configs = [
            {'title': f'Homepage {test_namespace}', 'page_type': 'vitrine', 'search_intent': 'TOFU', 'url_path': f'/{test_namespace}'},
            {'title': f'About Us {test_namespace}', 'page_type': 'vitrine', 'search_intent': 'TOFU', 'url_path': f'/{test_namespace}/about'},
            {'title': f'Services {test_namespace}', 'page_type': 'vitrine', 'search_intent': 'MOFU', 'url_path': f'/{test_namespace}/services'},
            {'title': f'Blog Post 1 {test_namespace}', 'page_type': 'blog', 'search_intent': 'TOFU', 'meta_description': 'First blog post', 'url_path': f'/{test_namespace}/blog/post-1'},
            {'title': f'Blog Post 2 {test_namespace}', 'page_type': 'blog', 'search_intent': 'MOFU', 'meta_description': 'Second blog post', 'url_path': f'/{test_namespace}/blog/post-2'},
            {'title': f'Product Page {test_namespace}', 'page_type': 'produit', 'search_intent': 'BOFU', 'meta_description': 'Buy our product', 'url_path': f'/{test_namespace}/product'},
            {'title': f'Landing Page {test_namespace}', 'page_type': 'landing', 'search_intent': 'BOFU', 'url_path': f'/{test_namespace}/landing'},
            {'title': f'Contact {test_namespace}', 'page_type': 'vitrine', 'search_intent': 'BOFU', 'url_path': f'/{test_namespace}/contact'},
        ]
        
        for config in page_configs:
            page = Page.objects.create(
                website=self.test_website,
                **config
            )
            self.test_pages.append(page)
    
    
    def _setup_hierarchies(self):
        """Setup page hierarchies"""
        # Homepage as root
        homepage = self.test_pages[0]
        PageHierarchy.objects.create(page=homepage, parent=None)
        
        # Level 2 pages
        for page in [self.test_pages[1], self.test_pages[2], self.test_pages[7]]:  # About, Services, Contact
            PageHierarchy.objects.create(page=page, parent=homepage)
        
        # Level 3 page
        PageHierarchy.objects.create(page=self.test_pages[5], parent=self.test_pages[2])  # Product under Services
        
        # Create breadcrumbs
        for page in self.test_pages:
            if hasattr(page, 'hierarchy'):
                breadcrumb, _ = PageBreadcrumb.objects.get_or_create(page=page)
                breadcrumb.regenerate_breadcrumb()
    
    def _setup_layouts(self):
        """Setup layouts and sections"""
        for i, page in enumerate(self.test_pages):
            # Create layout
            layout = PageLayout.objects.create(
                page=page,
                render_strategy='sections' if i % 2 == 0 else 'static'
            )
            
            # Add sections
            if layout.render_strategy == 'sections':
                # Add hero section
                PageSection.objects.create(
                    page=page,
                    section_type='hero_banner',
                    data={'title': f'Hero for {page.title}'},
                    order=0,
                    created_by=self.test_user
                )
                
                # Add container with children for some
                if i % 3 == 0:
                    container = PageSection.objects.create(
                        page=page,
                        section_type='layout_columns',
                        data={},
                        layout_config={'columns': [8, 4]},
                        order=1,
                        created_by=self.test_user
                    )
                    
                    # Add children
                    PageSection.objects.create(
                        page=page,
                        parent_section=container,
                        section_type='rich_text',
                        data={'content': 'Main content'},
                        order=0,
                        created_by=self.test_user
                    )
    
    def _setup_seo(self):
        """Setup SEO configurations"""
        priorities = [1.0, 0.8, 0.8, 0.5, 0.5, 0.6, 0.7, 0.9]
        
        for i, page in enumerate(self.test_pages):
            # SEO config
            seo = PageSEO.objects.create(
                page=page,
                sitemap_priority=priorities[i],
                sitemap_changefreq='daily' if i < 3 else 'weekly',
                exclude_from_sitemap=(i == 7),  # Exclude contact
                featured_image=f'https://example.com/og-{i}.jpg' if i % 2 == 0 else None
            )
            
            # Performance
            perf = PagePerformance.objects.create(
                page=page,
                last_rendered_at=timezone.now() - timedelta(hours=i*2) if i < 5 else None,
                render_time_ms=100 + i*50,
                cache_hits=i*10
            )
    
    def _setup_workflow(self):
        """Setup workflow statuses"""
        statuses = ['published', 'published', 'published', 'draft', 'in_progress', 'approved', 'scheduled', 'archived']
        
        for i, page in enumerate(self.test_pages):
            status = PageStatus.objects.create(
                page=page,
                status=statuses[i],
                status_changed_by=self.test_user,
                status_changed_at=timezone.now() - timedelta(days=i)
            )
            
            # Add history for some
            if i < 4:
                PageWorkflowHistory.objects.create(
                    page=page,
                    old_status='draft',
                    new_status=statuses[i],
                    changed_by=self.test_user,
                    created_at=timezone.now() - timedelta(days=i+1)
                )
            
            # Add scheduling for approved/scheduled
            if statuses[i] in ['approved', 'scheduled']:
                PageScheduling.objects.create(
                    page=page,
                    scheduled_publish_date=timezone.now() + timedelta(days=i),
                    auto_publish=True,
                    scheduled_by=self.test_user
                )
    
    def _setup_keywords(self):
        """Setup keyword associations"""
        # Create test keywords
        keywords = []
        for i in range(5):
            kw, _ = Keyword.objects.get_or_create(
                keyword=f'filter test keyword {i}',
                defaults={
                    'volume': 100 * (i + 1),
                    'search_intent': ['TOFU', 'MOFU', 'BOFU'][i % 3]
                }
            )
            keywords.append(kw)
        
        # Assign to pages
        for i, page in enumerate(self.test_pages[:5]):
            if i < len(keywords):
                PageKeyword.objects.create(
                    page=page,
                    keyword=keywords[i],
                    keyword_type='primary' if i == 0 else 'secondary',
                    position=1,
                    is_ai_selected=(i % 2 == 0)
                )
    
    def test_website_filters(self):
        """Test website filters"""
        self.stdout.write('\n🌐 Testing Website Filters...')
        
        # Brand filter
        brand_filter = WebsiteFilter(data={'brand': self.test_brand.id})
        self._test_filter(brand_filter, 'Brand filter')
        
        # Search filter
        search_filter = WebsiteFilter(data={'search': self.test_website.name[:5]})
        self._test_filter(search_filter, 'Search filter')
        
        # DA filter
        da_filter = WebsiteFilter(data={'domain_authority__gte': 0})
        self._test_filter(da_filter, 'Domain Authority filter')
    
    def test_page_filters(self):
        """Test page content filters"""
        self.stdout.write('\n📄 Testing Page Filters...')
        
        # Page type filter
        blog_filter = PageFilter(data={
            'website': self.test_website.id,
            'page_type': 'blog'
        })
        self._test_filter(blog_filter, 'Blog pages')
        
        # Search intent filter
        tofu_filter = PageFilter(data={
            'website': self.test_website.id,
            'search_intent': 'TOFU'
        })
        self._test_filter(tofu_filter, 'TOFU pages')
        
        # Has meta description
        meta_filter = PageFilter(data={
            'website': self.test_website.id,
            'has_meta_description': True
        })
        self._test_filter(meta_filter, 'Pages with meta description')
        
        # Combined filters
        combined_filter = PageFilter(data={
            'website': self.test_website.id,
            'page_type': 'vitrine',
            'search_intent': 'TOFU',
            'search': 'Home'
        })
        self._test_filter(combined_filter, 'Combined page filters')
    
    def test_hierarchy_filters(self):
        """Test hierarchy filters"""
        self.stdout.write('\n🌳 Testing Hierarchy Filters...')
        
        # Level filters
        for level in [1, 2, 3]:
            level_filter = PageHierarchyFilter(data={
                'website': self.test_website.id,
                'level': level
            })
            self._test_filter(level_filter, f'Level {level} pages')
        
        # Root pages
        root_filter = PageHierarchyFilter(data={
            'website': self.test_website.id,
            'is_root': True
        })
        self._test_filter(root_filter, 'Root pages')
        
        # Has children
        parent_filter = PageHierarchyFilter(data={
            'website': self.test_website.id,
            'has_children': True
        })
        self._test_filter(parent_filter, 'Pages with children')
        
        # Breadcrumb filters
        breadcrumb_filter = PageBreadcrumbFilter(data={
            'website': self.test_website.id,
            'has_breadcrumb': True
        })
        self._test_filter(breadcrumb_filter, 'Pages with breadcrumb')
    
    def test_layout_filters(self):
        """Test layout and section filters"""
        self.stdout.write('\n🎨 Testing Layout Filters...')
        
        # Render strategy
        sections_filter = PageLayoutFilter(data={
            'website': self.test_website.id,
            'render_strategy': 'sections'
        })
        self._test_filter(sections_filter, 'Sections strategy')
        
        # Section type
        hero_filter = PageSectionFilter(data={
            'website': self.test_website.id,
            'section_type': 'hero_banner'
        })
        self._test_filter(hero_filter, 'Hero sections')
        
        # Container sections
        container_filter = PageSectionFilter(data={
            'website': self.test_website.id,
            'is_container': True
        })
        self._test_filter(container_filter, 'Container sections')
        
        # Has children
        parent_sections_filter = PageSectionFilter(data={
            'website': self.test_website.id,
            'has_children': True
        })
        self._test_filter(parent_sections_filter, 'Sections with children')
        
        # Created by user
        user_sections_filter = PageSectionFilter(data={
            'website': self.test_website.id,
            'created_by': self.test_user.id
        })
        self._test_filter(user_sections_filter, 'Sections by user')
    
    def test_seo_filters(self):
        """Test SEO filters"""
        self.stdout.write('\n🔍 Testing SEO Filters...')
        
        # High priority
        priority_filter = PageSEOFilter(data={
            'website': self.test_website.id,
            'sitemap_priority_high': True
        })
        self._test_filter(priority_filter, 'High priority pages')
        
        # Has featured image
        image_filter = PageSEOFilter(data={
            'website': self.test_website.id,
            'has_featured_image': True
        })
        self._test_filter(image_filter, 'Pages with featured image')
        
        # Exclude from sitemap
        exclude_filter = PageSEOFilter(data={
            'website': self.test_website.id,
            'exclude_from_sitemap': True
        })
        self._test_filter(exclude_filter, 'Excluded from sitemap')
        
        # Performance filters
        slow_filter = PagePerformanceFilter(data={
            'website': self.test_website.id,
            'render_time_slow': True
        })
        self._test_filter(slow_filter, 'Slow rendering pages')
        
        # Never rendered
        never_rendered_filter = PagePerformanceFilter(data={
            'website': self.test_website.id,
            'never_rendered': True
        })
        self._test_filter(never_rendered_filter, 'Never rendered pages')
    
    def test_workflow_filters(self):
        """Test workflow filters"""
        self.stdout.write('\n⚡ Testing Workflow Filters...')
        
        # Published pages
        published_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'is_published': True
        })
        self._test_filter(published_filter, 'Published pages')
        
        # Needs review
        review_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'needs_review': True
        })
        self._test_filter(review_filter, 'Needs review')
        
        # Can publish
        can_publish_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'can_publish': True
        })
        self._test_filter(can_publish_filter, 'Can be published')
        
        # Status changed recently
        recent_change_filter = PageStatusFilter(data={
            'website': self.test_website.id,
            'status_changed_after': (timezone.now() - timedelta(days=7)).isoformat()
        })
        self._test_filter(recent_change_filter, 'Recently changed status')
        
        # History filters
        progression_filter = PageWorkflowHistoryFilter(data={
            'website': self.test_website.id,
            'status_progression': True
        })
        self._test_filter(progression_filter, 'Status progressions')
        
        # Scheduling filters
        auto_publish_filter = PageSchedulingFilter(data={
            'website': self.test_website.id,
            'auto_publish': True
        })
        self._test_filter(auto_publish_filter, 'Auto-publish scheduled')
        
        # Ready to publish
        ready_filter = PageSchedulingFilter(data={
            'website': self.test_website.id,
            'ready_to_publish': True
        })
        self._test_filter(ready_filter, 'Ready to publish')
    
    def test_keyword_filters(self):
        """Test keyword filters"""
        self.stdout.write('\n🔑 Testing Keyword Filters...')
        
        if not KEYWORDS_AVAILABLE:
            self.stdout.write('  ⚠️ Keywords module not available')
            return
        
        # Keyword type
        primary_filter = PageKeywordFilter(data={
            'website': self.test_website.id,
            'keyword_type': 'primary'
        })
        self._test_filter(primary_filter, 'Primary keywords')
        
        # AI selected
        ai_filter = PageKeywordFilter(data={
            'website': self.test_website.id,
            'is_ai_selected': True
        })
        self._test_filter(ai_filter, 'AI selected keywords')
        
        # High volume
        volume_filter = PageKeywordFilter(data={
            'website': self.test_website.id,
            'high_volume': True
        })
        self._test_filter(volume_filter, 'High volume keywords')
        
        # Search
        search_kw_filter = PageKeywordFilter(data={
            'website': self.test_website.id,
            'search': 'filter test'
        })
        self._test_filter(search_kw_filter, 'Keyword search')
    
    def test_combined_filters(self):
        """Test complex filter combinations"""
        self.stdout.write('\n🔗 Testing Combined Filters...')
        
        # Published blog posts with high priority
        complex_filter_1 = PageFilter(
            data={
                'website': self.test_website.id,
                'page_type': 'blog'
            }
        ).qs.filter(
            workflow_status__status='published',
            seo_config__sitemap_priority__gte=0.5
        )
        
        self.stdout.write(f'  ✅ Published blogs with high priority: {complex_filter_1.count()}')
        
        # Pages with sections and good performance
        complex_filter_2 = Page.objects.filter(
            website=self.test_website,
            layout_config__render_strategy='sections',
            performance__render_time_ms__lt=300,
            performance__last_rendered_at__isnull=False
        ).distinct()
        
        self.stdout.write(f'  ✅ Pages with sections and good performance: {complex_filter_2.count()}')
        
        # Root pages that are published
        if hasattr(PageHierarchy.objects.first(), 'page'):
            complex_filter_3 = PageHierarchy.objects.filter(
                page__website=self.test_website,
                parent__isnull=True,
                page__workflow_status__status='published'
            )
            
            self.stdout.write(f'  ✅ Published root pages: {complex_filter_3.count()}')
        
        # Pages with keywords and scheduled
        if KEYWORDS_AVAILABLE:
            complex_filter_4 = Page.objects.filter(
                website=self.test_website,
                page_keywords__isnull=False,
                scheduling__auto_publish=True
            ).distinct()
            
            self.stdout.write(f'  ✅ Pages with keywords and scheduling: {complex_filter_4.count()}')
        
        # Performance analysis with annotations
        performance_analysis = Page.objects.filter(
            website=self.test_website
        ).annotate(
            sections_count=models.Count('sections'),
            keywords_count=models.Count('page_keywords'),
            has_seo=models.Case(
                models.When(seo_config__isnull=False, then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField()
            ),
            avg_render_time=models.Avg('performance__render_time_ms')
        ).filter(
            sections_count__gt=0
        )
        
        self.stdout.write(f'  ✅ Pages with performance analysis: {performance_analysis.count()}')
        
        # Display sample analysis
        for page in performance_analysis[:3]:
            self.stdout.write(f'     - {page.title}:')
            self.stdout.write(f'       Sections: {page.sections_count}, Keywords: {page.keywords_count}')
            self.stdout.write(f'       Has SEO: {page.has_seo}, Avg render: {page.avg_render_time}ms')
    
    def _test_filter(self, filter_obj, name):
        """Helper to test a filter"""
        if filter_obj.is_valid():
            count = filter_obj.qs.count()
            self.stdout.write(f'  ✅ {name}: {count} results')
            
            # Show first result details if any
            if count > 0 and hasattr(filter_obj.qs.first(), 'title'):
                first = filter_obj.qs.first()
                self.stdout.write(f'     Example: {first.title}')
        else:
            self.stdout.write(f'  ❌ {name}: Invalid filter')
            self.stdout.write(f'     Errors: {filter_obj.errors}')
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.stdout.write('\n🧹 Cleaning up filter test data...')
        
        # Delete test pages
        for page in self.test_pages:
            page.delete()
        
        # Clean test keywords if created
        if KEYWORDS_AVAILABLE:
            Keyword.objects.filter(
                keyword__startswith='filter test keyword'
            ).delete()
        
        self.stdout.write('  ✅ Test data cleaned')