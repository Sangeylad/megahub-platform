# backend/seo_pages_content/management/commands/test_page_builder.py

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import uuid
import json

from brands_core.models import Brand
from seo_websites_core.models import Website
from seo_pages_content.models import Page
from seo_pages_layout.models import PageLayout, PageSection
from seo_pages_layout.filters import PageLayoutFilter, PageSectionFilter

User = get_user_model()

class Command(BaseCommand):
    help = 'Test spécifique du page builder et layouts'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Testing SEO Pages Layout/Page Builder Module\n'))
        
        # Setup
        self.setup_test_data()
        
        # Tests
        self.test_basic_layout()
        self.test_layout_containers()
        self.test_nested_sections()
        self.test_section_ordering()
        self.test_layout_filters()
        self.test_complete_page_build()
        
        # Cleanup
        self.cleanup_test_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Page Builder tests completed!'))
    
    def setup_test_data(self):
        """Setup test data"""
        self.stdout.write('📝 Setting up page builder test data...')
        
        self.test_user = User.objects.first()
        self.test_brand = Brand.objects.filter(seo_website__isnull=False).first()
        
        if not self.test_brand or not self.test_user:
            self.stdout.write(self.style.ERROR('❌ Missing test data'))
            return
            
        self.test_website = self.test_brand.seo_website
        
        # Create test page
        self.test_page = Page.objects.create(
            website=self.test_website,
            title=f'Page Builder Test {uuid.uuid4().hex[:6]}',
            page_type='landing',
            search_intent='BOFU'
        )
        
        self.stdout.write(f'  ✅ Created test page: {self.test_page.title}')
    
    def test_basic_layout(self):
        """Test basic layout creation"""
        self.stdout.write('\n📐 Testing basic layout...')
        
        # Create page layout
        layout = PageLayout.objects.create(
            page=self.test_page,
            render_strategy='sections',
            layout_data={
                'theme': 'modern',
                'version': '2.0',
                'colors': {
                    'primary': '#007bff',
                    'secondary': '#6c757d'
                }
            }
        )
        
        self.stdout.write(f'  ✅ Layout created: {layout.render_strategy}')
        self.stdout.write(f'     - Theme: {layout.layout_data.get("theme")}')
        self.stdout.write(f'     - Version: {layout.layout_data.get("version")}')
        
        # Create simple sections
        sections_data = [
            {
                'section_type': 'hero_banner',
                'data': {
                    'title': 'Welcome to Our Site',
                    'subtitle': 'Professional SEO Services',
                    'cta': {
                        'text': 'Get Started',
                        'href': '/contact'
                    }
                },
                'order': 0
            },
            {
                'section_type': 'features_grid',
                'data': {
                    'title': 'Our Services',
                    'features': [
                        {'title': 'SEO Audit', 'description': 'Complete site analysis'},
                        {'title': 'Keyword Research', 'description': 'Find best keywords'},
                        {'title': 'Content Strategy', 'description': 'Content that ranks'}
                    ]
                },
                'order': 1
            },
            {
                'section_type': 'cta_banner',
                'data': {
                    'title': 'Ready to Start?',
                    'button': {
                        'text': 'Contact Us',
                        'href': '/contact'
                    }
                },
                'order': 2
            }
        ]
        
        for section_data in sections_data:
            section = PageSection.objects.create(
                page=self.test_page,
                created_by=self.test_user,
                **section_data
            )
            self.stdout.write(f'  ✅ Section: {section.section_type} (order {section.order})')
    
    def test_layout_containers(self):
        """Test layout container sections"""
        self.stdout.write('\n📦 Testing layout containers...')
        
        # Test 2-column layout
        columns_container = PageSection.objects.create(
            page=self.test_page,
            section_type='layout_columns',
            data={},  # Data required even if empty
            layout_config={
                'columns': [8, 4],
                'gap': '2rem',
                'align': 'start'
            },
            order=3,
            created_by=self.test_user
        )
        
        self.stdout.write(f'  ✅ Columns container: {columns_container.layout_config["columns"]}')
        
        # Add children to columns
        left_content = PageSection.objects.create(
            page=self.test_page,
            parent_section=columns_container,
            section_type='rich_text',
            data={
                'content': '<h2>Main Content</h2><p>This is the main content area.</p>'
            },
            order=0,
            created_by=self.test_user
        )
        
        right_sidebar = PageSection.objects.create(
            page=self.test_page,
            parent_section=columns_container,
            section_type='cta_banner',
            data={
                'title': 'Get Free Audit',
                'button': {'text': 'Start Now', 'href': '/audit'}
            },
            order=1,
            created_by=self.test_user
        )
        
        self.stdout.write('  ✅ Column children added')
        
        # Test grid layout
        grid_container = PageSection.objects.create(
            page=self.test_page,
            section_type='layout_grid',
            data={},
            layout_config={
                'grid_template_columns': 'repeat(3, 1fr)',
                'gap': '1.5rem'
            },
            order=4,
            created_by=self.test_user
        )
        
        # Add grid items - Utiliser rich_text au lieu de testimonial_card
        for i in range(6):
            PageSection.objects.create(
                page=self.test_page,
                parent_section=grid_container,
                section_type='rich_text',  # ✅ Type valide
                data={
                    'content': f'''
                        <div class="testimonial">
                            <p>"Great service! Testimonial {i+1}"</p>
                            <cite>- Client {i+1}</cite>
                            <div class="rating">★★★★★</div>
                        </div>
                    '''
                },
                order=i,
                created_by=self.test_user
            )
        
        self.stdout.write('  ✅ Grid container with 6 items')
        
        # Test stack layout
        stack_container = PageSection.objects.create(
            page=self.test_page,
            section_type='layout_stack',
            data={},
            layout_config={
                'gap': '1rem',
                'align': 'center'
            },
            order=5,
            created_by=self.test_user
        )
        
        self.stdout.write('  ✅ Stack container created')
    
    def test_nested_sections(self):
        """Test nested section limits"""
        self.stdout.write('\n🪆 Testing nested sections...')
        
        # Create parent container
        parent = PageSection.objects.create(
            page=self.test_page,
            section_type='layout_columns',
            data={},
            layout_config={'columns': [6, 6]},
            order=6,
            created_by=self.test_user
        )
        
        # Create child
        child = PageSection.objects.create(
            page=self.test_page,
            parent_section=parent,
            section_type='hero_banner',
            data={'title': 'Nested Hero'},
            order=0,
            created_by=self.test_user
        )
        
        self.stdout.write('  ✅ Level 2 nesting allowed')
        
        # Try level 3 (should fail)
        try:
            PageSection.objects.create(
                page=self.test_page,
                parent_section=child,
                section_type='rich_text',
                data={'content': 'Too deep'},
                order=0,
                created_by=self.test_user
            )
            self.stdout.write(self.style.ERROR('  ❌ Level 3 nesting allowed!'))
        except ValidationError:
            self.stdout.write('  ✅ Level 3 nesting correctly blocked')
        
        # Test same-page validation
        other_page = Page.objects.create(
            website=self.test_website,
            title='Other page',
            url_path='/other'
        )
        
        other_section = PageSection.objects.create(
            page=other_page,
            section_type='hero_banner',
            data={'title': 'Other page hero'},
            order=0,
            created_by=self.test_user
        )
        
        try:
            PageSection.objects.create(
                page=self.test_page,
                parent_section=other_section,  # Different page!
                section_type='rich_text',
                data={'content': 'Wrong parent'},
                order=0,
                created_by=self.test_user
            )
            self.stdout.write(self.style.ERROR('  ❌ Cross-page parent allowed!'))
        except ValidationError:
            self.stdout.write('  ✅ Cross-page parent correctly blocked')
    
    def test_section_ordering(self):
        """Test section ordering"""
        self.stdout.write('\n🔢 Testing section ordering...')
        
        # Get all top-level sections
        top_sections = PageSection.objects.filter(
            page=self.test_page,
            parent_section__isnull=True
        ).order_by('order')
        
        self.stdout.write(f'  ✅ Top-level sections: {top_sections.count()}')
        
        for section in top_sections:
            children = section.child_sections.count()
            self.stdout.write(f'     {section.order}: {section.section_type} ({children} children)')
        
        # Test reordering
        if top_sections.count() >= 2:
            first_section = top_sections[0]
            second_section = top_sections[1]
            
            # Swap orders
            first_order = first_section.order
            first_section.order = second_section.order
            second_section.order = first_order
            
            first_section.save()
            second_section.save()
            
            self.stdout.write('  ✅ Sections reordered')
    
    def test_layout_filters(self):
        """Test layout filters"""
        self.stdout.write('\n🔍 Testing layout filters...')
        
        # Create more test pages with layouts
        for i in range(3):
            page = Page.objects.create(
                website=self.test_website,
                title=f'Filter test page {i}',
                url_path=f'/filter-test-{i}'
            )
            
            PageLayout.objects.create(
                page=page,
                render_strategy='sections' if i % 2 == 0 else 'custom'  # Utiliser 'custom' au lieu de 'static'
            )
            
            # Add some sections
            for j in range(2):
                PageSection.objects.create(
                    page=page,
                    section_type='hero_banner',
                    data={'title': f'Hero {j}'},
                    order=j,
                    created_by=self.test_user
                )
        
        # Test layout filters
        sections_filter = PageLayoutFilter(data={
            'website': self.test_website.id,
            'render_strategy': 'sections'
        })
        
        if sections_filter.is_valid():
            sections_count = sections_filter.qs.count()
            self.stdout.write(f'  ✅ Sections strategy layouts: {sections_count}')
        
        # Test section filters
        hero_filter = PageSectionFilter(data={
            'website': self.test_website.id,
            'section_type': 'hero_banner'
        })
        
        if hero_filter.is_valid():
            hero_count = hero_filter.qs.count()
            self.stdout.write(f'  ✅ Hero sections: {hero_count}')
        
        # Test container filter
        container_filter = PageSectionFilter(data={
            'website': self.test_website.id,
            'is_container': True
        })
        
        if container_filter.is_valid():
            container_count = container_filter.qs.count()
            self.stdout.write(f'  ✅ Container sections: {container_count}')
        
        # Test has_children filter
        parent_filter = PageSectionFilter(data={
            'website': self.test_website.id,
            'has_children': True
        })
        
        if parent_filter.is_valid():
            parent_count = parent_filter.qs.count()
            self.stdout.write(f'  ✅ Sections with children: {parent_count}')
    
    def test_complete_page_build(self):
        """Test building a complete page"""
        self.stdout.write('\n🏗️ Testing complete page build...')
        
        # Create new page for complete build
        complete_page = Page.objects.create(
            website=self.test_website,
            title='Complete Landing Page',
            page_type='landing',
            search_intent='BOFU',
            meta_description='Complete landing page test'
        )
        
        # Create layout
        layout = PageLayout.objects.create(
            page=complete_page,
            render_strategy='sections',
            layout_data={
                'theme': 'professional',
                'colors': {
                    'primary': '#0066cc',
                    'secondary': '#333333'
                }
            }
        )
        
        # Build page structure
        sections_created = []
        
        # 1. Hero section
        hero = PageSection.objects.create(
            page=complete_page,
            section_type='hero_banner',
            data={
                'title': 'Boost Your SEO Performance',
                'subtitle': 'Professional SEO services that deliver results',
                'cta': {'text': 'Get Started', 'href': '/contact'},
                'background_image': '/images/hero-bg.jpg'
            },
            order=0,
            created_by=self.test_user
        )
        sections_created.append(hero)
        
        # 2. Features in 3-column grid
        features_grid = PageSection.objects.create(
            page=complete_page,
            section_type='layout_grid',
            data={},
            layout_config={
                'grid_template_columns': 'repeat(3, 1fr)',
                'gap': '2rem'
            },
            order=1,
            created_by=self.test_user
        )
        sections_created.append(features_grid)
        
        # Add feature cards using rich_text
        features = [
            {'title': 'SEO Audit', 'icon': '🔍', 'desc': 'Complete analysis'},
            {'title': 'Keyword Research', 'icon': '🎯', 'desc': 'Find opportunities'},
            {'title': 'Content Strategy', 'icon': '📝', 'desc': 'Rank higher'}
        ]
        
        for i, feature in enumerate(features):
            card = PageSection.objects.create(
                page=complete_page,
                parent_section=features_grid,
                section_type='rich_text',  # ✅ Utiliser rich_text
                data={
                    'content': f'''
                        <div class="feature-card">
                            <div class="icon">{feature['icon']}</div>
                            <h3>{feature['title']}</h3>
                            <p>{feature['desc']}</p>
                        </div>
                    '''
                },
                order=i,
                created_by=self.test_user
            )
            sections_created.append(card)
        
        # 3. Testimonials section using rich_text
        testimonials = PageSection.objects.create(
            page=complete_page,
            section_type='rich_text',  # ✅ Utiliser rich_text
            data={
                'content': '''
                    <div class="testimonials-section">
                        <h2>What Our Clients Say</h2>
                        <div class="testimonial-grid">
                            <div class="testimonial">
                                <p>"Amazing results!"</p>
                                <cite>- John Doe</cite>
                                <div class="rating">★★★★★</div>
                            </div>
                            <div class="testimonial">
                                <p>"Best SEO service!"</p>
                                <cite>- Jane Smith</cite>
                                <div class="rating">★★★★★</div>
                            </div>
                        </div>
                    </div>
                '''
            },
            order=2,
            created_by=self.test_user
        )
        sections_created.append(testimonials)
        
        # 4. CTA section
        cta = PageSection.objects.create(
            page=complete_page,
            section_type='cta_banner',
            data={
                'title': 'Ready to Grow Your Business?',
                'subtitle': 'Get a free SEO audit today',
                'button': {'text': 'Get Free Audit', 'href': '/free-audit'}
            },
            order=3,
            created_by=self.test_user
        )
        sections_created.append(cta)
        
        self.stdout.write(f'  ✅ Complete page built with {len(sections_created)} sections')
        
        # Generate render data
        render_data = {
            'strategy': layout.render_strategy,
            'theme': layout.layout_data.get('theme'),
            'sections': []
        }
        
        # Build sections hierarchy
        top_sections = PageSection.objects.filter(
            page=complete_page,
            parent_section__isnull=True
        ).order_by('order')
        
        for section in top_sections:
            section_data = {
                'type': section.section_type,
                'data': section.data,
                'layout_config': section.layout_config,
                'children': []
            }
            
            # Add children
            for child in section.child_sections.order_by('order'):
                child_data = {
                    'type': child.section_type,
                    'data': child.data
                }
                section_data['children'].append(child_data)
            
            render_data['sections'].append(section_data)
        
        # Update layout with render data
        layout.layout_data['render_data'] = render_data
        layout.save()
        
        self.stdout.write('  ✅ Render data generated')
        self.stdout.write(f'     - Sections: {len(render_data["sections"])}')
        self.stdout.write(f'     - Theme: {render_data["theme"]}')
        
        # Display structure
        self.stdout.write('\n  📋 Page Structure:')
        for i, section in enumerate(render_data['sections']):
            self.stdout.write(f'     {i+1}. {section["type"]}')
            if section['children']:
                for j, child in enumerate(section['children']):
                    self.stdout.write(f'        - {child["type"]}')
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.stdout.write('\n🧹 Cleaning up test data...')
        
        # Delete test pages (cascade handles sections)
        Page.objects.filter(
            title__startswith='Page Builder Test',
            website=self.test_website
        ).delete()
        
        Page.objects.filter(
            title__startswith='Filter test page',
            website=self.test_website
        ).delete()
        
        Page.objects.filter(
            title='Complete Landing Page',
            website=self.test_website
        ).delete()
        
        Page.objects.filter(
            title='Other page',
            website=self.test_website
        ).delete()
        
        self.stdout.write('  ✅ Test data cleaned')