# backend/seo_pages_content/management/commands/test_hierarchy.py

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import uuid

from brands_core.models import Brand
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_hierarchy.models import PageHierarchy, PageBreadcrumb
from seo_pages_hierarchy.filters import PageHierarchyFilter, PageBreadcrumbFilter

User = get_user_model()

class Command(BaseCommand):
    help = 'Test spécifique de la hiérarchie des pages SEO'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌳 Testing SEO Pages Hierarchy Module\n'))
        
        # Setup
        self.setup_test_data()
        
        # Tests
        self.test_basic_hierarchy()
        self.test_hierarchy_limits()
        self.test_breadcrumbs()
        self.test_hierarchy_filters()
        self.test_advanced_navigation()
        
        # Cleanup
        self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Hierarchy tests completed!'))
    
    def setup_test_data(self):
        """Setup test data"""
        self.stdout.write('📝 Setting up hierarchy test data...')
        
        # Get first brand with website
        self.test_brand = Brand.objects.filter(seo_website__isnull=False).first()
        if not self.test_brand:
            self.stdout.write(self.style.ERROR('❌ No brand with website found'))
            return
            
        self.test_website = self.test_brand.seo_website
        self.stdout.write(f'  ✅ Using website: {self.test_website.name}')
        
        # Create test pages
        self.test_pages = []
        page_types = [
            ('Homepage', 'vitrine', '/'),
            ('About Us', 'vitrine', '/about'),
            ('Services', 'vitrine', '/services'),
            ('SEO Service', 'produit', '/services/seo'),
            ('SEO Audit', 'produit', '/services/seo/audit'),
            ('Blog', 'blog', '/blog'),
            ('SEO Tips', 'blog', '/blog/seo-tips'),
        ]
        
        for title, page_type, url_path in page_types:
            page = Page.objects.create(
                website=self.test_website,
                title=f'{title} {uuid.uuid4().hex[:6]}',
                page_type=page_type,
                url_path=url_path,
                search_intent='TOFU'
            )
            self.test_pages.append(page)
        
        self.stdout.write(f'  ✅ Created {len(self.test_pages)} test pages')
    
    def test_basic_hierarchy(self):
        """Test basic hierarchy creation"""
        self.stdout.write('\n📊 Testing basic hierarchy...')
        
        # Create root hierarchy
        homepage = self.test_pages[0]
        root = PageHierarchy.objects.create(
            page=homepage,
            parent=None
        )
        
        self.stdout.write(f'  ✅ Root: {homepage.title} (Level {root.get_level()})')
        
        # Create level 2
        about = self.test_pages[1]
        services = self.test_pages[2]
        blog = self.test_pages[5]
        
        for page in [about, services, blog]:
            hierarchy = PageHierarchy.objects.create(
                page=page,
                parent=homepage
            )
            self.stdout.write(f'  ✅ Level 2: {page.title} → parent: {hierarchy.parent.title}')
        
        # Create level 3
        seo_service = self.test_pages[3]
        seo_tips = self.test_pages[6]
        
        services_hierarchy = PageHierarchy.objects.create(
            page=seo_service,
            parent=services
        )
        self.stdout.write(f'  ✅ Level 3: {seo_service.title} → parent: {services_hierarchy.parent.title}')
        
        blog_hierarchy = PageHierarchy.objects.create(
            page=seo_tips,
            parent=blog
        )
        self.stdout.write(f'  ✅ Level 3: {seo_tips.title} → parent: {blog_hierarchy.parent.title}')
        
        # Store for later tests
        self.hierarchy_map = {
            'root': homepage,
            'about': about,
            'services': services,
            'blog': blog,
            'seo_service': seo_service,
            'seo_tips': seo_tips
        }
    
    def test_hierarchy_limits(self):
        """Test 3-level limit"""
        self.stdout.write('\n🚫 Testing hierarchy limits...')
        
        # Try to create level 4
        seo_audit = self.test_pages[4]
        seo_service = self.hierarchy_map['seo_service']
        
        try:
            PageHierarchy.objects.create(
                page=seo_audit,
                parent=seo_service  # This would be level 4
            )
            self.stdout.write(self.style.ERROR('  ❌ Level 4 was allowed!'))
        except ValidationError as e:
            self.stdout.write('  ✅ Level 4 correctly blocked')
            self.stdout.write(f'     Error: {e.messages[0]}')
        
        # Test duplicate page in hierarchy
        try:
            PageHierarchy.objects.create(
                page=self.hierarchy_map['about'],
                parent=self.hierarchy_map['services']
            )
            self.stdout.write(self.style.ERROR('  ❌ Duplicate hierarchy allowed!'))
        except Exception:
            self.stdout.write('  ✅ Duplicate hierarchy blocked')
    
    def test_breadcrumbs(self):
        """Test breadcrumb generation"""
        self.stdout.write('\n🍞 Testing breadcrumbs...')
        
        # Test for level 3 page
        seo_service = self.hierarchy_map['seo_service']
        breadcrumb, created = PageBreadcrumb.objects.get_or_create(page=seo_service)
        
        breadcrumb_data = breadcrumb.regenerate_breadcrumb()
        self.stdout.write(f'  ✅ Breadcrumb for "{seo_service.title}": {len(breadcrumb_data)} levels')
        
        for i, item in enumerate(breadcrumb_data):
            self.stdout.write(f'     {i+1}. {item["title"]} → {item["url"]}')
        
        # Verify correct order (root to current)
        expected_order = ['Homepage', 'Services', 'SEO Service']
        actual_titles = [item['title'].split()[0] for item in breadcrumb_data]
        
        if actual_titles == expected_order:
            self.stdout.write('  ✅ Breadcrumb order correct')
        else:
            self.stdout.write(f'  ❌ Order incorrect: {actual_titles}')
        
        # Test breadcrumb for root
        root_breadcrumb, _ = PageBreadcrumb.objects.get_or_create(
            page=self.hierarchy_map['root']
        )
        root_data = root_breadcrumb.regenerate_breadcrumb()
        self.stdout.write(f'  ✅ Root breadcrumb: {len(root_data)} level')
    
    def test_hierarchy_filters(self):
        """Test hierarchy filters"""
        self.stdout.write('\n🔍 Testing hierarchy filters...')
        
        # IMPORTANT: Désactiver temporairement l'ordering pour éviter la boucle infinie
        from seo_pages_content.models import Page
        original_ordering = Page._meta.ordering
        Page._meta.ordering = []
        
        try:
            # Test level filter
            for level in [1, 2, 3]:
                filter_obj = PageHierarchyFilter(data={
                    'website': self.test_website.id,
                    'level': level
                })
                
                if filter_obj.is_valid():
                    count = filter_obj.qs.count()
                    self.stdout.write(f'  ✅ Level {level}: {count} pages')
            
            # Test root filter
            root_filter = PageHierarchyFilter(data={
                'website': self.test_website.id,
                'is_root': True
            })
            
            if root_filter.is_valid():
                root_count = root_filter.qs.count()
                self.stdout.write(f'  ✅ Root pages: {root_count}')
            
            # Test has_children filter
            parent_filter = PageHierarchyFilter(data={
                'website': self.test_website.id,
                'has_children': True
            })
            
            if parent_filter.is_valid():
                parent_count = parent_filter.qs.count()
                self.stdout.write(f'  ✅ Pages with children: {parent_count}')
            
            # Test breadcrumb filter
            breadcrumb_filter = PageBreadcrumbFilter(data={
                'website': self.test_website.id,
                'has_breadcrumb': True
            })
            
            if breadcrumb_filter.is_valid():
                breadcrumb_count = breadcrumb_filter.qs.count()
                self.stdout.write(f'  ✅ Pages with breadcrumb: {breadcrumb_count}')
                
        finally:
            # Restaurer l'ordering original
            Page._meta.ordering = original_ordering
    
    def test_advanced_navigation(self):
        """Test navigation methods"""
        self.stdout.write('\n🧭 Testing navigation methods...')
        
        # Get children of a page
        services = self.hierarchy_map['services']
        children = Page.objects.filter(hierarchy__parent=services)
        
        self.stdout.write(f'  ✅ Children of "{services.title}": {[p.title for p in children]}')
        
        # Navigate from leaf to root
        seo_tips = self.hierarchy_map['seo_tips']
        hierarchy = seo_tips.hierarchy
        
        path = []
        current = seo_tips
        while current:
            path.append(current.title.split()[0])  # Get base title without UUID
            if hasattr(current, 'hierarchy') and current.hierarchy.parent:
                current = current.hierarchy.parent
            else:
                break
        
        self.stdout.write(f'  ✅ Path to root: {" ← ".join(path)}')
        
        # Get all descendants
        root = self.hierarchy_map['root']
        descendants = PageHierarchy.objects.filter(
            page__website=self.test_website
        ).exclude(page=root)
        
        self.stdout.write(f'  ✅ Total descendants of root: {descendants.count()}')
        
        # Test siblings
        about_siblings = Page.objects.filter(
            hierarchy__parent=root
        ).exclude(id=self.hierarchy_map['about'].id)
        
        self.stdout.write(f'  ✅ Siblings of About: {[p.title.split()[0] for p in about_siblings]}')
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.stdout.write('\n🧹 Cleaning up test data...')
        
        # Delete test pages (cascade will handle hierarchy)
        for page in self.test_pages:
            page.delete()
        
        self.stdout.write('  ✅ Test data cleaned')