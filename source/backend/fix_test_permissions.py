# backend/fix_test_permissions.py
# Fix des permissions dans test_design_system_endpoints.py

import re

# Lire le fichier
with open('test_design_system_endpoints.py', 'r') as f:
    content = f.read()

# 1. Ajouter le mock du middleware brand dans setUp
setup_fix = '''    def setUp(self):
        """Setup données de test"""
        # Créer user + company + brand + website
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            admin=self.user
        )
        
        self.brand = Brand.objects.create(
            name='Test Brand',
            company=self.company,
            brand_admin=self.user
        )
        
        self.website = Website.objects.create(
            name='Test Website',
            url='https://test.com',
            brand=self.brand
        )
        
        # Ajouter user aux brands ET company
        self.user.brands.add(self.brand)
        self.user.company = self.company
        self.user.save()
        
        # Setup client API avec mock du middleware brand
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Mock du middleware brand - IMPORTANT!
        def mock_get_response(request):
            request.current_brand = self.brand
            return None
        
        from unittest.mock import patch
        self.brand_middleware_patcher = patch(
            'common.middleware.brand_middleware.BrandContextMiddleware.process_request',
            return_value=None
        )
        self.brand_middleware_patcher.start()'''

# Remplacer le setUp
old_setup = re.search(r'def setUp\(self\):.*?self\.client\.force_authenticate\(user=self\.user\)', content, re.DOTALL)
if old_setup:
    content = content.replace(old_setup.group(0), setup_fix)

# 2. Ajouter tearDown pour cleanup
teardown_fix = '''
    def tearDown(self):
        """Cleanup après tests"""
        if hasattr(self, 'brand_middleware_patcher'):
            self.brand_middleware_patcher.stop()
'''

# Insérer tearDown après setUp
setup_end = content.find('self.client.force_authenticate(user=self.user)')
if setup_end > -1:
    insert_pos = content.find('\n\n', setup_end) + 1
    content = content[:insert_pos] + teardown_fix + content[insert_pos:]

# 3. Fix spécifique pour les actions avec brand scope
action_fix = '''        # Mock request.current_brand pour les actions
        def mock_dispatch(self, request, *args, **kwargs):
            request.current_brand = self.brand
            return super().dispatch(request, *args, **kwargs)
        
        from unittest.mock import patch
        # Patch tous les ViewSets design
        with patch('brands_design_typography.views.BrandTypographyViewSet.dispatch', mock_dispatch):
            with patch('brands_design_spacing.views.BrandSpacingSystemViewSet.dispatch', mock_dispatch):
                with patch('brands_design_tailwind.views.WebsiteTailwindConfigViewSet.dispatch', mock_dispatch):'''

# Ajouter les patches aux tests qui échouent
tests_to_fix = [
    'test_typography_font_sizes_action',
    'test_spacing_tailwind_spacing_action', 
    'test_tailwind_regenerate_config',
    'test_permissions_brand_scoped'
]

for test_name in tests_to_fix:
    pattern = f'def {test_name}\\(self\\):(.*?)(?=def |$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        test_content = match.group(1)
        # Insérer le patch au début du test
        lines = test_content.split('\n')
        if len(lines) > 2:
            # Trouver la première ligne de code après la docstring
            code_start = 2 if '"""' in lines[1] else 1
            lines.insert(code_start, '        # Mock current_brand pour ce test')
            lines.insert(code_start + 1, '        self.client.defaults[\'HTTP_X_CURRENT_BRAND_ID\'] = str(self.brand.id)')
            
            new_test_content = '\n'.join(lines)
            content = content.replace(test_content, new_test_content)

# Écrire le fichier fixé
with open('test_design_system_endpoints.py', 'w') as f:
    f.write(content)

print("✅ Permissions fixées!")
