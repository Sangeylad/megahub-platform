# backend/auth_core/tests/test_auth_endpoints.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from auth_core.tests.factories import UserFactory

class AuthEndpointsTest(APITestCase):
    """Tests des endpoints d'authentification"""
    
    def setUp(self):
        self.user = UserFactory(username='testuser', email='test@example.com')
        self.user.set_password('testpass123')
        self.user.save()
    
    def test_login_success(self):
        """Test connexion réussie"""
        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_with_email(self):
        """Test connexion avec email"""
        url = reverse('auth-login')
        data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_login_invalid_credentials(self):
        """Test connexion avec identifiants invalides"""
        url = reverse('auth-login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_me_endpoint_authenticated(self):
        """Test endpoint profil avec utilisateur connecté"""
        self.client.force_authenticate(user=self.user)
        url = reverse('auth-me')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_me_endpoint_unauthenticated(self):
        """Test endpoint profil sans authentification"""
        url = reverse('auth-me')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_password_success(self):
        """Test changement de mot de passe réussi"""
        self.client.force_authenticate(user=self.user)
        url = reverse('auth-change-password')
        data = {
            'current_password': 'testpass123',
            'new_password': 'newtestpass456',
            'new_password_confirm': 'newtestpass456'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le mot de passe a changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newtestpass456'))
    
    def test_logout_success(self):
        """Test déconnexion réussie"""
        self.client.force_authenticate(user=self.user)
        url = reverse('auth-logout')
        
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
