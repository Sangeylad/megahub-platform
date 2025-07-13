# backend/tests/utils/test_helpers.py
from rest_framework_simplejwt.tokens import RefreshToken
from brands_core.models import Brand

class JWTTestMixin:
    """Mixin pour gérer JWT dans les tests"""
    
    def setup_jwt_auth(self, user, brand=None):
        """Configure JWT auth + brand headers"""
        if not brand:
            brand = Brand.objects.filter(company=user.company).first()
        
        # Générer JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Headers complets
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Bearer {access_token}',
            'HTTP_X_BRAND_ID': str(brand.id),
        }
        
        # Pour compatibilité, on peut aussi faire les deux
        self.client.force_authenticate(user=user)  # Garde pour d'autres middlewares
        
        return self.auth_headers